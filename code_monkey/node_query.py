from code_monkey.node import (
    Node,
    ProjectNode,
    ClassNode,
    FunctionNode,
    ImportNode,
    ModuleNode,
    PackageNode,
    ProjectNode,
    AssignmentNode,
    ConstantNode)

def project_query(project_path):
    '''Take a filesystem path project_path, and return a NodeQuery containing
    a ProjectNode representing the Python project at that path.

    When working with a new project, this is usually the first thing you
    should use.'''

    return NodeQuery(
        ProjectNode(project_path))

class NodeQuery(object):
    '''A set of nodes, which can be filtered down to select nodes that match
    certain criteria.'''

    def __init__(self, matches=set()):

        #for convenience, NodeQueries called with a single Node will
        #automatically coerce it to a single-item set, and they'll coerce lists
        #into sets as well
        if isinstance(matches, Node):
            matches = set([matches])
        elif isinstance(matches, list):
            matches = set(matches)

        self.matches = matches

    def __getitem__(self, index):
        return self.as_list[index]

    def __iter__(self):
        return self.matches.__iter__()

    def __len__(self):
        return len(self.matches)

    @property
    def as_list(self):
        '''Returns an ordered list of the nodes in the query. Queries don't
        change, so we cache the list.'''
        if not hasattr(self, '_as_list'):
            self._as_list = list(self.matches)

        return self._as_list

    def join(self, *other_queries):
        '''Return a new query encompassing both this query and all parameter
        queries'''

        #copy our own matches
        new_matches = self.matches.copy()

        for other_query in other_queries:
            new_matches = new_matches.union(other_query.matches)

        return NodeQuery(new_matches)

    def children(self):
        '''Return a new query encompassing all immediate children of matches'''
        children = set()

        for match in self:
            children = children.union(set(match.children.values()))

        return NodeQuery(children)

    def descendents(self):
        '''Return a flat query of all nodes descended from matches'''

        children = self.children()
        descendents = NodeQuery(set())

        for child in children:
            #first, recurse down and collect any descendents from children...
            child_descendents = NodeQuery([child]).descendents()

            descendents = descendents.join(child_descendents)

        #...then join the children themselves to the set
        descendents = descendents.join(children)

        return descendents

    def flatten(self):
        '''Return a flat query of matches and all their descendents'''

        return self.join(self.descendents())

    def filter_type(self, type_cls):
        '''Return only the query elements of a certain type; i.e. ClassNode,
        FunctionNode, etc.'''

        filter_matches = set()

        for match in self:
            if isinstance(match, type_cls):
                filter_matches.add(match)

        return NodeQuery(filter_matches)

    def packages(self):
        '''Return a query containing only PackageNodes.'''
        return self.filter_type(PackageNode)

    def modules(self):
        '''Return a query containing only ModuleNodes.

        Note that ModuleNodes represent 'leaf' modules only; while Python
        considers a package to be a type of module, code_monkey does not.'''
        return self.filter_type(ModuleNode)

    def classes(self):
        '''Return a query containing only ClassNodes.'''
        return self.filter_type(ClassNode)

    def functions(self):
        '''Return a query containing only FunctionNodes, which may represent
        functions or methods.'''
        return self.filter_type(FunctionNode)

    def assignments(self):
        '''Return a query containing only AssignmentNodes, which represent
        variable assignments.'''
        return self.filter_type(AssignmentNode)

    def imports(self):
        '''Return a query containing only ImportNodes.'''
        return self.filter_type(ImportNode)

    def constants(self):
        '''Return a query containing only ConstantNodes.'''
        return self.filter_type(ConstantNode)

    def path_contains(self, find_me):
        '''Match nodes whose path contains the string find_me'''
        filter_matches = set()

        for match in self:
            if find_me in match.path:
                filter_matches.add(match)

        return NodeQuery(filter_matches)

    def source_contains(self, find_me):
        '''Match nodes whose source contains any string in the list find_me. If
        find_me is a single string, it will be coerced to a list.'''

        if isinstance(find_me, str):
            find_me = [find_me]

        filter_matches = set()

        for match in self:
            if match.get_source_file():
                source = match.get_source()

                for test_string in find_me:
                    if test_string in source:
                        filter_matches.add(match)
                        break

        return NodeQuery(filter_matches)


    def has_child(self, find_me):
        '''Match nodes who have an immediate child with the name find_me'''

        filter_matches = set()

        for match in self:
            if find_me in match.children.keys():
                filter_matches.add(match)

        return NodeQuery(filter_matches)

    def subclass_of_name(self, find_me):
        '''Match nodes who are a direct subclass of a parent named find_me.'''
        # TODO: create a smarter subclass_of method that takes a ClassNode and
        # scans the tree for direct and indrect subclasses.

        filter_matches = set()

        for match in self:
            if hasattr(match._astroid_object, 'basenames') and \
                    find_me in match._astroid_object.basenames:
                filter_matches.add(match)

        return NodeQuery(filter_matches)
