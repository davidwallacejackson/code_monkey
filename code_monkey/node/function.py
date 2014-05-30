from code_monkey.change import SourceChangeGenerator
from code_monkey.node.base import Node

class FunctionNode(Node):
    '''Class representing a Python function or method, at the module or class
    level.'''

    def __init__(self, parent, name, astroid_object):
        super(FunctionNode, self).__init__()

        self.parent = parent
        self.name = name
        self._astroid_object = astroid_object

    @property
    def change(self):
        return SourceChangeGenerator(self)

    @property
    def fs_path(self):
        return self.parent.fs_path

    @property
    def body_start_line(self):
        #TODO: account for multi-line function signatures
        return self.start_line + 1

    @property
    def body_start_column(self):
        return 0
