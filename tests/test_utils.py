from os import path

from nose.tools import assert_equal, assert_is_instance

from code_monkey.utils import line_column_to_absolute_index

TEST_PROJECT_PATH = path.join(
    path.dirname(path.realpath(__file__)),
    '../test_project')

def test_line_column_to_absolute_index():
    '''Test that we correctly convert from a line/column position in a block of
    text to a character index.'''

    with open(path.join(TEST_PROJECT_PATH, 'settings.py')) as source_file:

        source = source_file.read()

        assert_equal(
            line_column_to_absolute_index(source, 0, 0),
            0)

        assert_equal(
            line_column_to_absolute_index(source, 1, 0),
            21)
