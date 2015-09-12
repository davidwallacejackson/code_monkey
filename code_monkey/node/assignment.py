from ast import literal_eval

from code_monkey.change import VariableChangeGenerator
from code_monkey.node.source import SourceNode
from code_monkey.utils import (
    absolute_index_to_line_column,
    find_termination)

class AssignmentNode(SourceNode):
    '''Node representing a variable assignment inside Python source code.

    The body of the variable is considered to be everything on the right of the
    = sign, beginning with the first non-whitespace character. Unlike classes
    and functions, a variable's source does NOT include a newline at the end.'''

    def __init__(self, parent, astroid_object):
        #the _astroid_object (an Assign object) has TWO children that we need to
        #consider: the variable name, and another astroid node (the 'right
        #hand' value)
        self._astroid_name = astroid_object.targets[0]
        self._astroid_value = astroid_object.value

        try:
            name = self._astroid_name.name
        except AttributeError:
            #'subscript' assignments (a[b] = ...) don't have a name in astroid.
            #instead, we give them one by reading their source

            #TODO: this can result in names containing dots, which is invalid.
            #need a better solution
            name = self._astroid_name.as_string()

        super(AssignmentNode, self).__init__(
            parent=parent,
            name=name,
            astroid_object=astroid_object)

    def eval_body(self):
        '''Attempt to evaluate the body (i.e., the value) of this AssignmentNode
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

    #the 'whole source' of a AssignmentNode includes the name and the value
    @property
    def start_line(self):
        return self._astroid_name.fromlineno - 1

    @property
    def start_column(self):
        return self._astroid_name.col_offset

    #in a AssignmentNode, the _astroid_value represents the body
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
        if next_sibling:
            scan_from_line = next_sibling.fromlineno
            scan_from_column = next_sibling.col_offset - 1
        else:
            scan_from_line = len(file_source_lines) - 1
            scan_from_column = len(file_source_lines[scan_from_line]) - 1

        #this string doesn't have the right formatting, but it should be
        #otherwise correct -- so we can use it to see what character our
        #variable ends on
        terminating_char = self._astroid_value.as_string()[-1]

        return find_termination(
            file_source_lines,
            scan_from_line,
            scan_from_column,
            terminating_char)


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
