from code_monkey.node import (
    ClassNode,
    FunctionNode,
    ModuleNode,
    PackageNode,
    ProjectNode,
    VariableNode)

class NodeQuery(object):

    def __init__(self, matches=[]):
        self.matches = matches

    def __getitem__(self, index):
        return self.matches[index]

    def __len__(self):
        return len(self.matches)

    def join(self, *other_queries):
        '''Return a new Query encompassing both this query and all parameter
        Queries'''

        #copy our own matches
        new_matches = list(self.matches)

        for other_query in other_queries:
            new_matches.extend(other_query.matches)

        return NodeQuery(new_matches)

    def children(self):
        '''Return a new Query encompassing all immediate children of matches'''
        children = []

        for match in self:
            children.extend(match.children)

        return NodeQuery(children)

    def descendents(self):
        '''Return a flat Query of all nodes descended from matches'''

        children = self.children()
        descendents = NodeQuery([])

        for child in children:
            #first, recurse down and collect any descendents from children...
            child_descendents = NodeQuery([child]).descendents()

            descendents = descendents.join(child_descendents)

        #...then join the children themselves to the list
        descendents = descendents.join(children)

        return descendents

    def flatten(self):
        '''Return a flat query of matches and all their descendents'''

        return self.join(self.descendents())

    def filter_type(self, type_cls):
        '''Return only the query elements of a certain type; i.e. ClassNode,
        FunctionNode, etc.'''

        filter_matches = []

        for match in self:
            if isinstance(match, type_cls):
                filter_matches.append(match)

        return NodeQuery(filter_matches)

    def packages(self):
        return self.filter_type(PackageNode)

    def modules(self):
        #'leaf' modules only; though Python considers packages to be a type of
        #module, we do not
        return self.filter_type(ModuleNode)

    def classes(self):
        return self.filter_type(ClassNode)

    def functions(self):
        return self.filter_type(FunctionNode)

    def variables(self):
        #variables at module scope only
        return self.filter_type(VariableNode)

    def path_contains(self, find_me):
        '''Match nodes whose path contains the string find_me'''
        filter_matches = []

        for match in self:
            if find_me in match.path:
                filter_matches.append(match)

        return NodeQuery(filter_matches)

    def source_contains(self, find_me):
        '''Match nodes whose source contains the string find_me.'''

        filter_matches = []

        for match in self:
            if match.source_file and find_me in match.get_source_code():
                filter_matches.append(match)

        return NodeQuery(filter_matches)


    def has_name(self, find_me):
        '''Match nodes whose scope contains a name find_me.'''

        filter_matches = []

        for match in self:
            if match.rope_scope and \
                    find_me in match.rope_scope.get_names().keys():
                filter_matches.append(match)

        return NodeQuery(filter_matches)
