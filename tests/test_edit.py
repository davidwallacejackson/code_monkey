'''Test changesets, diffs, and committing changes.'''
from os import path
from shutil import copytree, rmtree

from nose.tools import (
    assert_equal,
    assert_is_instance,
    assert_raises,
    with_setup)

from code_monkey.change import Change
from code_monkey.node import ProjectNode
from code_monkey.edit import ChangeSet
from code_monkey.utils import OverlapEditException

TEST_PROJECT_PATH = path.join(
    path.dirname(path.realpath(__file__)),
    '../test_project')

COPY_PATH = path.join(
    path.dirname(path.realpath(__file__)),
    '../test_project__copy')

RESOURCES_PATH = path.join(
    path.dirname(path.realpath(__file__)),
    'resources')

EXPECTED_DIFF_SINGLE = '''Changes:

--- {0}
+++ {0}
@@ -19,6 +19,9 @@
         self.is_up = False
         self.can_work = False
 
+    def like_tab_and_mountain_dew(self):
+        return True
+
     things_code_monkey_like = [
         'fritos',
         'tab',
'''

EXPECTED_DIFF_STACKED = '''Changes:

--- {0}
+++ {0}
@@ -2,6 +2,8 @@
 from test_project import settings
 
 class Employee(object):
+
+    FIRST_INJECTED_VALUE = \'foo\'
 
     def __init__(self, first_name, last_name):
         self.first_name = first_name
@@ -14,6 +16,10 @@
 
 class CodeMonkey(Employee):
     """He writes code."""
+
+    SECOND_INJECTED_VALUE = [
+        'bar'
+    ]
     def __init__(self, *args, **kwargs):
         super(CodeMonkey, self).__init__(*args, **kwargs)
         self.is_up = False
'''

def setup_func():
    #create a copy of the test_project folder
    try:
        copytree(TEST_PROJECT_PATH, COPY_PATH)
    except OSError:
        #if it's already there, delete it and re-copy
        rmtree(COPY_PATH)
        copytree(TEST_PROJECT_PATH, COPY_PATH)


def teardown_func():
    #remove the copied test_project folder
    rmtree(COPY_PATH)


#the decorator ensures that the setup/teardown happens for each test
#we could also do this by making a test class with setUp/tearDown
@with_setup(setup_func, teardown_func)
def test_single_edit_to_file():
    '''Test that we can make a single change to a single file.'''
    project = ProjectNode(COPY_PATH)
    package = project.children['lib']
    nested_module = package.children['employee']

    code_monkey_class = nested_module.children['CodeMonkey']

    inject_source = \
        "\n    def like_tab_and_mountain_dew(self):\n        return True\n"

    changeset = ChangeSet()
    change = code_monkey_class.change.inject_at_line(
        6, inject_source)

    changeset.add_changes([change])

    #check that diffs work as expected
    expected = EXPECTED_DIFF_SINGLE.format(code_monkey_class.fs_path)
    assert_equal(changeset.diff(), expected)

    changeset.commit()

    expected_file_path = path.join(RESOURCES_PATH, 'single_edit_expected')

    #check that the edit worked properly
    with open(code_monkey_class.fs_path) as modified_file:
        with open(expected_file_path) as expected_file:
            modified_source = modified_file.read()
            expected_source = expected_file.read()

            assert_equal(modified_source, expected_source)

@with_setup(setup_func, teardown_func)
def test_stacked_edits_to_file():
    '''Test that we can make multiple consecutive edits to a file in one
    ChangeSet.'''
    project = ProjectNode(COPY_PATH)

    employee_module = project.children['lib'].children['employee']
    employee_class = employee_module.children['Employee']
    code_monkey_class = employee_module.children['CodeMonkey']

    #we'll do the Employee with an inject_at_line directly, and CodeMonkey with
    #an inject_assignment, to get broader coverage

    employee_inject_source = "\n    FIRST_INJECTED_VALUE = 'foo'\n"

    change = employee_class.change.inject_at_line(
        1,
        employee_inject_source)

    second_change = code_monkey_class.change.inject_assignment(
        '    ',
        'SECOND_INJECTED_VALUE',
        ['bar'],
        line_index=1)

    changeset = ChangeSet()
    changeset.add_changes([change, second_change])

    #check that diffs work as expected
    expected = EXPECTED_DIFF_STACKED.format(employee_module.fs_path)
    assert_equal(changeset.diff(), expected)

    changeset.commit()

    expected_file_path = path.join(RESOURCES_PATH, 'stacked_edit_expected')

    #check that the edit worked properly
    with open(employee_module.fs_path) as modified_file:
        with open(expected_file_path) as expected_file:
            modified_source = modified_file.read()
            expected_source = expected_file.read()

            assert_equal(modified_source, expected_source)


def test_conflicting_changes():
    '''Test that ChangeSet raises an exception if we give it two overlapping
    changes.

    Does not write any changes to filesystem, so it doesn't need a fresh copy of
    the test project.'''

    settings_path = path.join(TEST_PROJECT_PATH, 'settings.py')

    change = Change(
        settings_path,
        0,
        10,
        'some_newtext')

    second_change = Change(
        settings_path,
        5,
        15,
        'more_newtext')

    with assert_raises(OverlapEditException):
        ChangeSet([change, second_change])
