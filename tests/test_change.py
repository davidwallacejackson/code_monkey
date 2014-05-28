from os import path

from nose.tools import assert_equal

from code_monkey.change import Change

TEST_PROJECT_PATH = path.join(
    path.dirname(path.realpath(__file__)),
    '../test_project')

EXPECTED_PREVIEW = '''--- /Users/djackson/git/code_monkey/tests/../test_project/settings.py
+++ /Users/djackson/git/code_monkey/tests/../test_project/settings.py
@@ -1,3 +1,4 @@
+foobar
 ONE_LINER = 'foobar'
 
 MULTILINE_SETTING = {
'''

def test_str():
    change = Change(
        path.join(TEST_PROJECT_PATH, 'settings.py'),
        0,
        0,
        'foobar\n')

    assert_equal(str(change), EXPECTED_PREVIEW)