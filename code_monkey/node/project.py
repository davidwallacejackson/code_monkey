from logilab.common.modutils import modpath_from_file

from code_monkey.node.base import Node
from code_monkey.node.module import ModuleNode
from code_monkey.node.package import PackageNode
from code_monkey.utils import get_modules

class ProjectNode(Node):
    '''Node representing an entire Python project. The project root may or may
    not be a package, but it must exist within the Python path of the current
    environment.'''

    def __init__(self, project_path):
        super(ProjectNode, self).__init__()

        #gets the python 'dotpath' of the project root. If the project root
        #itself is in the Python path, this will be an empty string
        self.name = '.'.join(modpath_from_file(project_path))

        self.parent = None
        self.scope = None

        #the file system (not python) path to the project
        self._fs_path = project_path

    @property
    def children(self):
        '''astroid doesn't expose the children of packages in a convenient way,
        so we the filesystem to list them and build child nodes'''

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

    @property
    def path(self):
        return self.name

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return '{}: {}'.format(
            str(self.__class__.__name__),
            self.name)
