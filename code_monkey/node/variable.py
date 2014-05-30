from ast import literal_eval

from code_monkey.change import VariableChangeGenerator
from code_monkey.node.base import Node
from code_monkey.utils import (
    absolute_index_to_line_column,
    line_column_to_absolute_index)

class VariableNode(Node):
    '''Node representing a variable assignment inside Python source code.

    The body of the variable is considered to be everything on the right of the
    = sign, beginning with the first non-whitespace character. Unlike classes
    and functions, a variable's source does NOT include a newline at the end.'''

    def __init__(self, parent, astroid_object):
        super(VariableNode, self).__init__()

        self.parent = parent

        #the _astroid_object (an Assign object) has TWO children that we need to
        #consider: (the variable name) and another astroid node (the 'right
        #hand' value)
        self._astroid_object = astroid_object

        #TODO: account for tuple assignment
        self._astroid_name = self._astroid_object.targets[0]
        self._astroid_value = self._astroid_object.value

        try:
            self.name = self._astroid_name.name
        except AttributeError:
            #'subscript' assignments (a[b] = ...) don't have a name in astroid.
            #instead, we give them one by reading their source

            #TODO: this can result in names containing dots, which is invalid.
            #need a better solution
            self.name = self._astroid_name.as_string()

    def eval_body(self):
        '''Attempt to evaluate the body (i.e., the value) of this VariableNode
        using ast.literal_eval (which will evaluate ONLY Python literals).

        Return the value if successful, otherwise, return None.'''
        try:
            return literal_eval(self.get_body_source())
        except (SyntaxError, ValueError):
            return None

    @property
    def fs_path(self):
        return self.parent.fs_path

    @property
    def change(self):
        return VariableChangeGenerator(self)

    #the 'whole source' of a VariableNode includes the name and the value
    @property
    def start_line(self):
        return self._astroid_name.fromlineno - 1

    @property
    def start_column(self):
        return self._astroid_name.col_offset

    #in a VariableNode, the _astroid_value represents the body
    @property
    def body_start_line(self):
        return self._astroid_value.fromlineno - 1

    @property
    def body_start_column(self):
        return self._astroid_value.col_offset

    @property
    def end_index(self):
        #there's a bug in astroid where it doesn't correctly detect the last
        #line of multiline enclosed blocks (parens, brackets, etc.) -- it gives
        #the last line with content, rather than the line containing the
        #terminating character

        #we have to work around this by scanning through the source ourselves to
        #find the terminating point

        #astroid bug report submitted:
        #https://bitbucket.org/logilab/astroid/issue/31/astroid-sometimes-reports-the-wrong

        file_source_lines = self.get_file_source_code().splitlines(True)

        #we start by finding the line/column at which the next 'sibling' of
        #this node begins. if the node is at the end of the file, we get the
        #end of the file instead
        next_sibling = self._astroid_object.next_sibling()
        astroid_end_line = self._astroid_value.tolineno - 1
        if next_sibling:
            next_sibling_line = next_sibling.fromlineno
            next_sibling_column = next_sibling.col_offset
            lines_to_scan = file_source_lines[
                astroid_end_line:(next_sibling_line+1)]

            #trim the last line so that we don't include any of the sibling
            lines_to_scan[-1] = lines_to_scan[-1][0:next_sibling_column]
        else:
            #if there is no sibling, we just start from the end of the file
            lines_to_scan = file_source_lines[
                self._astroid_value.tolineno:len(file_source_lines)]

        #this string doesn't have the right formatting, but it should be
        #otherwise correct -- so we can use it to see what character our
        #variable ends on
        terminating_char = self._astroid_value.as_string()[-1]

        #scan through the lines in reverse order, looking for the end of the
        #node

        #len(lines_to_scan) - (line_index + 1) is the index of a line in
        #lines_to_scan -- basically, it takes us from the 'reversed'
        #indices that we get in line_index back to real, from-the-beginning
        #indices
        for line_index, line in enumerate(reversed(lines_to_scan)):

            #remove comments from line
            if '#' in line:
                line = line[0:line.find('#')]

            for char_index, char in enumerate(reversed(line)):
                if char == terminating_char:
                    line_index_in_file = astroid_end_line + (
                        len(lines_to_scan) - (line_index + 1))
                    char_index_in_line = len(line) - char_index
                    return line_column_to_absolute_index(
                        self.get_file_source_code(),
                        line_index_in_file,
                        char_index_in_line)


    #for variable nodes, it's easiest to find an absolute end index first, then
    #work backwards to get line and column numbers
    @property
    def end_line(self):
        return absolute_index_to_line_column(
            self.get_file_source_code(),
            self.end_index)[0]

    @property
    def end_column(self):
        return absolute_index_to_line_column(
            self.get_file_source_code(),
            self.end_index)[1]
