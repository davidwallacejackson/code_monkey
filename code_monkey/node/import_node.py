'''Named import_node instead of import because import is a reserved word.'''

from code_monkey.change import SourceChangeGenerator
from code_monkey.node.base import Node


# TODO: convert to SourceNode
class ImportNode(Node):
    '''Node representing an import statement.'''

    def __init__(self, parent, astroid_object, siblings):
        super(ImportNode, self).__init__()
        self.parent = parent
        self._astroid_object = astroid_object

        base_name = astroid_object.names[0][0]
        self.name = base_name

        index = 0
        while self.name in siblings:
            self.name = base_name + '_' + str(index)
            index += 1

        # so for multiple imports from datetime, you get datetime,
        # datetime_0, datetime_1 etc.

    @property
    def change(self):
        return SourceChangeGenerator(self)

    @property
    def fs_path(self):
        return self.parent.fs_path
