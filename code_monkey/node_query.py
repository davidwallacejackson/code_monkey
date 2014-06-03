from code_monkey.node import (
    ProjectNode,
    ClassNode,
    FunctionNode,
    ModuleNode,
    PackageNode,
    ProjectNode,
    VariableNode)

def project_query(project_path):
    '''Return a NodeQuery containing a ProjectNode representing the Python
    project at project_path.'''

    return NodeQuery(
        ProjectNode(project_path))

class NodeQuery(object):
    '''A set of nodes, which can be filtered down to select nodes that match
    certain criteria.'''

    def __init__(self, matches=[]):

        #for convenience, NodeQueries called with a single argument will
        #automatically coerce it to a single-item list
        if not isinstance(matches, list):
            matches = [matches]

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
            children.extend(match.children.values())

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
            if match.get_source_file() and find_me in match.get_source():
                filter_matches.append(match)

        return NodeQuery(filter_matches)


    def has_child(self, find_me):
        '''Match nodes who have an immediate child with the name find_me'''

        filter_matches = []

        for match in self:
            if find_me in match.children.keys():
                filter_matches.append(match)

        return NodeQuery(filter_matches)

    def subclass_of_name(self, find_me):
        '''Match nodes who are a direct subclass of a parent named find_me.

        TODO: create a smarter subclass_of method that takes a ClassNode and
        scans the tree for direct and indrect subclasses.'''

        filter_matches = []

        for match in self:
            if hasattr(match._astroid_object, 'basenames') and \
                    find_me in match._astroid_object.basenames:
                filter_matches.append(match)

        return NodeQuery(filter_matches)
