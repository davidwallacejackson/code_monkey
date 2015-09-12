from astroid.manager import AstroidManager
from logilab.common.modutils import modpath_from_file

from code_monkey.change import SourceChangeGenerator
from code_monkey.node.source import SourceNode

class ModuleNode(SourceNode):
    '''Node representing a module (a single Python source file).'''

    def __init__(self, parent, fs_path):
        #gets the module name -- the whole return value of modpath_from_file
        #is a list containing each element of the dotpath
        name = modpath_from_file(fs_path)[-1]

        astroid_object = AstroidManager().ast_from_file(fs_path)

        super(ModuleNode, self).__init__(
            name=name,
            parent=parent,
            astroid_object=astroid_object)

        self._fs_path = fs_path

    @property
    def change(self):
        return SourceChangeGenerator(self)

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

    @property
    def fs_path(self):
        return self._fs_path
