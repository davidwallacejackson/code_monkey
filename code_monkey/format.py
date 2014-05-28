'''Tools for formatting source code to insert into a file.'''

#the string to add to create a single level of indentation
INDENTATION_LEVEL = '    '


def format_source(format_me, starting_indentation='', indent_first_line=False):
    '''Turn format_me into a string suitable for insertion into a source file.
    format_me can be a string, number, boolean, list, tuple, or dictionary.'''

    if isinstance(format_me, list):
        return format_list(
            format_me,
            starting_indentation,
            indent_first_line)

    if isinstance(format_me, tuple):
        return format_tuple(
            format_me,
            starting_indentation,
            indent_first_line)

    if isinstance(format_me, dict):
        return format_dict(
            format_me,
            starting_indentation,
            indent_first_line)

    if isinstance(format_me, (int, float, str, bool)):
        return format_literal(
            format_me,
            starting_indentation,
            indent_first_line)


def format_literal(format_me, starting_indentation='', indent_first_line=False):
    output = ''

    if indent_first_line:
        output += starting_indentation

    output += repr(format_me)

    return output


def format_list(format_me, starting_indentation='', indent_first_line=False):
    output = ''

    if indent_first_line:
        output += starting_indentation

    output += '[\n'

    scope_indentation = starting_indentation + INDENTATION_LEVEL

    #each element gets its own line
    for element in format_me:
        output +=  format_source(
            element,
            starting_indentation=scope_indentation,
            indent_first_line=True)
        output += ',\n'


    output += starting_indentation + ']'

    return output


def format_tuple(format_me, starting_indentation='', indent_first_line=False):
    output = ''

    if indent_first_line:
        output += starting_indentation

    output += '(\n'

    scope_indentation = starting_indentation + INDENTATION_LEVEL

    #each element gets its own line
    for element in format_me:
        output +=  format_source(
            element,
            starting_indentation=scope_indentation,
            indent_first_line=True)
        output += ',\n'


    output += starting_indentation + ')'

    return output


def format_dict(format_me, starting_indentation='', indent_first_line=False):
    output = ''

    if indent_first_line:
        output += starting_indentation

    output += '{\n'

    scope_indentation = starting_indentation + INDENTATION_LEVEL

    #each element gets its own line
    for key, value in format_me.items():
        output +=  format_source(
            key,
            starting_indentation=scope_indentation,
            indent_first_line=True)
        output += ': '
        output += format_source(
            value,
            starting_indentation=scope_indentation,
            indent_first_line=False)
        output += ',\n'


    output += starting_indentation + '}'

    return output
