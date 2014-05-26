'''Test changesets, previews, and committing changes.'''
from os import path
from shutil import copytree, rmtree

from nose.tools import assert_equal, assert_is_instance

from code_monkey.node import ProjectNode
from code_monkey.edit import ChangeSet
from code_monkey.utils import inject_at_line, lines_to_string, string_to_lines

TEST_PROJECT_PATH = path.join(
    path.dirname(path.realpath(__file__)),
    '../test_project')

COPY_PATH = path.join(
    path.dirname(path.realpath(__file__)),
    '../test_project__copy')

RESOURCES_PATH = path.join(
    path.dirname(path.realpath(__file__)),
    'resources')

EXPECTED_PREVIEW_SINGLE = '''Changes:

--- {0}
+++ {0}
@@ -19,6 +19,9 @@
         self.is_up = False
         self.can_work = False
 
+    def like_tab_and_mountain_dew(self):
+        return True
+
     def get_up(self):
         self.is_up = True
 
'''

EXPECTED_PREVIEW_STACKED = '''Changes:

--- {0}
+++ {0}
@@ -2,6 +2,8 @@
 from test_project import settings
 
 class Employee(object):
+
+    FIRST_INJECTED_VALUE = 'foo'
 
     def __init__(self, first_name, last_name):
         self.first_name = first_name
--- {0}
+++ {0}
@@ -13,6 +13,8 @@
 
 
 class CodeMonkey(Employee):
+
+    SECOND_INJECTED_VALUE = ['bar']
     """He writes code."""
     def __init__(self, *args, **kwargs):
         super(CodeMonkey, self).__init__(*args, **kwargs)
'''

def setUp():
    #create a copy of the test_project folder
    try:
        copytree(TEST_PROJECT_PATH, COPY_PATH)
    except OSError:
        #if it's already there, delete it and re-copy
        rmtree(COPY_PATH)
        copytree(TEST_PROJECT_PATH, COPY_PATH)


def tearDown():
    #remove the copied test_project folder
    rmtree(COPY_PATH)

def test_single_edit_to_file():
    '''Test that we can make a single change to a single file.'''
    project = ProjectNode(COPY_PATH)

    package = project.children['lib']

    nested_module = package.children['employee']

    code_monkey_class = nested_module.children['CodeMonkey']

    source = code_monkey_class.get_source_code()
    source_lines = string_to_lines(source)

    inject_source = \
        "\n    def like_tab_and_mountain_dew(self):\n        return True\n"
    inject_lines = string_to_lines(inject_source)

    new_source_lines = inject_at_line(
        source_lines,
        inject_lines,
        6)
    new_source = lines_to_string(new_source_lines)

    changeset = ChangeSet()
    change = code_monkey_class.generate_change(new_source)

    changeset.add_changes({
        code_monkey_class.fs_path: [change]})
    
    #check that previews work as expected
    expected = EXPECTED_PREVIEW_SINGLE.format(code_monkey_class.fs_path)
    assert_equal(changeset.preview(), expected)

    changeset.commit()

    expected_file_path = path.join(RESOURCES_PATH, 'single_edit_expected')

    #check that the edit worked properly
    with open(code_monkey_class.fs_path) as modified_file:
        with open(expected_file_path) as expected_file:
            modified_source = modified_file.read()
            expected_source = expected_file.read()

            assert_equal(modified_source, expected_source)


def test_stacked_edits_to_file():
    '''Test that we can make multiple consecutive edits to a file in one
    ChangeSet.'''
    project = ProjectNode(COPY_PATH)

    employee_module = project.children['lib'].children['employee']
    employee_class = employee_module.children['Employee']
    code_monkey_class = employee_module.children['CodeMonkey']

    employee_source = employee_class.get_source_code()
    employee_lines = string_to_lines(employee_source)

    code_monkey_source = code_monkey_class.get_source_code()
    code_monkey_lines = string_to_lines(code_monkey_source)

    employee_inject_source = "\n    FIRST_INJECTED_VALUE = 'foo'\n"
    employee_inject_lines = string_to_lines(employee_inject_source)

    code_monkey_inject_source = "\n    SECOND_INJECTED_VALUE = ['bar']\n"
    code_monkey_inject_lines = string_to_lines(code_monkey_inject_source)

    new_source_lines = inject_at_line(
        employee_lines,
        employee_inject_lines,
        1)
    new_source = lines_to_string(new_source_lines)

    second_new_source_lines = inject_at_line(
        code_monkey_lines,
        code_monkey_inject_lines,
        1)
    second_new_source = lines_to_string(second_new_source_lines)


    changeset = ChangeSet()
    change = employee_class.generate_change(new_source)
    second_change = code_monkey_class.generate_change(second_new_source)

    changeset.add_changes({
        employee_module.fs_path: [change, second_change]})
    
    #check that previews work as expected
    expected = EXPECTED_PREVIEW_STACKED.format(employee_module.fs_path)
    assert_equal(changeset.preview(), expected)

    changeset.commit()

    expected_file_path = path.join(RESOURCES_PATH, 'stacked_edit_expected')

    #check that the edit worked properly
    with open(employee_module.fs_path) as modified_file:
        with open(expected_file_path) as expected_file:
            modified_source = modified_file.read()
            expected_source = expected_file.read()

            assert_equal(modified_source, expected_source)

