from logilab.common.modutils import modpath_from_file

from code_monkey.node.base import Node
from code_monkey.node.module import ModuleNode
from code_monkey.utils import get_modules

class PackageNode(Node):
    '''Node representing a Python package (a directory containing an __init__.py
    file)'''

    def __init__(self, parent, fs_path):
        super(PackageNode, self).__init__()

        self.parent = parent
        self._fs_path = fs_path

        #gets the module name -- the whole return value of modpath_from_file
        #is a list containing each element of the dotpath
        self.name = modpath_from_file(fs_path)[-1]

    @property
    def children(self):
        '''astroid doesn't expose the children of packages in a convenient way,
        so we use pkgutil to access them and build child nodes'''

        fs_children = get_modules(self.fs_path)

        children = {}

        for fs_path, is_package in fs_children:
            if is_package:
                child = PackageNode(
                    parent=self,
                    fs_path=fs_path)
                children[child.name] = child
            else:
                child = ModuleNode(
                    parent=self,
                    fs_path=fs_path)
                children[child.name] = child

        return children
