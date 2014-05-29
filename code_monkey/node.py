from ast import literal_eval
import os
import pkgutil

from astroid.manager import AstroidManager
from astroid.node_classes import Assign, AssName
from astroid.scoped_nodes import Class, Function

from code_monkey.change import ChangeGenerator, VariableChangeGenerator
from code_monkey.utils import (
    count_unterminated_in_source,
    find_termination,
    line_column_to_absolute_index,
    string_to_lines)

def get_modules(fs_path):
    '''Find all Python modules in fs_path. Returns a list of tuples of the form:
    (module_name, is_package)'''

    modules = []

    for filename in os.listdir(fs_path):

        full_path = os.path.join(fs_path, filename)

        if os.path.isdir(full_path) and '__init__.py' in os.listdir(full_path):
            #directories with an __init__.py file are Python packages
            modules.append((filename, True))
        elif filename.endswith('.py') and not filename == '__init__.py':
            #TODO: figure out how to handle source in init files, since astroid
            #doesn't acknowledge them

            #strip the extension
            module_name = os.path.splitext(filename)[0]

            #files ending in .py are assumed to be Python modules
            modules.append((module_name, False))

    return modules


def make_astroid_project(project_path):
    project_files = []

    return AstroidManager().project_from_files([project_path])


class Node(object):

    def __init__(self):
        self.parent = None
        self.path = None

    @property
    def change(self):
        return ChangeGenerator(self)

    @property
    def children(self):
        return {}

    @property
    def name(self):
        '''the name is the last component of the path'''
        if not self.path:
            return '[root]'

        path_components = self.path.split('.')
        return path_components[
            len(path_components) - 1]

    @property
    def root(self):
        '''return the root Node in the tree (should be a ProjectNode)'''
        if self.parent:
            return self.parent.root

        return self

    @property
    def fs_path(self):
        #some nodes will recurse upward to find their fs_path, which is why we
        #hide it behind a property method
        return self._fs_path

    def get_source_file(self):
        '''return a read-only file object for the file in which this Node was
        defined. only meaningful at or below the module level -- higher than
        that, source_file is None.'''

        try:
            return open(self.fs_path, 'r')
        except IOError:
            #if the path is to a directory, we'll get an IOError
            return None


    @property
    def start_line(self):
        #astroid gives line numbers starting with 1
        return self._astroid_object.fromlineno - 1

    @property
    def body_start_line(self):
        return self.start_line


    @property
    def end_line(self):
        #astroid gives line numbers starting with 1
        return self._astroid_object.tolineno

    @property
    def body_end_line(self):
        return self.end_line


    @property
    def start_column(self):
        return self._astroid_object.col_offset

    @property
    def body_start_column(self):
        return self.start_column


    @property
    def end_column(self):
        return 0

    @property
    def body_end_column(self):
        return self.body_end_column


    @property
    def start_index(self):
        '''The character index of the beginning of the node, relative to the
        entire source file.'''
        return line_column_to_absolute_index(
            self.get_file_source_code(),
            self.start_line,
            self.start_column)

    @property
    def end_index(self):
        '''The character index of the character after the end of the node,
        relative to the entire source file.'''
        return line_column_to_absolute_index(
            self.get_file_source_code(),
            self.end_line,
            self.end_column)

    @property
    def body_start_index(self):
        '''The character index of the beginning of the node body, relative to
        the entire source file.'''
        return line_column_to_absolute_index(
            self.get_file_source_code(),
            self.body_start_line,
            self.body_start_column)

    @property
    def body_end_index(self):
        '''The character index of the character after the end of the node body,
        relative to the entire source file.'''
        return line_column_to_absolute_index(
            self.get_file_source_code(),
            self.body_end_line,
            0)
 
    def _get_source_region(self, start_index, end_index):
        '''return a substring of the source code starting from start_index up to
        but not including end_index'''

        with open(self.fs_path, 'r') as source_file:

            if not source_file:
                return None

            source = source_file.read()
            source = source[start_index:end_index]

            return source

    def get_file_source_code(self):
        '''Return the text of the entire file containing Node.'''
        with open(self.fs_path, 'r') as source_file:
            if not source_file:
                return None

            return source_file.read()

    def get_source(self):
        '''return a string of the source code the Node represents'''

        return self._get_source_region(
            self.start_index,
            self.end_index)

    def get_body_source(self):
        '''return a string of only the body of the node -- i.e., excluding the
        declaration. For a Class or Function, that means the class or function
        body. For a Variable, that's the right hand of the assignment. For a
        Module, it's the same as get_source().'''
        return self._get_source_region(
            self.body_start_index,
            self.body_end_index)


    def __unicode__(self):
        return '{}: {}'.format(
            str(self.__class__.__name__),
            self.path)

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return self.__unicode__()



class ProjectNode(Node):

    def __init__(self, project_path):
        super(ProjectNode, self).__init__()

        #remove trailing slash if present, for consistency
        #this is important when we use .split('/') to find the name of the
        #project directory
        if project_path.endswith('/'):
            project_path = project_path[:-1]

        self._astroid_project = make_astroid_project(project_path)
        self.parent = None
        self.scope = None
        self.path = ''

        #the file system (not python) path to the project
        self._fs_path = project_path

    @property
    def children(self):
        '''astroid doesn't expose the children of packages in a convenient way,
        so we the filesystem to list them and build child nodes'''

        #NOTE: pkgutil.iter_modules should do this, but for some reason it is
        #occasionally iterating down and grabbing modules that aren't on the
        #surface. Would be worth finding out why.
        child_names = get_modules(self.fs_path)

        children = {}

        for name, is_package in child_names:
            if is_package:
                children[name] = PackageNode(
                    parent=self,
                    path=name)
            else:
                children[name] = ModuleNode(
                    parent=self,
                    path=name)

        return children

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return '{}: {}'.format(
            str(self.__class__.__name__),
            self.name)


class PackageNode(Node):
    
    def __init__(self, parent, path):
        super(PackageNode, self).__init__()

        self.parent = parent
        self.path = path

        self._fs_path = os.path.join(
            self.root.fs_path,
            self.path.replace('.', '/'))

    @property
    def children(self):
        '''astroid doesn't expose the children of packages in a convenient way,
        so we use pkgutil to access them and build child nodes'''

        child_names = get_modules(self.fs_path)
        children = {}

        for name, is_package in child_names:
            if is_package:
                children[name] = PackageNode(
                    parent=self,
                    path=self.path + '.' + name)
            else:
                children[name] = ModuleNode(
                    parent=self,
                    path=self.path + '.' + name)

        return children


class ModuleNode(Node):

    def __init__(self, parent, path):
        super(ModuleNode, self).__init__()

        self.parent = parent
        self.path = path

        #TODO: below is a hacky way of getting the name of the folder that the
        #whole project is in (and it's broken under Windows). come up with
        #something more robust!
        root_fs_path = self.root.fs_path

        if '__init__.py' in os.listdir(root_fs_path):
            #if root has an __init__, it's a package, and we need to add its
            #name to the path
            root_package_name = self.root.fs_path.split('/')[-1] + '.'
        else:
            root_package_name = ''

        self._fs_path = os.path.join(
            self.root.fs_path,
            self.path.replace('.', '/')) + '.py'

        try:
            self._astroid_object = self.root._astroid_project.get_module(
                root_package_name + self.path)
        except KeyError:
            #if the project root is not in the current Python path, astroid
            #uses filenames to identify modules. And depending on what exactly
            #is in the path, the project folder's name may or may not be
            #appended

            #TODO: find a way to force consistent behavior in astroid. ideally,
            #we want it to always behave like the project under inspection is in
            #the Python path
            self._astroid_object = self.root._astroid_project.get_module(
                self.fs_path)

    @property
    def children(self):
        #all of the children found by astroid:

        astroid_children = self._astroid_object.get_children()
        children = {}

        for child in astroid_children:
            
            if isinstance(child, Class):

                children[child.name] = ClassNode(
                    parent=self,
                    path=self.path + '.' + child.name,
                    astroid_object=child)

            elif isinstance(child, Function):

                children[child.name] = FunctionNode(
                    parent=self,
                    path=self.path + '.' + child.name,
                    astroid_object=child)

            elif isinstance(child, Assign):
                #Assign is the class representing a variable assignment.

                #we don't know the name of the variable until we build the Node,
                #so we build the node before adding it to the children dict
                child_node = VariableNode(
                    parent=self,
                    astroid_object=child)

                children[child_node.name] = child_node

        return children

    @property
    def start_line(self):
        #for modules, astroid gives 0 as the start line -- so we don't want to
        #subtract 1
        return self._astroid_object.fromlineno

    @property
    def start_column(self):
        #for modules, astroid gives None as the column offset -- by our
        #conventions, it should be 0
        return 0


class ClassNode(Node):
    def __init__(self, parent, path, astroid_object):
        super(ClassNode, self).__init__()

        self.parent = parent
        self.path = path
        self._astroid_object = astroid_object

    @property
    def children(self):
        #all of the children found by astroid:

        astroid_children = self._astroid_object.get_children()
        children = {}

        for child in astroid_children:

            if isinstance(child, Class):

                children[child.name] = ClassNode(
                    parent=self,
                    path=self.path + '.' + child.name,
                    astroid_object=child)

            elif isinstance(child, Function):

                children[child.name] = FunctionNode(
                    parent=self,
                    path=self.path + '.' + child.name,
                    astroid_object=child)

            elif isinstance(child, Assign):
                #Assign is the class representing a variable assignment.

                #we don't know the name of the variable until we build the Node,
                #so we build the node before adding it to the children dict
                child_node = VariableNode(
                    parent=self,
                    astroid_object=child)

                children[child_node.name] = child_node

        return children
    @property
    def fs_path(self):
        #TODO: doesn't work for nested classes
        return self.parent.fs_path

    @property
    def body_start_line(self):
        #TODO: account for multi-line class signatures
        return self.start_line + 1

    @property
    def body_start_column(self):
        return 0


class VariableNode(Node):
    def __init__(self, parent, astroid_object):
        super(VariableNode, self).__init__()

        self.parent = parent

        #the _astroid_object (an Assign object) has TWO children that we need to
        #consider: (the variable name) and another astroid node (the 'right
        #hand' value)
        self._astroid_object = astroid_object

        #TODO: account for tuple assignment
        self._astroid_name = self._astroid_object.targets[0]
        self._astroid_value = self._astroid_object.value

        try:
            self.path = self.parent.path + '.' + self._astroid_name.name
        except AttributeError:
            #'subscript' assignments (a[b] = ...) don't have a name in astroid.
            #instead, we give them one by reading their source

            #TODO: this can result in names containing dots, which is invalid.
            #need a better solution
            self.path = self.parent.path + '.' + self._astroid_name.as_string()

    def eval_body(self):
        '''Attempt to evaluate the body (i.e., the value) of this VariableNode
        using ast.literal_eval (which will evaluate ONLY Python literals).

        Return the value if successful, otherwise, return None.'''
        try:
            return literal_eval(self.get_body_source())
        except (SyntaxError, ValueError):
            return None

    @property
    def fs_path(self):
        #TODO: doesn't work for nested variables
        return self.parent.fs_path

    @property
    def change(self):
        return VariableChangeGenerator(self)

    #the 'whole source' of a VariableNode includes the name and the value
    @property
    def start_line(self):
        return self._astroid_name.fromlineno - 1

    @property
    def start_column(self):
        return self._astroid_name.col_offset

    #in a VariableNode, the _astroid_value represents the body
    @property
    def body_start_line(self):
        return self._astroid_value.fromlineno - 1

    @property
    def body_start_column(self):
        return self._astroid_value.col_offset

    @property
    def end_line(self):
        #there's a bug in astroid where it doesn't correctly detect the last
        #line of multiline enclosed blocks (parens, brackets, etc.) -- it gives
        #the last line with content, rather than the line containing the
        #terminating character

        #we have to work around this by scanning through the source ourselves to
        #find the terminating point -- see utils.find_termination

        #should probably submit a bug report for astroid, too

        astroid_end_index = line_column_to_absolute_index(
            self.get_file_source_code(),
            self._astroid_value.tolineno,
            0)

        source_via_astroid = self._get_source_region(
            self.body_start_index,
            astroid_end_index)

        unclosed_dict = {}

        parens_count = count_unterminated_in_source(
            source_via_astroid, '(', ')')
        if parens_count > 0:
            unclosed_dict[')'] = parens_count 

        square_count = count_unterminated_in_source(
            source_via_astroid, '[', ']')
        if square_count > 0:
            unclosed_dict[']'] = square_count

        curly_count = count_unterminated_in_source(
            source_via_astroid, '{', '}')
        if curly_count > 0:
            unclosed_dict['}'] = curly_count

        if len(unclosed_dict.items()) > 0:
            unclosed_count = reduce(lambda x, y: x+y, unclosed_dict.values())
        else:
            unclosed_count = 0

        if unclosed_count == 0:
            #if there are no unclosed blocks, then astroid found the right end
            #line, and we can just return it
            return self._astroid_value.tolineno - 1

        #otherwise, we have to dig through the source looking for the end
        #ourselves
        with open(self.fs_path, 'r') as source_file:
            full_source = source_file.read()

            source_lines = string_to_lines(full_source)

        end_line = find_termination(
            source_lines,
            self._astroid_value.tolineno - 1,
            unclosed_dict)

        return (end_line + 1)


class FunctionNode(Node):
    def __init__(self, parent, path, astroid_object):
        super(FunctionNode, self).__init__()

        self.parent = parent
        self.path = path
        self._astroid_object = astroid_object

    @property
    def fs_path(self):
        #TODO: doesn't work for nested functions/methods
        return self.parent.fs_path

    @property
    def body_start_line(self):
        #TODO: account for multi-line function signatures
        return self.start_line + 1

    @property
    def body_start_column(self):
        return 0
