from code_monkey.node.expression.base import ExpressionNode

class ConstantNode(ExpressionNode):
    def __init__(self, parent, name, astroid_object):
        super(ConstantNode, self).__init__(parent, name, astroid_object)
        self.value_type = astroid_object._repr_name()

    def consume_expression(self, detector):
        detector.consume_constant()
