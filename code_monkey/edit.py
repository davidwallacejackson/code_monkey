'''Tools for editing source files.'''
import difflib
from operator import attrgetter

from code_monkey.utils import OverlapEditException


def changes_overlap(first_change, second_change):
    '''Return whether first_change and second_change overlap.'''

    if first_change.start >= second_change.start and \
            first_change.start < second_change.end:
        return True

    if first_change.end >= second_change.start and \
            first_change.end < second_change.end:
        return True

    if second_change.start >= first_change.start and \
            second_change.start < first_change.end:
        return True

    if second_change.end >= first_change.start and \
            second_change.end < first_change.end:
        return True

    return False


class ChangeSet(object):
    '''A set of individual changes to make to various files. Can be previewed or
    committed.'''

    def __init__(self, changes=[]):
        self.changes = {}
        self.add(changes)

    def add(self, changes):
        '''Adds changes to the ChangeSet. If changes is a single change, it will
        be coerced to a list of one change (so changeset.add(my_change) is a
        valid use)'''

        if not isinstance(changes, list):
            changes = [changes]

        for change in changes:
            if not change.path in self.changes.keys():
                self.changes[change.path] = []

            for old_change in self.changes[change.path]:
                #check that our new change does not conflict (overlap) with
                #existing changes

                if changes_overlap(old_change, change):
                    #changes in the same file are not allowed to touch the
                    #same lines
                    raise OverlapEditException(
                        change.path,
                        (old_change, change))

            self.changes[change.path].append(change)

    def get_changed_source_for_path(self, path):
        '''Get the source of the file at path after applying the changes in
        ChangeSet.'''

        sorted_changes = sorted(self.changes[path], key=attrgetter('start'))

        #offset is the number of characters to ADD to the location of the
        #next change. It can be negative, if previous changes were smaller
        #than the source they replaced
        offset = 0

        #source changes with every run of the loop to reflect each separate
        #change
        with open(path) as read_file:
            source = read_file.read()

        for change in sorted_changes:
            #adjust the indices to account for the offset
            start = change.start + offset
            end = change.end + offset

            #apply the change to source
            source = source[:start] + change.new_text + source[end:]

            #adjust offset based on the length of the change
            old_length = change.end - change.start
            new_length = len(change.new_text)
            offset += new_length - old_length

        return source

    def diff(self):
        '''Get a diff (as a string) of all the changes to the source encompassed
        by this ChangeSet.'''

        output = 'Changes:\n\n'

        for path in self.changes.keys():
            with open(path, 'r') as source_file:
                old_source = source_file.read()

            new_source = self.get_changed_source_for_path(path)

            old_lines = old_source.splitlines(True)
            new_lines = new_source.splitlines(True)
            diff = difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile=path,
                tofile=path)

            path_diff = ''

            for line in diff:
                path_diff += line

            output += path_diff


        return output

    def diff_to_file(self, file_path):
        '''Write self.diff to file_path. Any file at file_path will be
        erased'''
        with open(file_path, 'w') as outfile:
            outfile.write(self.diff())

    def commit(self):
        '''Write these changes to the filesystem.'''

        for path, file_changes in self.changes.items():

            new_source = self.get_changed_source_for_path(path)

            with open(path, 'w') as write_file:
                write_file.write(new_source)
