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

def test_preview():
    project = ProjectNode(TEST_PROJECT_PATH)

    #brittle, might suggest that we need to refactor children into dicts
    package = project.children[0]

    nested_module = package.children[0]

    code_monkey_class = nested_module.children[1]

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
    
    expected = EXPECTED_PREVIEW.format(code_monkey_class.fs_path)
    assert_equal(changeset.preview(), expected)

