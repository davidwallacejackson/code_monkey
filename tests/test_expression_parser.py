from nose.tools import assert_equal

from code_monkey.expression_parser import find_end_constant

def test_constant():
    '''Test that find_end_constant finds the end of the first Python constant
    in a string, and ignores everything else.'''

    assert_equal(find_end_constant('150.01\n', 0), len('150.01'))
    assert_equal(find_end_constant('False\n', 0), len('False'))
    assert_equal(find_end_constant("'''multi\nline\ntext\n'''\n", 0),
        len("'''multi\nline\ntext\n'''"))

    assert_equal(find_end_constant('42 + 3\n', 0), 2)

    assert_equal(find_end_constant('my_func(42, "foobar")\n', 8), 10)

    assert_equal(find_end_constant('(42)', 0), len('(42)'))
    assert_equal(find_end_constant(' (          "42"   )   ', 0),
        len(' (          "42"   )'))
