from astroid.manager import AstroidManager
from astroid.node_classes import Assign, Import
from astroid.scoped_nodes import Class, Function
from logilab.common.modutils import modpath_from_file

from code_monkey.change import SourceChangeGenerator
from code_monkey.node.base import Node
from code_monkey.node.class_node import ClassNode
from code_monkey.node.function import FunctionNode
from code_monkey.node.import_node import ImportNode
from code_monkey.node.assignment import AssignmentNode

class ModuleNode(Node):
    '''Node representing a module (a single Python source file).'''

    def __init__(self, parent, fs_path):
        super(ModuleNode, self).__init__()

        self.parent = parent
        self._fs_path = fs_path

        #gets the module name -- the whole return value of modpath_from_file
        #is a list containing each element of the dotpath
        self.name = modpath_from_file(fs_path)[-1]

        self._astroid_object = AstroidManager().ast_from_file(fs_path)

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
                child_node = AssignmentNode(
                    parent=self,
                    astroid_object=child)

                children[child_node.name] = child_node

            elif isinstance(child, Import):
                base_name = child.names[0][0]
                name = base_name

                index = 0
                while name in children:
                    name = base_name + '_' + str(index)
                    index += 1

                # so for multiple imports from datetime, you get datetime,
                # datetime_0, datetime_1 etc.

                child_node = ImportNode(
                    parent=self,
                    name=name,
                    astroid_object=child)

                children[child_node.name] = child_node

        return children

    @property
    def start_line(self):
        #for modules, astroid gives 0 as the start line -- so we don't want to
        #subtract 1
        return self._astroid_object.fromlineno

    @property
    def start_column(self):
        #for modules, astroid gives None as the column offset -- by our
        #conventions, it should be 0
        return 0
