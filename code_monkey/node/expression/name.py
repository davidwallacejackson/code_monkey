from code_monkey.node.expression.base import ExpressionNode

class NameNode(ExpressionNode):
    def consume_expression(self, detector):
        detector.consume_name()

class AssignmentNameNode(NameNode):
    #not *really* an expression -- should it be refactored?
    pass
