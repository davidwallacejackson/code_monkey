from code_monkey.node import ProjectNode

class NodeQuery(object):

    def __init__(self, matches=[]):
        self.matches = matches

    def join(self, *other_queries):
        '''Return a new Query encompassing both this query and all parameter
        Queries'''

        new_matches = self.matches

        for other_query in other_queries:
            new_matches.extend(other_query.matches)

        return NodeQuery(new_matches)

    def children(self):
        '''Return a new Query encompassing all immediate children of matches'''
        children = []

        for match in self.matches:
            children.extend(match.children)

        return NodeQuery(children)

    def descendents(self):
        '''Return a flat Query of all nodes descended from matches'''

        descendents = self.children()

        for child in descendents.matches:
            child_descendents = NodeQuery([child]).descendents()

            descendents = descendents.join(child_descendents)

        return descendents

    def flatten(self):
        '''Return a flat query of matches and all their descendents'''

        return self.join(self.descendents())
