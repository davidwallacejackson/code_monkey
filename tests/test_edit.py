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

EXPECTED_PREVIEW = '''Changes:

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
    expected = EXPECTED_PREVIEW.format(code_monkey_class.fs_path)
    assert_equal(changeset.preview(), expected)

    changeset.commit()

    expected_file_path = path.join(RESOURCES_PATH, 'single_edit_expected')

    #check that the edit worked properly
    with open(code_monkey_class.fs_path) as modified_file:
        with open(expected_file_path) as expected_file:
            modified_source = modified_file.read()
            expected_source = expected_file.read()

            assert_equal(modified_source, expected_source)
