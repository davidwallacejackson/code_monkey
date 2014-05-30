from nose.tools import assert_equal

from code_monkey.format import (
    format_dict,
    format_list,
    format_literal,
    format_value,
    format_tuple)


EXPECTED_LIST = '''[
    3,
    4,
    5
]'''

EXPECTED_TUPLE = '''(
    'foo/bar/baz.quux',
    True
)'''

EXPECTED_DICT = '''{
    'a': 42,
    'b': False
}'''

EXPECTED_NESTED = '''(
    True,
    (
        3,
        4
    )
)'''

def test_literal():
    assert_equal(format_value(3), '3')
    assert_equal(format_value(True), 'True')
    assert_equal(format_value('foo'), "'foo'")


def test_list():
    assert_equal(format_value([3, 4, 5]), EXPECTED_LIST)


def test_tuple():
    assert_equal(format_value(('foo/bar/baz.quux', True)), EXPECTED_TUPLE)


def test_dict():
    assert_equal(format_value({'a':42, 'b':False}), EXPECTED_DICT)


def test_nested():
    assert_equal(format_value((True, (3, 4))), EXPECTED_NESTED)
