from os import path

from nose.tools import assert_equal, assert_is_instance

from code_monkey.node import (
    ClassNode,
    ModuleNode,
    PackageNode,
    ProjectNode,
    VariableNode)

TEST_PROJECT_PATH = path.join(
    path.dirname(path.realpath(__file__)),
    '../test_project')

TEST_CLASS_SOURCE = '''class Employee(object):

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
        self.pay_rate = settings.BASE_PAY

    def full_name(self):
        return self.first_name + ' ' + self.last_name
'''

CLASS_BODY_SOURCE = '''
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
        self.pay_rate = settings.BASE_PAY

    def full_name(self):
        return self.first_name + ' ' + self.last_name
'''

VARIABLE_SOURCE = '''MULTILINE_SETTING = {
    'some_key': 42,
    'other_key': {


        'baz': 'quux'
    }


}
'''

VARIABLE_BODY_SOURCE = '''{
    'some_key': 42,
    'other_key': {


        'baz': 'quux'
    }


}
'''

def test_node_tree():
    '''Test that nodes are correctly created from source'''
    project = ProjectNode(TEST_PROJECT_PATH)

    assert_equal(len(project.children), 2)

    #brittle, might suggest that we need to refactor children into dicts
    package = project.children[0]
    root_module = project.children[1]

    nested_module = package.children[0]

    assert_is_instance(package, PackageNode)
    assert_is_instance(root_module, ModuleNode)
    assert_is_instance(nested_module, ModuleNode)

    module_var = root_module.children[1]
    class_node = nested_module.children[0]

    assert_is_instance(module_var, VariableNode)
    assert_is_instance(class_node, ClassNode)

    assert_equal(class_node.get_source_code(), TEST_CLASS_SOURCE)
    assert_equal(class_node.get_body_source_code(), CLASS_BODY_SOURCE)

    assert_equal(module_var.get_source_code(), VARIABLE_SOURCE)
    assert_equal(module_var.get_body_source_code(), VARIABLE_BODY_SOURCE)


