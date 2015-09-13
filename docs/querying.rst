.. currentmodule :: code_monkey.node_query

Querying Your Project
=====================

code_monkey exposes a chaining query DSL for searching your project's
codebase. Specifically, it has a class called ``NodeQuery`` that acts as a
wrapper around a set of nodes. You can call filtering methods on NodeQueries
to narrow your search, or index into them like a list to grab individual
nodes and inspect them.

Here's an example::

    from code_monkey.node_query import project_query

    #this is a single-element query containing just a "Project" node
    project = project_query('path/to/my/project')

    #this is a query containing every node in your project
    #(this includes packages, modules, function definitions, classes,
    #import statements, and variable assignments)
    everything = project.flatten()

    #this query contains a node for every class in your project
    just_classes = everything.classes()

    #this is only classes that have 'tests.' in their Python dotpath
    just_test_classes = just_classes.path_contains('tests.')

    #this is only methods of said test classes
    #(i.e., function nodes that are direct children of a class)
    test_methods = just_test_classes.children().functions()

    #this is the first FunctionNode in the above query, representing a
    #single method
    single_method = test_methods[0]


Chaining query methods creates new instances of NodeQuery, rather than
modifying old ones, so you can keep old queries around and use them to
perform new searches.

Here's a detailed breakdown of the search functionality available to you:

.. autofunction :: project_query

.. autoclass :: NodeQuery
    :members:
    :exclude-members: as_list

