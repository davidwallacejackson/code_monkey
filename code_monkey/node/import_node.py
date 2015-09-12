'''Named import_node instead of import because import is a reserved word.'''

from code_monkey.change import SourceChangeGenerator
from code_monkey.node.base import Node


class ImportNode(Node):
    '''Node representing an import statement.'''

    def __init__(self, parent, name, astroid_object):
        super(ImportNode, self).__init__()

        self.parent = parent
        self.name = name
        self._astroid_object = astroid_object

    @property
    def change(self):
        return SourceChangeGenerator(self)

    @property
    def fs_path(self):
        return self.parent.fs_path
