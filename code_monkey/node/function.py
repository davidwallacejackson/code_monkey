from astroid.node_classes import Arguments

from code_monkey.change import SourceChangeGenerator
from code_monkey.node.source import SourceNode
from code_monkey.utils import (
    absolute_index_to_line_column,
    find_termination,
    safe_docstring)

class FunctionNode(SourceNode):
    '''Class representing a Python function or method, at the module or class
    level.'''

    @property
    def change(self):
        return SourceChangeGenerator(self)

    @property
    def fs_path(self):
        return self.parent.fs_path

    @property
    def _astroid_child_after_signature(self):
        for child in self._astroid_object.get_children():
            if not isinstance(child, Arguments):
                return child

    @property
    def body_start_index(self):
        file_source = self.get_file_source_code()
        first_child = self._astroid_child_after_signature

        #see the safe_docstring function for details on why we do this
        docstring = self._astroid_object.doc
        if docstring and ':' in docstring:
            file_source = file_source.replace(
                docstring,
                safe_docstring(docstring))

        
        #first character AFTER the colon at the end of the signature
        after_colon_index = find_termination(
            file_source.splitlines(True),
            first_child.fromlineno - 1,
            first_child.col_offset,
            ':')

        #now that we've found the colon where the function signature ends,
        #search FORWARDS for the next newline. one after that is our start
        #index
        for newline_index, char in enumerate(file_source[after_colon_index:]):
            if char == '\n':
                return after_colon_index + newline_index + 1

    @property
    def body_start_line(self):
        return absolute_index_to_line_column(
            self.get_file_source_code(),
            self.body_start_index)[0]

    @property
    def body_start_column(self):
        return absolute_index_to_line_column(
            self.get_file_source_code(),
            self.body_start_index)[1]


    @property
    def inner_indentation(self):
        '''The indentation level, as a string, of source inside this class.'''
        lines = self.get_file_source_code().splitlines(True)

        #the body may begin with blank lines (which don't tell us the current
        #indentation), so instead, we use the line of the first child
        first_child = self._astroid_child_after_signature
        return lines[first_child.fromlineno][0:first_child.col_offset]

