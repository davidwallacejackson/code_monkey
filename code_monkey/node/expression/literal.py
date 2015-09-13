from code_monkey.node.expression.base import ExpressionNode

class LiteralNode(ExpressionNode):
    def __init__(self, parent, name, astroid_object):
        super(LiteralNode, self).__init__(parent, name, astroid_object)

        self.value_type = astroid_object._repr_name()
