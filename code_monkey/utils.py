'''Utility functions used by other modules.'''
import difflib


class InvalidEditException(Exception):
    pass


class OverlapEditException(InvalidEditException):
    def __init__(self, path, conflicting_changes):
        error_message = "Changes overlap: \n"
        error_message += change_as_string(path, conflicting_changes[0])
        error_message += 'vs:\n'
        error_message += change_as_string(path, conflicting_changes[1])

        super(InvalidEditException, self).__init__(error_message)


def string_to_lines(input_string):
    '''return input_string as a list of individual line strings, each ending in
    a newline character.

    The output should be suitable for use with ChangeSet, so we throw an
    exception if input_string doesn't end in a newline.'''
    split_lines = input_string.split('\n')

    #strip the last element from split_lines, which should be an empty string
    split_lines = split_lines[:-1]


    output_lines = []

    #make a list of the lines with the newline characters added back in (split
    #strips them)
    for line in split_lines:
        output_lines.append(line + '\n')

    return output_lines


def lines_to_string(input_lines):
    '''return lines of source code as a single string'''

    return ''.join(input_lines)


def inject_at_line(source_lines, lines_to_inject, start_at):
    '''Return a copy of source_lines with lines_to_inject added in at index
    start_at. Lines in source_lines are not overwritten, but moved to accomodate
    the new content.'''

    output = source_lines[:start_at]
    output.extend(lines_to_inject)
    output.extend(source_lines[start_at:])

    return output


def get_changed_copy(old_lines, change):
    '''Return a copy of old_lines (a list of line strings) with change
    applied.'''

    starting_line, ending_line, new_lines = change

    transformed_lines = old_lines[:starting_line]
    transformed_lines.extend(new_lines)
    transformed_lines.extend(old_lines[(ending_line + 1):])

    return transformed_lines


def change_as_string(path, change):
    '''Return a string showing the lines affected by change in path, before and
    after the change is processed.

    change is a tuple of the format (starting_line, ending_line, new_lines)'''

    with open(path) as source_file:
        source_lines = source_file.readlines()
        transformed_lines = get_changed_copy(source_lines, change)

        diff = difflib.unified_diff(
            source_lines,
            transformed_lines,
            fromfile=path,
            tofile=path)

        output = ''

        for line in diff:
            output += line

        return output


def count_unterminated_in_source(text, start_char, term_char):
    '''Given a string text and substrings start_char and term_char, return the
    number of start_char without a matching term_char. Use, for instance, to
    find the number of unmatched parentheses in a source string.

    The current implementation has known issues: it can be fooled by end chars
    preceding start chars, and/or chars appearing inside string literals. TODO:
    Fix with a proper parsing solution. Better yet, look into the astroid bug
    that makes this necessary (see VariableNode.body_end_line)'''
    return text.count(start_char) - text.count(term_char)


def find_termination(lines, start_at, terminating_chars):
    '''Given a list of strings lines, an int starting_at, and a dict
    terminating_chars mapping strings to ints, return the line number by which
    we have seen each substring the number of times mapped to it in
    terminating_chars, starting at lines[start_at].

    Argh, that's a mouthful. In other words:

    find_termination(lines, 20, {')', 3}) starts at line 20, and looks for 3
    terminating parentheses, then gives you the line it's on when it find the
    last one.

    This has the same problems that count_unterminated_in_source mentions above.
    Also, it won't detect NEW start_chars in the lines and adjust
    terminating_chars accordingly. TODO: fix this whole system.'''

    remaining_count = reduce(lambda x, y: x+y, terminating_chars.values())
    if remaining_count <= 0:
        return None

    for index, line in enumerate(lines[start_at:]):
        for char in line:
            if char in terminating_chars.keys():
                terminating_chars[char] -= 1
                remaining_count = reduce(
                    lambda x, y: x+y, terminating_chars.values())
                if remaining_count <= 0:
                    return index + start_at

    return None
