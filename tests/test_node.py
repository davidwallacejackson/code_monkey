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

VARIABLE_VALUE = {
    'some_key': 42,
    'other_key': {
        'baz': 'quux'
    }
}


def test_node_tree():
    '''Test that nodes are correctly created from source'''
    project = ProjectNode(TEST_PROJECT_PATH)

    assert_equal(len(project.children), 2)

    package = project.children['lib']
    root_module = project.children['settings']

    nested_module = package.children['employee']

    assert_is_instance(package, PackageNode)
    assert_is_instance(root_module, ModuleNode)
    assert_is_instance(nested_module, ModuleNode)

    module_var = root_module.children['MULTILINE_SETTING']
    class_node = nested_module.children['Employee']

    assert_is_instance(module_var, VariableNode)
    assert_is_instance(class_node, ClassNode)

    assert_equal(class_node.get_source(), TEST_CLASS_SOURCE)
    assert_equal(class_node.get_body_source(), CLASS_BODY_SOURCE)

    assert_equal(module_var.get_source(), VARIABLE_SOURCE)
    assert_equal(module_var.get_body_source(), VARIABLE_BODY_SOURCE)

    assert_equal(module_var.eval_body(), VARIABLE_VALUE)
