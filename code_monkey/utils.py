'''Utility functions used by other modules.'''
import os

class InvalidEditException(Exception):
    pass


class OverlapEditException(InvalidEditException):
    def __init__(self, path, conflicting_changes):
        error_message = "Changes overlap: \n"
        error_message += str(conflicting_changes[0])
        error_message += 'vs:\n'
        error_message += str(conflicting_changes[1])

        super(InvalidEditException, self).__init__(error_message)


class TerminationNotFoundException(Exception):
    def __init__(self, lines, start_column, start_line, terminating_char):
        error_message = "terminating character {} was not found\n".format(
            terminating_char)
        error_message += "scan started at {}, {} in source: {}".format(
            start_column,
            start_line,
            ''.join(lines))

        super(Exception, self).__init__(error_message)


#snippet from: http://stackoverflow.com/questions/1151658/python-hashable-dicts
class hashabledict(dict):
  def __key(self):
    return tuple((k,self[k]) for k in sorted(self))
  def __hash__(self):
    return hash(self.__key())
  def __eq__(self, other):
    return self.__key() == other.__key()

def get_modules(fs_path):
    '''Find all Python modules in fs_path. Returns a list of tuples of the form:
    (full_path, is_package)'''

    modules = []

    for filename in os.listdir(fs_path):

        full_path = os.path.join(fs_path, filename)

        if os.path.isdir(full_path) and '__init__.py' in os.listdir(full_path):
            #directories with an __init__.py file are Python packages
            modules.append((full_path, True))

        elif filename.endswith('.py'):
            #files ending in .py are assumed to be Python modules
            modules.append((full_path, False))

    return modules


def findnth(haystack, needle, n):
    #snippet from: http://stackoverflow.com/questions/1883980/find-the-nth-occurrence-of-substring-in-a-string
    parts = haystack.split(needle, n+1)
    if len(parts) <= (n + 1):
        return - 1
    return len(haystack)-len(parts[-1])-len(needle)


def line_column_to_absolute_index(text, line, column):
    '''Given line and column numbers (0-indexed) for a string text, return the
    corresponding index in the entire string.'''

    if line < 0:
        raise ValueError("Negative line index {} is invalid.".format(
            line))

    total_lines = text.count('\n')

    if line > total_lines:
        raise ValueError(
            "Asked for line {} (0-indexed), but string has only {} lines".format(
                line, total_lines + 1))


    if line == 0:
        line_start_index = 0
    else:
        #finding the nth newline gets you the position before the first column
        #of a line -- we actually want the first column of the line to be
        #"column 0"
        line_start_index = findnth(text, '\n', line - 1) + 1

    return line_start_index + column


def absolute_index_to_line_column(text, index):
    '''Given an index in a string text, return the corresponding 0-indexed line
    and column numbers.'''

    start_through_index = text[0:(index+1)]
    lines = start_through_index.splitlines(True)
    line_index = len(lines) - 1

    target_line = lines[-1]

    #target_line has already been clipped to end at index
    column = len(target_line) - 1

    return (line_index, column)


def find_termination(lines, start_line, start_column, terminating_char):
    '''Walk back through lines starting from start_line, start_column, and
    return the index at which terminating_char first appears, disregarding
    anything on a line that is part of a comment. Again, the scan is BACKWARDS
    -- so the result will be before start_line, start_column in the source file.

    Raises an exception if the terminating_char is not found.

    The intended use is to find the end of a construct whose bounds are not
    necessaily determined by the placement of its children -- anything inside
    parentheses or brackets, where Python disregards whitespace.'''

    #the last line to scan (remember, backwards!)
    file_line_limit = 0

    lines_to_scan = lines[file_line_limit:(start_line + 1)]

    #trim the last line so that we don't include any of the sibling
    lines_to_scan[-1] = lines_to_scan[-1][0:start_column+1]

    #scan through the lines in reverse order, looking for the end of the node

    #len(lines_to_scan) - (line_index + 1) is the index of a line in
    #lines_to_scan -- basically, it takes us from the 'reversed' indices that we
    #get in line_index back to real, from-the-beginning indices
    for line_index, line in enumerate(reversed(lines_to_scan)):

        #remove comments from line
        if '#' in line:
            line = line[0:line.find('#')]

        for char_index, char in enumerate(reversed(line)):
            if char == terminating_char:
                line_index_in_file = file_line_limit + \
                    len(lines_to_scan) - (line_index + 1)
                char_index_in_line = len(line) - char_index
                return line_column_to_absolute_index(
                    ''.join(lines),
                    line_index_in_file,
                    char_index_in_line)

    #we didn't find anything!
    raise TerminationNotFoundException(
        lines,
        start_line,
        start_column,
        terminating_char)

def safe_docstring(input):
    '''Takes a docstring input, and returns a version with all ':' characters
    replaced with ' '.

    ':' characters will confuse the method we use to scan for the beginning of a
    class or function body (basically, looking backwards from the first element
    until we find the ':' from the signature), which is why we do this.

    It's safe to sub in safe_docstring for docstring in a copy of the source,
    because even if the docstring text appears elsewhere in the file, the
    scanner won't hit it, and it will take up the same number of characters.

    We could fool this by have a docstring whose text appears at the end of the
    signature as well. Hopefully, that's a rare case, but: TODO: fix that.'''

    return input.replace(':', ' ')

def count_lines(text):
    '''Return the number of lines in text.'''
    return text.count('\n')
