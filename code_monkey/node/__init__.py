'''
Classes representing nodes in the code_monkey project tree. Nodes are aware of
their filesystem path, and, where applicable, their character boundaries within
a source file.

Every Node has a ChangeGenerator (see code_monkey.change) as its .change
property , which can be used to create new Changes based on the contents of that
node.
'''

from code_monkey.node.base import Node

from code_monkey.node.class_node import ClassNode
from code_monkey.node.function import FunctionNode
from code_monkey.node.import_node import ImportNode
from code_monkey.node.module import ModuleNode
from code_monkey.node.package import PackageNode
from code_monkey.node.project import ProjectNode
from code_monkey.node.assignment import AssignmentNode

from code_monkey.node.expression.literal import LiteralNode