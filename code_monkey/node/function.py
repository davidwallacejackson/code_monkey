from astroid.node_classes import Arguments

from code_monkey.change import SourceChangeGenerator
from code_monkey.node.base import Node
from code_monkey.utils import absolute_index_to_line_column, find_termination

class FunctionNode(Node):
    '''Class representing a Python function or method, at the module or class
    level.'''

    def __init__(self, parent, name, astroid_object):
        super(FunctionNode, self).__init__()

        self.parent = parent
        self.name = name
        self._astroid_object = astroid_object

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
        #TODO: ignore text in docstrings
        file_source = self.get_file_source_code()
        first_child = self._astroid_child_after_signature
        colon_index = find_termination(
            file_source.splitlines(True),
            first_child.fromlineno - 1,
            first_child.col_offset,
            ':')

        #now that we've found the colon where the function signature ends,
        #search FORWARDS for the next newline. one after that is our start
        #index
        for newline_index, char in enumerate(file_source[colon_index:]):
            if char == '\n':
                return colon_index + newline_index + 1

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
    def outer_indentation(self):
        '''The indentation level, as a string, at the source where this function
        begins.'''
        lines = self.get_file_source_code().splitlines(True)
        return lines[self.start_line][0:self.start_column]

    @property
    def inner_indentation(self):
        '''The indentation level, as a string, of source inside this class.'''
        lines = self.get_file_source_code().splitlines(True)

        #the body may begin with blank lines (which don't tell us the current
        #indentation), so instead, we use the line of the first child
        first_child = self._astroid_child_after_signature
        return lines[first_child.fromlineno][0:first_child.col_offset]
