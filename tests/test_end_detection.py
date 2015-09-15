from nose.tools import assert_equal, assert_raises

from code_monkey.end_detection import EndDetector, DetectorLockedError

def find_end_constant(source, start_from):
    detector = EndDetector(source)
    detector.discard_before(start_from)
    detector.consume_constant()
    detector.lock()

    return detector.get_end_index(detector.last_consumed)


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
    assert_equal(find_end_constant(' (          "42"   )   ', 1),
        len(' (          "42"   )'))


def test_locking():
    '''Test that we can't consume tokens after locking an EndDetector.'''
    detector = EndDetector('123 + 200')
    detector.consume_constant()
    detector.lock()

    with assert_raises(DetectorLockedError):
        detector.consume_anything()
