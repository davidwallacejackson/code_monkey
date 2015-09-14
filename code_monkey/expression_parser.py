import token
import tokenize
from StringIO import StringIO

from code_monkey.utils import line_column_to_absolute_index

UNMATCHED = "'{}' without matching {} in {}"

CONSTANT_TOKENS = [
    token.NUMBER,
    token.STRING
]

#a constant can be a token.NAME, but only if it's one of these:
CONSTANT_NAMES = [
    'True',
    'False',
    'None'
]

WHITESPACE_TOKENS = [
    token.INDENT,
    token.NEWLINE
]

class ParseError(Exception):
    pass

def find_end_constant(source, start_from):
    '''Return the index of the character *after* the first Python constant
    found in source.

    All tokens beginning before index start_from will be ignored (this is
    necessary because the Python tokenizer won't work on certain incomplete
    lines, so we have to pass the *whole* line in and tokenize it).'''

    tokens = [
        {
            'type': token[0],
            'token': token[1],
            'start': token[2],
            'end': token[3],
        }
        for token in
        tokenize.generate_tokens(StringIO(source).readline)
    ]

    stack = []

    constant_found = False

    while tokens:
        token = tokens[0]
        tokens = tokens[1:]

        is_constant = (
            token['type'] in CONSTANT_TOKENS or
            token['token'] in CONSTANT_NAMES)

        start_index = line_column_to_absolute_index(
            source,
            token['start'][0] - 1,
            token['start'][1])

        if start_index < start_from:
            pass

        elif token['token'] == '(':
            stack.append(')')

        elif token['token'] == ')':
            popped = stack.pop()
            if not popped == ')':
                raise ParseError(UNMATCHED.format(')', '(', source))

        elif is_constant:
            constant_found = True

        elif token['type'] in WHITESPACE_TOKENS:
            pass

        if constant_found and not stack:
            return line_column_to_absolute_index(
                source,
                token['end'][0] - 1, # row is 1-indexed, so we offset it 
                token['end'][1])

    #if we made it through source without finding an ending, something's wrong
    raise ParseError("No constant found in: {}".format(source))
