'''Utility functions used by other modules.'''


class InvalidEditException(Exception):
    pass


class OverlapEditException(InvalidEditException):
    def __init__(path, conflicting_changes):
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

    if not split_lines[-1] == '':
        raise InvalidEditException(
            'input_string must end in a newline character')

    #strip the last element from split_lines, which should be an empty string
    split_lines = split_lines[:-1]


    output_lines = []

    #make a list of the lines with the newline characters added back in (split
    #strips them)
    for line in split_lines:
        output_lines.append(line + '\n')

    return output_lines
