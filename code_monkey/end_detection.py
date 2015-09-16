import token as token_types
import tokenize
from StringIO import StringIO

from code_monkey.utils import line_column_to_absolute_index, hashabledict

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

def get_tokens(source):
    '''Return an array of token dicts in source.'''
    return [
        hashabledict({
            'type': token[0],
            'token': token[1],
            'start': (token[2][0] - 1, token[2][1]),
            'end': (token[3][0] - 1, token[3][1]),
        })
        for token in
        tokenize.generate_tokens(StringIO(source).readline)
    ]

def consume_parens(func):
    '''Wrap a method to consume any surrounding parens and enclosed whitespace.

    Any Python expression can be wrapped in parens without changing its meaning,
    so we need this all over the place.'''

    def wrapped(*args, **kwargs):
        self = args[0]

        par_count = 0

        while self.tokens[0]['token'] == '(':
            self.consume([], ['('])
            par_count += 1
            self.consume_many(WHITESPACE_TOKENS, ['\n'])

        func(*args, **kwargs)

        while par_count > 0:
            self.consume_many(WHITESPACE_TOKENS, ['\n'])
            self.consume([], [')'])
            par_count -= 1

            if len(self.tokens) == 0:
                raise ParseError(UNMATCHED.format('(', ')', self.source))

    return wrapped

class ParseError(Exception):
    pass

class DetectorLockedError(Exception):
    def __init__(self):
        super(DetectorLockedError, self).__init__(
            "This EndDetector is locked and cannot consume tokens.")

class EndDetector:

    def __init__(self, source, child_tokens=[]):
        self.source = source
        self.all_tokens = get_tokens(source)
        self.child_tokens = child_tokens

        self.tokens = filter(
            lambda token: token not in self.child_tokens,
            self.all_tokens)

        self.consumed = []
        self.locked = False


    @property
    def last_consumed(self):
        return self.consumed[-1]

    def lock(self):
        '''Lock this EndDetector, preventing it from consuming any more tokens.
        
        This is just a little extra safety, since we're going to generate these
        things and pass them around -- we don't want people changing their state
        unexpectedly.'''
        self.locked = True

    def get_end_index(self, token):
        '''Return the absolute index of the end of token in self.source.''' 
        return line_column_to_absolute_index(
            self.source,
            token['end'][0],
            token['end'][1])

    def consume_anything(self, discard=False):
        '''Consume the first token, no matter what it is.

        If discard == True, the token will **not** be added to the record of
        consumed tokens. Use this for tokens that shouldn't be considered 'part'
        of the node, but we have to skip past anyway.'''

        if self.locked:
            raise DetectorLockedError()

        if not discard:
            self.consumed.append(self.tokens[0])

        self.tokens = self.tokens[1:]


    def consume(self, types, matches=[]):
        '''Consume the first token if it's either of a type in types, or
        exactly matches a string in matches. Otherwise, raise an error.'''

        token = self.tokens[0]

        if not (token['type'] in types or token['token'] in matches):
            raise ParseError("Expected type {} or match {}, but got {}".format(
                types,
                matches,
                token))

        self.consume_anything()


    def consume_many(self, types, matches=[]):
        '''Consume any leading tokens indicated by types or matches. Return the
        number of tokens consumed.'''

        count = 0
        token = self.tokens[0]

        while token['type'] in types or token['token'] in matches:
            self.consume(types, matches)

            token = self.tokens[0]
            count += 1

        return count

    def consume_many_not(self, types, matches):
        '''As consume_many, but only consumes tokens that *don't* fit a
        specified type or match string.'''
        count = 0
        token = self.tokens[0]

        while not token['type'] in types and not token['token'] in matches:
            self.consume_anything()

            token = self.tokens[0]
            count += 1

        return count


    def discard_before(self, start_from):
        '''Discard any tokens starting at an index before start_from. Return the
        number of tokens discarded.'''

        count = 0
        token = self.tokens[0]

        while line_column_to_absolute_index(
                self.source,
                token['start'][0],
                token['start'][1]) < start_from:

            self.consume_anything(discard=True)
            
            token = self.tokens[0]
            count += 1

        return count


    @consume_parens
    def consume_constant(self):
        '''Consume the next Python constant found in source.

        All tokens beginning before index start_from will be ignored (this is
        necessary because the Python tokenizer won't work on certain incomplete
        lines, so we have to pass the *whole* line in and tokenize it).'''

        self.consume(CONSTANT_TOKENS, CONSTANT_NAMES)

    @consume_parens
    def consume_name(self):
        '''Consume the next name found in source.'''
        self.consume([token_types.NAME])

    @consume_parens
    def consume_call(self):
        '''Consume the next function call in source.'''
        self.consume([token_types.NAME])
        self.consume_many(WHITESPACE_TOKENS)
        self.consume([], ['('])
        self.consume_many(WHITESPACE_TOKENS)
        self.consume([], [')'])
