from code_monkey.node.expression.base import ExpressionNode

class ConstantNode(ExpressionNode):
    def __init__(self, parent, astroid_object, siblings):
        super(ConstantNode, self).__init__(
            parent=parent,
            astroid_object=astroid_object,
            siblings=siblings)

        base_name = 'constant'
        self.name = base_name

        index = 0
        while self.name in siblings:
            self.name = base_name + '_' + str(index)
            index += 1

        self.value_type = astroid_object._repr_name()

    def consume_expression(self, detector):
        detector.consume_constant()
