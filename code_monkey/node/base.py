from code_monkey.change import ChangeGenerator
from code_monkey.utils import line_column_to_absolute_index

class Node(object):
    '''Base class for all Nodes in the code_monkey project tree.'''

    def __init__(self):
        self.parent = None

    @property
    def change(self):
        return ChangeGenerator(self)

    @property
    def children(self):
        return {}

    @property
    def root(self):
        '''return the root Node in the tree (should be a ProjectNode)'''
        if self.parent:
            return self.parent.root

        return self

    @property
    def fs_path(self):
        #some nodes will recurse upward to find their fs_path, which is why we
        #hide it behind a property method
        return self._fs_path

    @property
    def path(self):
        parent_path = self.parent.path

        #prevents an 'empty' root from giving us paths like '.foo.bar.baz'
        if parent_path == '':
            return self.name

        return parent_path + '.' + self.name

    #TODO: make nodes not __eq__ after the underlying source has changed.
    #This would also be a good opportunity to add some kind of caching.
    def __eq__(self, other):
        return self.path == other.path

    def __unicode__(self):
        return '{}: {}'.format(
            str(self.__class__.__name__),
            self.path)

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return self.__unicode__()
