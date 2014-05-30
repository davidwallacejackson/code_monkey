'''Named class_node instead of class because class is reserved in python for the
class keyword'''

from astroid.node_classes import Assign
from astroid.scoped_nodes import Class, Function

from code_monkey.change import SourceChangeGenerator
from code_monkey.node.base import Node
from code_monkey.node.function import FunctionNode
from code_monkey.node.variable import VariableNode


class ClassNode(Node):
    '''Node representing a Python class. The class may be at the module level,
    or nested inside another class.'''

    def __init__(self, parent, name, astroid_object):
        super(ClassNode, self).__init__()

        self.parent = parent
        self.name = name
        self._astroid_object = astroid_object

    @property
    def change(self):
        return SourceChangeGenerator(self)

    @property
    def children(self):
        #all of the children found by astroid:

        astroid_children = self._astroid_object.get_children()
        children = {}

        for child in astroid_children:

            if isinstance(child, Class):

                children[child.name] = ClassNode(
                    parent=self,
                    name=child.name,
                    astroid_object=child)

            elif isinstance(child, Function):

                children[child.name] = FunctionNode(
                    parent=self,
                    name=child.name,
                    astroid_object=child)

            elif isinstance(child, Assign):
                #Assign is the class representing a variable assignment.

                #we don't know the name of the variable until we build the Node,
                #so we build the node before adding it to the children dict
                child_node = VariableNode(
                    parent=self,
                    astroid_object=child)

                children[child_node.name] = child_node

        return children

    @property
    def fs_path(self):
        return self.parent.fs_path

    @property
    def body_start_line(self):
        #TODO: account for multi-line class signatures
        return self.start_line + 1

    @property
    def body_start_column(self):
        return 0
