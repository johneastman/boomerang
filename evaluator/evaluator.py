import typing

from _parser import _parser
from tokens.tokens import *
from evaluator._environment import Environment
from utils.utils import raise_error
import copy


class Evaluator:
    def __init__(self, ast: list[_parser.Statement], env: typing.Optional[Environment]) -> None:
        self.ast = ast
        self.env = env

    @property
    def get_env(self) -> Environment:
        if self.env is None:
            raise Exception("Environment is None")
        return self.env

    def evaluate(self) -> typing.List[_parser.Base]:
        return self.evaluate_statements(self.ast)

    def evaluate_statements(self, statements: list[_parser.Statement]) -> list[_parser.Base]:
        evaluated_expressions = []
        for expression in statements:
            evaluated_expression = self.evaluate_expression(expression)
            # `copy.deepcopy` ensures each evaluated expression in `evaluated_expressions` is accurate to the state of
            # the program during the evaluation of that particular expression.
            evaluated_expressions.append(copy.deepcopy(evaluated_expression))

        # TODO: Figure out how to handle returns for both REPL and regular code execution
        if len(evaluated_expressions) == 0:
            evaluated_expressions.append(_parser.NoReturn())
        return evaluated_expressions

    def validate_expression(self, expression: _parser.Expression) -> _parser.Base:
        value: _parser.Base = self.evaluate_expression(expression)
        if isinstance(value, _parser.NoReturn):
            raise_error(value.line_num, "cannot evaluate expression that returns no value")
        return value

    def evaluate_expression(self, expression: typing.Union[_parser.Expression, _parser.Statement]) -> _parser.Base:
        if isinstance(expression, _parser.BinaryOperation):
            return self.evaluate_binary_expression(expression)

        elif isinstance(expression, _parser.UnaryOperation):
            return self.evaluate_unary_expression(expression)

        elif isinstance(expression, _parser.SetVariable):
            return self.evaluate_assign_variable(expression)

        elif isinstance(expression, _parser.Identifier):
            return self.evaluate_identifier(expression)

        elif isinstance(expression, _parser.ExpressionStatement):
            return self.evaluate_expression(expression.expr)

        # Base Types
        elif isinstance(expression, _parser.Integer):
            return expression

        elif isinstance(expression, _parser.Float):
            return expression

        # This is a program-specific error because a missing object type would come about during development, not
        # when a user is using this programming language.
        raise Exception(f"Unsupported type: {type(expression).__name__}")

    def evaluate_assign_variable(self, variable_assignment: _parser.SetVariable) -> _parser.NoReturn:
        variable = variable_assignment.name

        if isinstance(variable, _parser.Identifier):
            var_value: _parser.Base = self.validate_expression(variable_assignment.value)
            self.get_env.set_var(variable.value, var_value)
            return _parser.NoReturn(line_num=var_value.line_num)

        raise_error(variable_assignment.name.line_num, f"cannot assign value to type {type(variable).__name__}")

    def evaluate_identifier(self, identifier: _parser.Identifier) -> _parser.Base:
        # For variables, check the current environment. If it does not exist, check the parent environment.
        # Continue doing this until there are no more parent environments. If the variable does not exist in all
        # scopes, it does not exist anywhere in the code.
        env: typing.Optional[Environment] = self.env
        while env is not None:
            variable_value = env.get_var(identifier.value)
            if variable_value is not None:

                # When a variable is retrieved, update the line number to reflect the current line number because the
                # variable was saved with the line number where it was defined.
                variable_value.line_num = identifier.line_num
                return variable_value
            env = env.parent_env

        raise_error(identifier.line_num, f"undefined variable: {identifier.value}")

    def evaluate_unary_expression(self, unary_expression: _parser.UnaryOperation) -> _parser.Base:
        expression_result = self.validate_expression(unary_expression.expression)
        op_type = unary_expression.op.type

        if op_type == PLUS:
            return expression_result.positive()

        elif op_type == MINUS:
            return expression_result.negative()

        else:
            raise Exception(f"Invalid unary operator: {op_type} ({unary_expression.op.value})")

    def evaluate_binary_expression(self, binary_operation: _parser.BinaryOperation) -> _parser.Base:
        left = self.validate_expression(binary_operation.left)

        right = self.validate_expression(binary_operation.right)
        op_type = binary_operation.op.type

        # Math operations
        if op_type == PLUS:
            return left.add(right)

        elif op_type == MINUS:
            return left.subtract(right)

        elif op_type == MULTIPLY:
            return left.multiply(right)

        elif op_type == DIVIDE:
            return left.divide(right)

        raise Exception(f"Invalid binary operator '{binary_operation.op.value}' at line {binary_operation.op.line_num}")

    def create_base_object(self, value: object, line_num: int) -> _parser.Base:
        if isinstance(value, float):
            return _parser.Float(value, line_num)
        elif isinstance(value, int):
            return _parser.Integer(value, line_num)
        else:
            raise Exception(f"Unsupported internal type: {type(value).__name__}")
