from os import path

from nose.tools import assert_equal, assert_is_instance, assert_not_equal

from code_monkey.node import (
    ClassNode,
    FunctionNode,
    ModuleNode,
    PackageNode,
    ProjectNode,
    VariableNode)
from code_monkey.node_query import NodeQuery

TEST_PROJECT_PATH = path.join(
    path.dirname(path.realpath(__file__)),
    '../test_project')

project = ProjectNode(TEST_PROJECT_PATH)
q = NodeQuery([project])


def test_descent():
    '''Test that queries traverse the tree properly.'''

    #.children() should only get the direct children of matches -- and we only
    #have one match in q
    assert_equal(len(q.children()), len(q.matches[0].children))

    #the number of nodes in the whole project tree, including the root
    assert_equal(len(q.flatten()), 9)
    
    #this would count __init__, as well
    # assert_equal(len(q.flatten()), 11)


def test_type_filters():
    '''Test that queries properly filter out different types of Nodes'''
    for match in q.flatten().packages():
        assert_is_instance(match, PackageNode)

    for match in q.flatten().modules():
        assert_is_instance(match, ModuleNode)

    for match in q.flatten().classes():
        assert_is_instance(match, ClassNode)

    for match in q.flatten().functions():
        assert_is_instance(match, FunctionNode)

    for match in q.flatten().variables():
        assert_is_instance(match, VariableNode)


def test_find_filters():
    '''Test that queries properly filter out Nodes based on text searches'''

    #settings is at the root, so searching on lib should exclude it
    for match in q.flatten().path_contains('lib'):
        assert_not_equal(match.name, 'settings')

    code_monkey_class_query = q.flatten().source_contains(
        'def get_coffee(self)')

    assert_equal(len(code_monkey_class_query), 2)
    assert_equal(code_monkey_class_query[0].name, 'CodeMonkey')
