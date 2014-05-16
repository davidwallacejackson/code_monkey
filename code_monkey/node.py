import os
import pkgutil

import rope.base.project
from rope.base.pynames import DefinedName
from rope.base.pyobjectsdef import PyClass, PyFunction


def get_modules(fs_path):
    '''Find all Python modules in fs_path. Returns a list of tuples of the form:
    (module_name, is_package)'''

    modules = []

    for filename in os.listdir(fs_path):

        full_path = os.path.join(fs_path, filename)

        if os.path.isdir(full_path) and '__init__.py' in os.listdir(full_path):
            #directories with an __init__.py file are Python packages
            modules.append((filename, True))
        elif filename.endswith('.py'):

            #NOTE: not sure if this is robust enough. better way?
            module_name = filename.strip(".py")

            #files ending in .py are assumed to be Python modules
            modules.append((module_name, False))

    return modules


class Node(object):

    def __init__(self):
        self.parent = None
        self.children = None
        self.rope_scope = None
        self.path = None

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
        if self.parent:
            return self.parent.root

        return self

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
        self.rope_project = rope.base.project.Project(project_path)
        self.parent = None
        self.scope = None
        self.path = ''

        #the file system (not python) path to the project
        self.fs_path = project_path

    @property
    def children(self):
        '''rope doesn't expose the children of packages in a convenient way, so
        we the filesystem to list them and build child nodes'''

        #NOTE: pkgutil.iter_modules should do this, but for some reason it is
        #occasionally iterating down and grabbing modules that aren't on the
        #surface. Would be worth finding out why.
        child_names = get_modules(self.fs_path)

        children = []

        for name, is_package in child_names:
            if is_package:
                children.append(PackageNode(
                    parent=self,
                    path=name))
            else:
                children.append(ModuleNode(
                    parent=self,
                    path=name))

        return children

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return '{}: {}'.format(
            str(self.__class__.__name__),
            self.name)


class PackageNode(Node):
    
    def __init__(self, parent, path):
        self.parent = parent
        self.path = path
        self.rope_object = self.root.rope_project.get_pycore().get_module(path)

    @property
    def children(self):
        '''rope doesn't expose the children of packages in a convenient way, so
        we use pkgutil to access them and build child nodes'''

        child_names = get_modules(self.rope_object.get_resource().real_path)
        children = []

        for name, is_package in child_names:
            if is_package:
                children.append(PackageNode(
                    parent=self,
                    path=self.path + '.' + name))
            else:
                children.append(ModuleNode(
                    parent=self,
                    path=self.path + '.' + name))

        return children


class ModuleNode(Node):

    def __init__(self, parent, path):
        self.parent = parent
        self.path = path
        self.rope_object = self.root.rope_project.get_pycore().get_module(path)
        self.rope_scope = self.rope_object.get_scope()

    @property
    def children(self):
        #all of rope's PyNames found in scope in this module
        names = self.rope_scope.get_names()
        children = []

        for str_name, pyname in names.items():
            #str_name is the name as a string, pyname is the rope PyName object
            #representing it

            #we only want names defined in this module -- rope calls these
            #DefinedNames
            if isinstance(pyname, DefinedName):
                pyobject = pyname.get_object()

                #we can use the PyObject from rope to distinguish classes,
                #functions, and variables

                if isinstance(pyobject, PyClass):

                    children.append(ClassNode(
                        parent=self,
                        path=self.path + '.' + str_name))

                elif isinstance(pyobject, PyFunction):

                    children.append(FunctionNode(
                        parent=self,
                        path=self.path + '.' + str_name))

                else:
                    #if it's not a class or a function, we'll assume it's a
                    #variable

                    children.append(VariableNode(
                        parent=self,
                        path=self.path + '.' + str_name))

        return children

 
class ClassNode(Node):
    def __init__(self, parent, path):
        self.parent = parent
        self.path = path

        self.rope_object = self.parent.rope_scope.get_name(
            self.name).get_object()
        self.rope_scope = self.rope_object.get_scope()


class VariableNode(Node):
    def __init__(self, parent, path):
        self.parent = parent
        self.path = path

        self.rope_object = self.parent.rope_scope.get_name(
            self.name).get_object()


class FunctionNode(Node):
    def __init__(self, parent, path):
        self.parent = parent
        self.path = path

        self.rope_object = self.parent.rope_scope.get_name(
            self.name).get_object()
        self.rope_scope = self.rope_object.get_scope()

