import token as token_types
import tokenize
from StringIO import StringIO

from code_monkey.utils import line_column_to_absolute_index

UNMATCHED = "'{}' without matching {} in {}"

CONSTANT_TOKENS = [
    token_types.NUMBER,
    token_types.STRING
]

#a constant can be a token_types.NAME, but only if it's one of these:
CONSTANT_NAMES = [
    'True',
    'False',
    'None'
]

WHITESPACE_TOKENS = [
    token_types.INDENT,
    token_types.NEWLINE
]

BIN_OP_TOKENS = [
    token_types.PLUS,
    token_types.MINUS,
    token_types.STAR,
    token_types.SLASH,
    token_types.VBAR,
    token_types.AMPER,
    token_types.LESS,
    token_types.GREATER,
    token_types.EQUAL,
    token_types.DOT,
    token_types.PERCENT,
    token_types.EQEQUAL,
    token_types.NOTEQUAL,
    token_types.LESSEQUAL,
    token_types.GREATEREQUAL,
    token_types.CIRCUMFLEX,
    token_types.LEFTSHIFT,
    token_types.RIGHTSHIFT,
    token_types.DOUBLESTAR,
    token_types.PLUSEQUAL,
    token_types.MINEQUAL,
    token_types.STAREQUAL,
    token_types.SLASHEQUAL,
    token_types.PERCENTEQUAL,
    token_types.AMPEREQUAL,
    token_types.VBAREQUAL,
    token_types.CIRCUMFLEXEQUAL,
    token_types.LEFTSHIFTEQUAL,
    token_types.RIGHTSHIFTEQUAL,
    token_types.DOUBLESTAREQUAL,
    token_types.DOUBLESLASH,
    token_types.DOUBLESLASHEQUAL,
]

class ParseError(Exception):
    pass

class EndDetector:

    def __init__(self, source):
        self.source = source
        self.last_consumed = None

    def consume_or_error(self, tokens, types, matches=[]):
        '''Return tokens[1:] if tokens[0] is either one of the types in types, or
        exactly matches a string in matches. Otherwise, raise an error.'''

        if not (tokens[0]['type'] in types or tokens[0]['token'] in matches):
            raise ParseError("Expected type {} or match {}, but got {}".format(
                types,
                matches,
                tokens[0]))

        self.last_consumed = tokens[0]
        return tokens[1:]


    def consume_zero_or_more(self, tokens, types, matches=[]):
        '''Consume any leading tokens indicated by types or matches. Return a tuple
        (count, tokens), where count is the number of tokens removed and tokens is
        the list of remaining tokens.'''

        index = 0

        while tokens[index]['type'] in types or tokens[index]['token'] in matches:
            self.last_consumed = tokens[index]
            index += 1

        return (index, tokens[index:])

    def consume_before(self, tokens, start_from):
        index = 0

        while line_column_to_absolute_index(
                self.source,
                tokens[index]['start'][0],
                tokens[index]['start'][1]) < start_from:
            self.last_consumed = tokens[index]
            index += 1

        return tokens[index:]


    def find_end_constant(self, start_from):
        '''Return the index of the character *after* the first Python constant
        found in source.

        All tokens beginning before index start_from will be ignored (this is
        necessary because the Python tokenizer won't work on certain incomplete
        lines, so we have to pass the *whole* line in and tokenize it).'''

        tokens = get_tokens(self.source)

        tokens = self.consume_before(tokens, start_from)

        lpar_count, tokens = self.consume_zero_or_more(
            tokens,
            [], ['('])

        # _, tokens = self.consume_zero_or_more(tokens, [token_types.INDENT])

        tokens = self.consume_or_error(tokens, CONSTANT_TOKENS, CONSTANT_NAMES)

        # _, tokens = self.consume_zero_or_more(tokens, [token_types.INDENT])

        rpar_count, tokens = self.consume_zero_or_more(
            tokens,
            [], [')'])

        if lpar_count > rpar_count:
            raise ParseError(UNMATCHED.format('(', ')', self.source))
        elif lpar_count < rpar_count:
            raise ParseError(UNMATCHED.format(')', '(', self.source))

        return line_column_to_absolute_index(
            self.source,
            self.last_consumed['end'][0],
            self.last_consumed['end'][1])



def get_tokens(source):
    '''Return an array of token dicts in source.'''
    return [
        {
            'type': token[0],
            'token': token[1],
            'start': (token[2][0] - 1, token[2][1]),
            'end': (token[3][0] - 1, token[3][1]),
        }
        for token in
        tokenize.generate_tokens(StringIO(source).readline)
    ]


# def find_end_constant(source, start_from):
#     '''Return the index of the character *after* the first Python constant
#     found in source.

#     All tokens beginning before index start_from will be ignored (this is
#     necessary because the Python tokenizer won't work on certain incomplete
#     lines, so we have to pass the *whole* line in and tokenize it).'''

#     tokens = get_tokens(source)

#     lpar_count, tokens = consume_zero_or_more(
#         tokens,
#         [token_types.LPAR])

#     tokens = consume_or_error(tokens, CONSTANT_TOKENS, CONSTANT_NAMES)

#     rpar_count, tokens = consume_zero_or_more(
#         tokens,
#         [token_types.RPAR])

#     if lpar_count > rpar_count:
#         raise ParseError(UNMATCHED.format('(', ')', source))
#     elif lpar_count < rpar_count:
#         raise ParseError(UNMATCHED.format(')', '(', source))

#     return line_column_to_absolute_index(
#         source,
#         tokens[0]['start'][0] - 1,
#         tokens[0]['start'][1])

#     # stack = []

#     # constant_found = False

#     # while tokens:
#     #     token = tokens[0]
#     #     tokens = tokens[1:]

#     #     is_constant = (
#     #         token['type'] in CONSTANT_TOKENS or
#     #         token['token'] in CONSTANT_NAMES)

#     #     start_index = line_column_to_absolute_index(
#     #         source,
#     #         token['start'][0] - 1,
#     #         token['start'][1])

#     #     if start_index < start_from:
#     #         pass

#     #     elif token['token'] == '(':
#     #         stack.append(')')

#     #     elif token['token'] == ')':
#     #         popped = stack.pop()
#     #         if not popped == ')':
#     #             raise ParseError(UNMATCHED.format(')', '(', source))

#     #     elif is_constant:
#     #         constant_found = True

#     #     elif token['type'] in WHITESPACE_TOKENS:
#     #         pass

#     #     if constant_found and not stack:
#     #         return line_column_to_absolute_index(
#     #             source,
#     #             token['end'][0] - 1, # row is 1-indexed, so we offset it 
#     #             token['end'][1])

#     # #if we made it through source without finding an ending, something's wrong
#     # raise ParseError("No constant found in: {}".format(source))

# def consume_or_error(tokens, types, matches=[]):
#     '''Return tokens[1:] if tokens[0] is either one of the types in types, or
#     exactly matches a string in matches. Otherwise, raise an error.'''

#     if not (tokens[0]['type'] in types or tokens[0]['token'] in matches):
#         raise ParseError("Expected type {} or match {}, but got {}".format(
#             types,
#             matches,
#             tokens[0]))

#     return tokens[1:]


# def consume_zero_or_more(tokens, types, matches=[]):
#     '''Consume any leading tokens indicated by types or matches. Return a tuple
#     (count, tokens), where count is the number of tokens removed and tokens is
#     the list of remaining tokens.'''

#     index = 0

#     while tokens[index]['type'] in types or tokens[index]['token'] in matches:
#         index += 1

#     return (index, tokens[index:])


# def find_end_call(source, start_at):

#     tokens = get_tokens(source)

#     tokens = consume_or_error(
#         tokens,
#         [token_types.NAME])

#     tokens = consume_zero_or_more(
#         tokens,
#         [token_types.INDENT])

#     tokens = consume_or_error(
#         tokens,
#         [token_types.LPAR])



