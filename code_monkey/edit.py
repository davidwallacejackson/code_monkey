'''Tools for editing source files.'''
from operator import itemgetter

from code_monkey.utils import (
    get_changed_copy,
    OverlapEditException)


def ranges_overlap(first_range, second_range):
    '''Return whether first_range and second_range overlap. Each range is a
    tuple of the form (start_index, end_index). Used for preventing overlapping
    changes.'''

    first_start, first_end = first_range
    second_start, second_end = second_range

    if first_start >= second_start and first_start <= second_end:
        return True

    if first_end >= second_start and first_end <= second_end:
        return True

    if second_start >= first_start and second_start <= first_end:
        return True

    if second_end >= first_start and second_end <= first_end:
        return True

    return False


def change_as_string(path, change):
    '''Return a string showing the lines affected by change in path, before and
    after the change is processed.

    change is a tuple of the format (starting_line, ending_line, new_lines)'''

    starting_line, ending_line, new_lines = change

    with open(path) as source_file:
        source_lines = source_file.readlines()
        output = 'In file: {}:\n'.format(path)

        output += 'Before:\n'
        output += ''.join(source_lines[starting_line:(ending_line+1)]) + '\n'

        output += 'After:\n'
        output += ''.join(new_lines) + '\n'

        return output




class ChangeSet(object):
    '''A set of individual changes to make to various files. Can be previewed or
    committed.'''

    def __init__(self, changes={}):
        self.changes = {}
        self.add_changes(changes)

    def add_changes(self, changes):
        #changes is a dict of the format:
        #    'file_path': [
        #       (starting_line, ending_line, new_lines),
        #    ]
        #
        #make sure to convert the new source into lists of strings before
        #passing it in

        for path, file_changes in changes.items():
            if not path in self.changes.keys():
                self.changes[path] = []

            for new_change in file_changes:
                for old_change in self.changes[path]:
                    #check that our new change does not conflict (overlap) with
                    #existing changes

                    if ranges_overlap(
                            (old_change[0], old_change[1]),
                            (new_change[0], new_change[1])):
                        #changes in the same file are not allowed to touch the
                        #same lines
                        raise OverlapEditException(
                            path,
                            (old_change, new_change))

                self.changes[path].append(new_change)

    def preview(self):
        '''Get a human-readable preview of all the changes to the source
        encompassed by this ChangeSet.

        TODO: make the change descriptions smaller, probably using difflib.'''

        preview = 'Changes:\n\n'

        for path, file_changes in self.changes.items():
            for change in file_changes:
                preview += change_as_string(path, change)

        return preview

    def commit(self):
        '''Write these changes to the filesystem.'''

        for path, file_changes in self.changes.items():

            #gets the changes for this file as a list sorted by the
            #starting_line of each change
            sorted_changes = sorted(file_changes, key=itemgetter(0))

            #offset is the number of lines to ADD to the location of the next
            #change. It can be negative, if previous changes were smaller than
            #the source they replaced
            offset = 0

            #lines changes with every run of the loop to reflect each separate
            #change
            with open(path) as read_file:
                lines = read_file.readlines()

            for change in sorted_changes:
                #adjust the line numbers to account for the offset
                starting_line, ending_line, new_lines = change
                starting_line += offset
                ending_line += offset

                #apply the change to lines
                lines = get_changed_copy(
                    lines,
                    (starting_line, ending_line, new_lines))

                #adjust offset based on the length of the change
                old_length = (ending_line - starting_line) + 1
                new_length = len(new_lines)
                offset += new_length - old_length

            #lines now incorporates all changes, and is ready to be written out
            #to the file
            with open(path, 'w') as write_file:
                write_file.writelines(lines)

