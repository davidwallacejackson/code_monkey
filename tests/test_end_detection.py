from nose.tools import assert_equal, assert_raises

from code_monkey.end_detection import (
    EndDetector,
    DetectorLockedError,
    get_tokens)

def find_end(node_type, source, start_from=0, child_tokens={}):
    detector = EndDetector(source, child_tokens=child_tokens)
    detector.discard_before(start_from)
    getattr(detector, 'consume_' + node_type)()
    detector.lock()

    return detector.get_end_index(detector.last_consumed)


def test_constant():
    '''Test that find_end_constant finds the end of the first Python constant
    in a string, and ignores everything else.'''

    assert_equal(find_end('constant', '150.01\n'), len('150.01'))
    assert_equal(find_end('constant', 'False\n'), len('False'))
    assert_equal(find_end('constant', "'''multi\nline\ntext\n'''\n"),
        len("'''multi\nline\ntext\n'''"))

    assert_equal(find_end('constant', '42 + 3\n'), 2)

    assert_equal(find_end('constant', 'my_func(42, "foobar")\n', 8), 10)

    assert_equal(find_end('constant', '(42)'), len('(42)'))
    assert_equal(find_end('constant', ' (          "42"   )   ', 1),
        len(' (          "42"   )'))

    assert_equal(find_end('constant', '(\n42\n)\n'), len('(\n42\n)'))

def test_call():
    assert_equal(find_end('call', 'my_func()\n'), len('my_func()'))

    constant_token = get_tokens('my_func(42)\n')[2]
    assert_equal(
        find_end('call', 'my_func(42)\n', child_tokens=[constant_token]),
        len('my_func(42)'))

def test_name():
    assert_equal(find_end('name', 'some_var\n'), len('some_var'))

def test_locking():
    '''Test that we can't consume tokens after locking an EndDetector.'''
    detector = EndDetector('123 + 200')
    detector.consume_constant()
    detector.lock()

    with assert_raises(DetectorLockedError):
        detector.consume_anything()

