from os import path

from nose.tools import assert_equal, assert_is_instance, assert_not_equal

from code_monkey.node import (
    ClassNode,
    FunctionNode,
    ImportNode,
    ModuleNode,
    PackageNode,
    ProjectNode,
    AssignmentNode)
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
    assert_equal(len(q.children()), len(q[0].children))

    #the number of nodes in the whole project tree, including the root
    assert_equal(len(q.flatten()), 46)


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

    for match in q.flatten().assignments():
        assert_is_instance(match, AssignmentNode)

    for match in q.flatten().imports():
        assert_is_instance(match, ImportNode)


def test_find_filters():
    '''Test that queries properly filter out Nodes based on text searches'''

    #settings is at the root, so searching on lib should exclude it
    for match in q.flatten().path_contains('lib'):
        assert_not_equal(match.name, 'settings')

    code_monkey_class_query = q.flatten().classes().source_contains(
        'def get_coffee(self)')
    assert_equal(code_monkey_class_query[0].name, 'CodeMonkey')

    also_code_monkey_class_query = q.flatten().classes().has_child(
        'things_code_monkey_like')
    assert_equal(also_code_monkey_class_query[0].name, 'CodeMonkey')

    weird_subclass_query = q.flatten().classes().subclass_of_name(
        'datetime.datetime')
    assert_equal(weird_subclass_query[0].name, 'WeirdSubclass')

def test_no_duplicates():
    '''Test that duplicates of the same Node are omitted from queries.'''

    #flatten the whole tree, and join() it with itself:
    flattened = q.flatten()
    assert_equal(
        len(flattened),
        len(flattened.join(flattened)))

def test_constant():
    '''Test that we can find several types of constant nodes.'''

    constants = q.flatten().constants()

    assert_equal(constants.path_contains('ONE_LINER')[0].value_type, 'str')
    assert_equal(constants.path_contains('BASE_PAY')[0].value_type, 'int')
