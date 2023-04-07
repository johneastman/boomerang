import typing

from _parser import _parser
from tokens.tokens import *
from evaluator._environment import Environment
from utils.utils import language_error
import copy


class Evaluator:
    def __init__(self, ast: list[_parser.Node], env: typing.Optional[Environment]) -> None:
        self.ast = ast
        self.env = env

    @property
    def get_env(self) -> Environment:
        if self.env is None:
            raise Exception("Environment is None")
        return self.env

    def evaluate(self) -> typing.List[_parser.Node]:
        return self.evaluate_statements(self.ast)

    def evaluate_statements(self, statements: list[_parser.Node]) -> list[_parser.Node]:
        evaluated_expressions = []
        for expression in statements:
            evaluated_expression = self.evaluate_expression(expression)
            # `copy.deepcopy` ensures each evaluated expression in `evaluated_expressions` is accurate to the state of
            # the program during the evaluation of that particular expression.
            evaluated_expressions.append(copy.deepcopy(evaluated_expression))

        # TODO: Figure out how to handle returns for both REPL and regular code execution
        # TODO: handle no return
        # if len(evaluated_expressions) == 0:
        #     evaluated_expressions.append(_parser.NoReturn())
        return evaluated_expressions

    def evaluate_expression(self, expression: _parser.Node) -> _parser.Node:

        if expression.type == "binary_expression":
            return self.evaluate_binary_expression(expression)

        elif expression.type == "unary_expression":
            return self.evaluate_unary_expression(expression)

        elif expression.type == "assign":
            return self.evaluate_assign_variable(expression)

        elif expression.type == "identifier":
            return self.evaluate_identifier(expression)

        # Base Types
        elif expression.type == "integer":
            return expression

        elif expression.type == "float":
            return expression

        # This is a program-specific error because a missing object type would come about during development, not
        # when a user is using this programming language.
        raise Exception(f"Unsupported type: {expression.type}")

    def evaluate_assign_variable(self, variable: _parser.Node) -> _parser.Node:

        identifier = variable.params["identifier"]
        value = variable.params["value"]

        if identifier.type == "identifier":
            var_value: _parser.Node = self.evaluate_expression(value)
            self.get_env.set_var(identifier.value, var_value)
            return var_value

        raise language_error(variable.line_num, f"cannot assign value to type {type(variable).__name__}")

    def evaluate_identifier(self, identifier: _parser.Node) -> _parser.Node:
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

        raise language_error(identifier.line_num, f"undefined variable: {identifier.value}")

    def evaluate_unary_expression(self, unary_expression: _parser.Node) -> _parser.Node:
        expression_result = self.evaluate_expression(unary_expression.params["expression"])
        op = unary_expression.params["operator"]

        if op.type == PLUS:
            return expression_result

        elif op.type == MINUS:
            if expression_result.type == "float":
                new_value = -float(expression_result.value)
                return _parser.create_float(new_value, expression_result.line_num)
            elif expression_result.type == "integer":
                new_value = -int(expression_result.value)
                return _parser.create_integer(new_value, expression_result.line_num)
        raise Exception(f"Invalid unary operator: {op.type} ({op.value})")

    def evaluate_binary_expression(self, binary_operation: _parser.Node) -> _parser.Node:
        left = self.evaluate_expression(binary_operation.params["left"])

        right = self.evaluate_expression(binary_operation.params["right"])
        op = binary_operation.params["operator"]

        # Math operations
        if op.type == PLUS:
            return self.operate(left, op.type, right)

        elif op.type == MINUS:
            return self.operate(left, op.type, right)

        elif op.type == MULTIPLY:
            return self.operate(left, op.type, right)

        elif op.type == DIVIDE:
            return self.operate(left, op.type, right)

        raise language_error(op.line_num, f"Invalid binary operator '{op.value}'")

    def operate(self, left: _parser.Node, op: str, right: _parser.Node) -> _parser.Node:

        if left.type == "integer" and right.type == "integer":
            if op == PLUS:
                return _parser.create_integer(int(left.value) + int(right.value), left.line_num)
            elif op == MINUS:
                return _parser.create_integer(int(left.value) - int(right.value), left.line_num)
            elif op == MULTIPLY:
                return _parser.create_integer(int(left.value) * int(right.value), left.line_num)
            elif op == DIVIDE:
                return _parser.create_float(int(left.value) / int(right.value), left.line_num)

            raise language_error(left.line_num, f"Invalid operator: {op}")

        elif left.type == "float" and right.type == "float":
            if op == PLUS:
                return _parser.create_float(float(left.value) + float(right.value), left.line_num)
            elif op == MINUS:
                return _parser.create_float(float(left.value) - float(right.value), left.line_num)
            elif op == MULTIPLY:
                return _parser.create_float(float(left.value) * float(right.value), left.line_num)
            elif op == DIVIDE:
                return _parser.create_float(float(left.value) / float(right.value), left.line_num)

            raise language_error(left.line_num, f"Invalid operator: {op}")

        elif left.type == "integer" and right.type == "float":
            if op == PLUS:
                return _parser.create_float(float(left.value) + float(right.value), left.line_num)
            elif op == MINUS:
                return _parser.create_float(float(left.value) - float(right.value), left.line_num)
            elif op == MULTIPLY:
                return _parser.create_float(float(left.value) * float(right.value), left.line_num)
            elif op == DIVIDE:
                return _parser.create_float(float(left.value) / float(right.value), left.line_num)

            raise language_error(left.line_num, f"Invalid operator: {op}")

        elif left.type == "float" and right.type == "integer":
            if op == PLUS:
                return _parser.create_float(float(left.value) + float(right.value), left.line_num)
            elif op == MINUS:
                return _parser.create_float(float(left.value) - float(right.value), left.line_num)
            elif op == MULTIPLY:
                return _parser.create_float(float(left.value) * float(right.value), left.line_num)
            elif op == DIVIDE:
                return _parser.create_float(float(left.value) / float(right.value), left.line_num)

            raise language_error(left.line_num, f"Invalid operator: {op}")

        raise language_error(left.line_num, f"Invalid types {left.type} and {right.type} for binary operator {op}")
