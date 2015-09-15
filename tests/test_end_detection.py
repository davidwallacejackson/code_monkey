from nose.tools import assert_equal

from code_monkey.end_detection import EndDetector

def test_constant():
    '''Test that find_end_constant finds the end of the first Python constant
    in a string, and ignores everything else.'''

    assert_equal(EndDetector('150.01\n').find_end_constant(0), len('150.01'))
    assert_equal(EndDetector('False\n').find_end_constant(0), len('False'))
    assert_equal(EndDetector("'''multi\nline\ntext\n'''\n").find_end_constant(0),
        len("'''multi\nline\ntext\n'''"))

    assert_equal(EndDetector('42 + 3\n').find_end_constant(0), 2)

    assert_equal(EndDetector('my_func(42, "foobar")\n').find_end_constant(8), 10)

    assert_equal(EndDetector('(42)').find_end_constant(0), len('(42)'))
    assert_equal(EndDetector(' (          "42"   )   ').find_end_constant(1),
        len(' (          "42"   )'))
