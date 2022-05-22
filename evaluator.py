import _parser
import tokenizer


class Evaluator:
    def __init__(self, ast):
        self.ast = ast
        self.variables = {}

    def evaluate(self):
        return [self.evaluate_expression(expression) for expression in self.ast]

    def evaluate_expression(self, expression):
        if type(expression) == _parser.BinaryOperation:
            if expression.op.type == tokenizer.PLUS:
                return self.evaluate_expression(expression.left) + self.evaluate_expression(expression.right)
            elif expression.op.type == tokenizer.MINUS:
                return self.evaluate_expression(expression.left) - self.evaluate_expression(expression.right)
            elif expression.op.type == tokenizer.MULTIPLY:
                return self.evaluate_expression(expression.left) * self.evaluate_expression(expression.right)
            elif expression.op.type == tokenizer.DIVIDE:
                return self.evaluate_expression(expression.left) / self.evaluate_expression(expression.right)
        elif type(expression) == _parser.UnaryOperation:
            if expression.op.type == tokenizer.PLUS:
                return self.evaluate_expression(expression.expression)
            elif expression.op.type == tokenizer.MINUS:
                return -self.evaluate_expression(expression.expression)
            else:
                raise Exception(f"Invalid unary operator: {expression.op.type} ({expression.op.value})")
        elif type(expression) == _parser.AssignVariable:
            self.variables[expression.name] = self.evaluate_expression(expression.value)
        elif type(expression) == _parser.Identifier:
            variable_value = self.variables.get(expression.name_token.value, None)
            if variable_value is None:
                raise Exception(f"Undefined identifier: {expression.name_token.value}")
            return variable_value
        elif type(expression) == _parser.Number:
            return int(expression.value_token.value)


