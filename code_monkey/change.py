'''Code to generate new changes to the source of a Node. Every change is a
single Change object.

Nothing in this module actually overwrites files: that occurs in edit, where
Changes are grouped into ChangeSets. ChangeSets check that individual changes
do not conflict, provide diffs, and commit changes to disk.
'''
import difflib

from code_monkey.format import format_value
from code_monkey.utils import line_column_to_absolute_index

class Change(object):
    '''A single change to make to a single file. Replaces the file content
    from indices start through (end-1) with new_text.

    Args:
        path (str): The filesystem path of the file to edit.
        start (int): The index of the beginning of the region to overwrite.
        end (int): The index of the end of the region to overwrite
                   (non-inclusive).
        new_text (str): The new text to write over the old region.'''
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

        return Change(
            self.node.fs_path,
            self.node.start_index,
            self.node.end_index,
            new_source)

    def overwrite_body(self, new_source):
        '''Generate a change that overwrites the body of the node with
        new_source. In the case of a ModuleNode, this is equivalent to
        overwrite().'''

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

    def inject_at_body_line(self, line_index, inject_source):
        '''As inject_at_body_index, but takes a line index instead of a
        character index.'''

        character_index_of_line = line_column_to_absolute_index(
            self.node.get_body_source(),
            line_index,
            0)

        return self.inject_at_body_index(
            character_index_of_line, inject_source)

    def inject_before(self, inject_source):
        '''Generate a change that inserts inject_source starting on the line
        before this node.'''
        try:
            character_index_of_line = line_column_to_absolute_index(
                self.node.get_file_source_code(),
                self.node.start_line,
                0)
        except ValueError:
            # our node is at the beginning of its file
            # we'll need to select the first character of the file...
            character_index_of_line = 0

            # ...and "create" a line by inserting a newline into our source
            inject_source = '\n' + inject_source

        return Change(
            self.node.fs_path,
            character_index_of_line,
            character_index_of_line,
            inject_source)


    def inject_after(self, inject_source):
        '''Generate a change that inserts inject_source starting on the line
        after this node.'''
        try:
            character_index_of_line = line_column_to_absolute_index(
                self.node.get_file_source_code(),
                self.node.end_line + 1,
                0)
        except ValueError:
            # our node is at the end of its file
            # we'll need to select the last character of the file...
            character_index_of_line = len(self.node.get_file_source_code())

            # ...and "create" a line by inserting a newline into our source
            inject_source = '\n' + inject_source

        return Change(
            self.node.fs_path,
            character_index_of_line,
            character_index_of_line,
            inject_source)


class SourceChangeGenerator(ChangeGenerator):
    '''ChangeGenerator for Nodes that encompass a body of full Python source
    code -- i.e., modules, classes, and functions.'''

    def inject_assignment(self,
            name,
            value,
            extra_trailing_newline=False,
            convert_value=True,
            line_index=0):
        '''
        Injects a variable assignment, name = value, at line_index.

        Generated variables get one newline before. If you want to pass in raw
        source (instead of a value to be converted into source by a formatter),
        use convert_value=False.

        If extra_trailing_newline==True, one additional newline will be added
        after the variable declaration, so that there's a full blank line
        between it and the next line of source code.

        line_index is relative to the node body. If line_index is not provided,
        the variable will be inserted at node.body_start_line.
        '''

        indentation = self.node.inner_indentation
        if convert_value:
            value = format_value(
                value,
                starting_indentation=indentation)

        generated_source = '\n' + indentation + name + ' = ' + value + '\n'

        if extra_trailing_newline:
            generated_source += '\n'

        return self.inject_at_body_line(
            line_index,
            generated_source)


class VariableChangeGenerator(ChangeGenerator):
    '''ChangeGenerator for variable assignment nodes'''

    def value(self, value):
        '''Generate a change that changes the value of the variable to value.
        Value must be an int, string, bool, list, tuple, or dict. Lists, tuples,
        and dicts, must ALSO only contain ints, strings, bools, lists, tuples,
        or dicts.

        To put it another way, .value() takes in a value, converts it to Python
        source, and then overwrites the variable body with that source.'''

        return self.overwrite_body(
            format_value(
                value,
                starting_indentation=self.node.outer_indentation,
                indent_first_line=False))
