from os import path

from nose.tools import assert_equal

from code_monkey.node_query import project_query
from code_monkey.change import Change

TEST_PROJECT_PATH = path.join(
    path.dirname(path.realpath(__file__)),
    '../test_project')

EXPECTED_STR = '''--- {0}
+++ {0}
@@ -1,3 +1,4 @@
+foobar
 ONE_LINER = 'foobar'
 
 MULTILINE_SETTING = {{
'''

def test_str():
    change = Change(
        path.join(TEST_PROJECT_PATH, 'settings.py'),
        0,
        0,
        'foobar\n')

    expected = EXPECTED_STR.format(path.join(TEST_PROJECT_PATH, 'settings.py'))
    assert_equal(str(change), expected)


def test_change_value():
    '''Test that we can take a AssignmentNode and overwrite its current body with
    code generated from a new python value.'''

    q = project_query(TEST_PROJECT_PATH)

    setting_node = q.flatten().path_contains('MULTILINE_SETTING')[0]

    change = setting_node.change.value(42)
    assert_equal(change.new_text, '42')

    change = setting_node.change.value([42])
    assert_equal(change.new_text, '[\n    42\n]')
