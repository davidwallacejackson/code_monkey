'''Code to generate new changes to the source of a Node. Every change is a
single Change object.

Nothing in this module actually overwrites files: that occurs in edit, where
Changes are grouped into ChangeSets. ChangeSets check that individual changes
do not conflict, provide previews, and commit changes to disk.
'''
import difflib

from code_monkey.format import format_source
from code_monkey.utils import line_column_to_absolute_index

class Change(object):
    '''A single change to make to a single file. Replaces the file content
    from indices start through (end-1) with new_text.'''
    def __init__(self, path, start, end, new_text):
        self.path = path
        self.start = start
        self.end = end
        self.new_text = new_text

    def __unicode__(self):
        with open(self.path) as source_file:
            source = source_file.read()

        new_source = (
            source[:self.start] + self.new_text + source[self.end:])

        #difflib works on lists of line strings, so we convert the source and
        #its replacement to lists.
        source_lines = source.splitlines(True)
        new_lines = new_source.splitlines(True)

        diff = difflib.unified_diff(
            source_lines,
            new_lines,
            fromfile=self.path,
            tofile=self.path)

        output = ''

        #diff is a generator that returns lines, so we collect it into a string
        for line in diff:
            output += line

        return output

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return self.__unicode__()

class ChangeGenerator(object):
    '''Generates change tuples for a specific node. Every node with a source
    file should have one, as its .change property.

    So, a typical use might be: change = node.change.overwrite("newtext")'''

    def __init__(self, node):
        self.node = node

    def overwrite(self, new_source):
        '''Generate a change that overwrites the contents of the Node entirely
        with new_source'''

        #find the actual index in the source at which the node begins:
        file_source = self.node.get_file_source_code()

        return Change(
            self.node.fs_path,
            self.node.start_index,
            self.node.end_index,
            new_source)

    def overwrite_body(self, new_source):
        '''Generate a change that overwrites the body of the node with
        new_source. In the case of a ModuleNode, this is equivalent to
        overwrite().'''

        #find the actual index in the source at which the node begins:
        file_source = self.node.get_file_source_code()

        return Change(
            self.node.fs_path,
            self.node.body_start_index,
            self.node.body_end_index,
            new_source)


    def inject_at_index(self, index, inject_source):
        '''Generate a change that inserts inject_source into the node, starting
        at index. index is relative to the beginning of the node, not the
        beginning of the file.'''

        #find the actual index in the source at which the node begins:
        inject_index = self.node.start_index + index

        return Change(
            self.node.fs_path,
            inject_index,
            inject_index,
            inject_source)

    def inject_at_body_index(self, index, inject_source):
        '''Generate a change that inserts inject_source into the node, starting
        at index. index is relative to the beginning of the node body, not the
        beginning of the file.'''

        #find the actual index in the source at which the node begins:
        inject_index = self.node.body_start_index + index

        return Change(
            self.node.fs_path,
            inject_index,
            inject_index,
            inject_source)

    def inject_at_line(self, line_index, inject_source):
        '''As inject_at_index, but takes a line index instead of a character
        index.'''

        character_index_of_line = line_column_to_absolute_index(
            self.node.get_source(),
            line_index,
            0)

        return self.inject_at_index(character_index_of_line, inject_source)

    def inject_at_body_index(self, line_index, inject_source):
        '''As inject_at_index, but takes a line index instead of a character
        index.'''

        character_index_of_line = line_column_to_absolute_index(
            self.node.get_body_source(),
            line_index,
            0)

        return self.inject_at_body_index(
            character_index_of_line, inject_source)


class VariableChangeGenerator(ChangeGenerator):

    def value(self, value):
        '''Generate a change that changes the value of the variable to value.
        Value must be an int, string, bool, list, tuple, or dict. Lists, tuples,
        and dicts, must ALSO only contain ints, strings, bools, lists, tuples,
        or dicts.

        To put it another way, .value() takes in a value, converts it to Python
        source, and then overwrites the variable body with that source.'''

        return self.overwrite_body(format_source(value))
