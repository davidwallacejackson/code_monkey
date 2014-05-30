'''Utility functions used by other modules.'''


class InvalidEditException(Exception):
    pass


class OverlapEditException(InvalidEditException):
    def __init__(self, path, conflicting_changes):
        error_message = "Changes overlap: \n"
        error_message += str(conflicting_changes[0])
        error_message += 'vs:\n'
        error_message += str(conflicting_changes[1])

        super(InvalidEditException, self).__init__(error_message)


def findnth(haystack, needle, n):
    #snippet from: http://stackoverflow.com/questions/1883980/find-the-nth-occurrence-of-substring-in-a-string
    parts = haystack.split(needle, n+1)
    if len(parts) <= (n + 1):
        return - 1
    return len(haystack)-len(parts[-1])-len(needle)


def line_column_to_absolute_index(text, line, column):
    '''Given line and column numbers (0-indexed) for a string text, return the
    corresponding index in the entire string.'''

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
