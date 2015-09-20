import logging

from astroid.node_classes import Assign, Import, Const, Dict, Name, AssName
from astroid.scoped_nodes import Class, Function

from code_monkey.change import SourceChangeGenerator
from code_monkey.node.base import Node
from code_monkey.utils import (
    line_column_to_absolute_index,
    count_lines)

logger = logging.getLogger(__name__)

def get_node_class_mapping():
    '''Return a dictionary mapping astroid classes to their corresponding
    SourceNode equivalent.

    We do this in a function so that we can delay importing the other SourceNode
    classes (thereby preventing circular imports).'''

    from code_monkey import node as cm_nodes

    return {
        Class: cm_nodes.ClassNode,
        Function: cm_nodes.FunctionNode,
        Assign: cm_nodes.AssignmentNode,
        Import: cm_nodes.ImportNode,
        Const: cm_nodes.ConstantNode,
        Name: cm_nodes.NameNode,
        AssName: cm_nodes.AssignmentNameNode
    }

class SourceNode(Node):
    '''Shared base class for all nodes that represent code inside a single
    file (i.e., module or lower).'''

    def __init__(self, parent, astroid_object, siblings=[]):
        super(SourceNode, self).__init__()

        self.parent = parent
        self._astroid_object = astroid_object

        try:
            self.name = astroid_object.name
        except AttributeError:
            #not all astroid nodes have a .name property -- if we need to come
            #up with our own name, that should happen in the subclass' __init__
            #method
            pass

    @property
    def change(self):
        return SourceChangeGenerator(self)

    @property
    def fs_path(self):
        return self.parent.fs_path
    
    def get_source_file(self):
        '''return a read-only file object for the file in which this Node was
        defined. only meaningful at or below the module level -- higher than
        that, source_file is None.'''

        try:
            return open(self.fs_path, 'r')
        except IOError:
            #if the path is to a directory, we'll get an IOError
            return None


    @property
    def start_line(self):
        #astroid gives line numbers starting with 1
        return self._astroid_object.fromlineno - 1

    @property
    def body_start_line(self):
        return self.start_line


    @property
    def end_line(self):
        #astroid gives line numbers starting with 1
        return self._astroid_object.tolineno

    @property
    def body_end_line(self):
        return self.end_line


    @property
    def start_column(self):
        return self._astroid_object.col_offset

    @property
    def body_start_column(self):
        return self.start_column


    @property
    def end_column(self):
        return 0

    @property
    def body_end_column(self):
        return self.end_column


    @property
    def start_index(self):
        '''The character index of the beginning of the node, relative to the
        entire source file.'''
        return line_column_to_absolute_index(
            self.get_file_source_code(),
            self.start_line,
            self.start_column)

    @property
    def end_index(self):
        '''The character index of the character after the end of the node,
        relative to the entire source file.'''
        if self.end_line == count_lines(self.get_file_source_code()) + 1:
            # we're on the last line
            # the "next index" doesn't really exist -- it's the end of the file
            # + 1
            return len(self.get_file_source_code()) 

        return line_column_to_absolute_index(
            self.get_file_source_code(),
            self.end_line,
            self.end_column)

    @property
    def body_start_index(self):
        '''The character index of the beginning of the node body, relative to
        the entire source file.'''
        return line_column_to_absolute_index(
            self.get_file_source_code(),
            self.body_start_line,
            self.body_start_column)

    @property
    def body_end_index(self):
        '''The character index of the character after the end of the node body,
        relative to the entire source file.'''
        if self.body_end_line == count_lines(self.get_file_source_code()) + 1:
            # we're on the last line
            # the "next index" doesn't really exist -- it's the end of the file
            # + 1
            return len(self.get_file_source_code())

        return line_column_to_absolute_index(
            self.get_file_source_code(),
            self.body_end_line,
            self.body_end_column)
 
    def _get_source_region(self, start_index, end_index):
        '''return a substring of the source code starting from start_index up to
        but not including end_index'''

        with open(self.fs_path, 'r') as source_file:

            if not source_file:
                return None

            source = source_file.read()
            source = source[start_index:end_index]

            return source

    def get_file_source_code(self):
        '''Return the text of the entire file containing Node.'''
        with open(self.fs_path, 'r') as source_file:
            if not source_file:
                return None

            return source_file.read()

    def get_source(self):
        '''return a string of the source code the Node represents'''

        return self._get_source_region(
            self.start_index,
            self.end_index)

    def get_body_source(self):
        '''return a string of only the body of the node -- i.e., excluding the
        declaration. For a Class or Function, that means the class or function
        body. For a Variable, that's the right hand of the assignment. For a
        Module, it's the same as get_source().'''
        return self._get_source_region(
            self.body_start_index,
            self.body_end_index)

    @property
    def outer_indentation(self):
        '''The indentation level, as a string, at the source where this node
        begins.'''
        lines = self.get_file_source_code().splitlines(True)
        return lines[self.start_line][0:self.start_column]

    @property
    def children(self):
        #all of the children found by astroid:

        astroid_children = self._astroid_object.get_children()
        children = {}

        for child in astroid_children:

            try:
                code_monkey_class = get_node_class_mapping()[child.__class__]
                child_node = code_monkey_class(
                    parent=self,
                    astroid_object=child,
                    siblings=children)

                children[child_node.name] = child_node

            except KeyError:
                #there's no equivalent to this astroid class in code_monkey yet
                logger.debug('AST node omitted: ' + str(child))

        return children
