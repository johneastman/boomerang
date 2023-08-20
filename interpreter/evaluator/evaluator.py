import typing
from io import StringIO
import sys
import copy

import interpreter.parser_.ast_objects as o
from interpreter.tokens import tokens as t
from interpreter.evaluator.environment_ import Environment
from utils.utils import language_error, LanguageRuntimeException, Platform


class Evaluator:
    def __init__(self, ast: list[o.Expression], env: typing.Optional[Environment], platform: str) -> None:
        self.ast = ast

        # Environment needs to be optional because, when switching between scopes--such as a function call--the parent
        # environment could be None.
        self.env = env

        # Platform helps identify what features are or are not supported
        self.platform = platform

        self.unsupported_types: dict[str, list[typing.Type[o.Expression]]] = {
            Platform.WEB.name: [],
            Platform.CMD.name: [],
            Platform.TEST.name: []
        }

        self.output: list[str] = []

    @property
    def get_env(self) -> Environment:
        if self.env is None:
            raise Exception("Environment is None")
        return self.env

    def evaluate(self) -> tuple[list[o.Expression], list[str]]:
        return self.evaluate_statements(self.ast), self.output

    def evaluate_statements(self, statements: list[o.Expression]) -> list[o.Expression]:
        evaluated_expressions = []
        try:
            for expression in statements:
                evaluated_expression = self.evaluate_expression(expression)
                # `copy.deepcopy` ensures each evaluated expression in `evaluated_expressions` is accurate to the state
                # of the program during the evaluation of that particular expression.
                evaluated_expressions.append(copy.deepcopy(evaluated_expression))
            return evaluated_expressions

        except LanguageRuntimeException as e:
            error_obj = o.Error(e.line_num, str(e))
            self.output.append(str(error_obj))
            return [error_obj]

    def evaluate_expression(self, expression: o.Expression) -> o.Expression:

        # Raise an error if an expression instance is not supported on the current platform
        unsupported_types = self.unsupported_types.get(self.platform, [])
        if any(isinstance(expression, v) for v in unsupported_types):
            raise language_error(
                expression.line_num,
                f"unsupported operation for platform {self.platform}: {type(expression).__name__}"
            )

        if isinstance(expression, o.InfixExpression):
            return self.evaluate_binary_expression(expression)

        elif isinstance(expression, o.PrefixExpression):
            return self.evaluate_unary_expression(expression)

        elif isinstance(expression, o.Assignment):
            return self.evaluate_assign_variable(expression)

        elif isinstance(expression, o.When):
            return self.evaluate_when(expression)

        elif isinstance(expression, o.ForLoop):
            return self.evaluate_for(expression)

        elif isinstance(expression, o.Identifier):
            return self.evaluate_identifier(expression)

        elif isinstance(expression, o.PostfixExpression):
            return self.evaluate_postfix_expression(expression)

        elif isinstance(expression, o.List):
            # Initially, I had this code for evaluating lists:
            #
            #     for i in range(len(expression.values)):
            #         expression.values[i] = self.evaluate_expression(expression.values[i])
            #     return expression
            #
            # But that was causing infinite recursion due to a strange behavior where values were being changed
            # without explicitly being changed. Creating a new list object with the evaluates values of the old
            # list fixed the issue.
            values: list[o.Expression] = []
            for element_expression in expression.values:
                element_value = self.evaluate_expression(element_expression)
                values.append(element_value)
            return o.List(expression.line_num, values)

        # Base Types
        elif any(isinstance(expression, t) for t in [o.Number, o.String, o.Boolean, o.BuiltinFunction, o.Error, o.Function]):
            return expression

        # This is a program-specific error because a missing object type would come about during development, not
        # when a user is using this programming language.
        raise Exception(f"Unsupported type: {type(expression).__name__}")

    def evaluate_postfix_expression(self, postfix_expression: o.PostfixExpression) -> o.Expression:
        result = self.evaluate_expression(postfix_expression.expression)
        op = postfix_expression.operator

        if op.type == t.BANG:
            # Factorial
            return result.fac()
        elif op.type == t.DEC:
            # Decrement
            return result.dec()
        elif op.type == t.INC:
            # Increment
            return result.inc()

        raise language_error(result.line_num, f"invalid postfix operator: {op.type} ({op.value})")

    def evaluate_assign_variable(self, variable: o.Assignment) -> o.Expression:
        var_value: o.Expression = self.evaluate_expression(variable.value)
        self.get_env.set_var(variable.name, var_value)
        return var_value

    def evaluate_identifier(self, identifier: o.Identifier) -> o.Expression:
        value = self.get_env.get_var(identifier.value)
        if value is None:
            raise language_error(identifier.line_num, f"undefined variable: {identifier.value}")

        # When a variable is retrieved, update the line number to reflect the current line number because the
        # variable was saved with the line number where it was defined.
        value.line_num = identifier.line_num
        return value

    def evaluate_unary_expression(self, unary_expression: o.PrefixExpression) -> o.Expression:
        expression_result = self.evaluate_expression(unary_expression.expression)
        op = unary_expression.operator

        if op.type == t.PLUS:
            return expression_result.abs()

        elif op.type == t.MINUS:
            return expression_result.neg()

        elif op.type == t.NOT:
            return expression_result.not_()

        elif op.type == t.PACK:
            return expression_result.pack()

        raise Exception(f"Invalid prefix operator: {op.type} ({op.value})")

    def evaluate_binary_expression(self, binary_operation: o.InfixExpression) -> o.Expression:
        left = self.evaluate_expression(binary_operation.left)

        right = self.evaluate_expression(binary_operation.right)
        op = binary_operation.operator

        # Math operations
        if op.type == t.PLUS:
            return left.add(right)

        elif op.type == t.MINUS:
            return left.sub(right)

        elif op.type == t.MULTIPLY:
            return left.mul(right)

        elif op.type == t.DIVIDE:
            return left.div(right)

        elif op.type == t.MOD:
            return left.mod(right)

        elif op.type == t.PACK:
            return left.pow(right)

        elif op.type == t.SEND:
            tmp_stdout = StringIO()

            # Only divert standard output if the interpreter is being called from the web interface.
            if self.platform == Platform.WEB.name:
                sys.stdout = tmp_stdout

            try:
                result = left.ptr(right)
                if isinstance(result, o.FunctionCall):
                    return self.evaluate_function_call(result)
            finally:
                # Reset STDOUT
                sys.stdout = sys.__stdout__

            # Get value from String stream. If the interpreter is not being called from the web interface,
            # this value will always be an empty string.
            output_str = tmp_stdout.getvalue().strip()
            if len(output_str) > 0:
                self.output.append(output_str)
            return result

        # Comparison Operations
        elif op.type == t.EQ:
            return left.eq(right)

        elif op.type == t.NE:
            return left.ne(right)

        elif op.type == t.GT:
            return left.gt(right)

        elif op.type == t.GE:
            return left.ge(right)

        elif op.type == t.LT:
            return left.lt(right)

        elif op.type == t.LE:
            return left.le(right)

        # Boolean Operations
        elif op.type == t.AND:
            return left.and_(right)

        elif op.type == t.OR:
            return left.or_(right)

        elif op.type == t.XOR:
            return left.xor(right)

        elif op.type == t.IN:
            return left.contains(right)

        # Array index
        elif op.type == t.INDEX:
            return left.at(right)

        raise language_error(op.line_num, f"Invalid binary operator '{op.value}'")

    def evaluate_function_call(self, function_call: o.FunctionCall) -> o.Expression:
        line_num: int = function_call.line_num
        function_definition: o.Function = function_call.function
        call_params: o.List = function_call.call_params

        if len(call_params.values) != len(function_definition.parameters):
            raise language_error(line_num, f"Expected {len(function_definition.parameters)}, got {len(call_params.values)}")

        self.env = Environment(parent_env=self.get_env)

        # Set parameters as variables in new environment
        for ident, value in zip(function_definition.parameters, call_params.values):
            self.evaluate_assign_variable(
                o.Assignment(ident.line_num, ident.value, value)
            )

        return_value = self.evaluate_expression(function_definition.body)

        # Reset environment back to old environment
        self.env = self.get_env.parent_env

        return_value.line_num = line_num
        return return_value

    def evaluate_when(self, when: o.When) -> o.Expression:

        switch_expression = self.evaluate_expression(when.expression)

        for condition, return_expr in when.case_expressions:
            evaluated_condition = self.evaluate_expression(condition)

            is_equal = evaluated_condition.eq(switch_expression)
            if not isinstance(is_equal, o.Boolean):
                raise language_error(when.line_num, "must be boolean expression")

            if is_equal.value:
                result = self.evaluate_expression(return_expr)
                result.line_num = when.line_num
                return result

        # When expressions should always return something because of the "else" clause. If nothing
        # is returned, there is a bug in the code.
        raise Exception(f"Error at line {when.line_num}: When statement did not return")

    def evaluate_for(self, for_loop: o.ForLoop) -> o.Expression:

        values = self.evaluate_expression(for_loop.values)

        if not isinstance(values, o.List):
            raise language_error(values.line_num, f"expected List, got {type(values).__name__}")

        # Create new environment for for-loop expression scope
        self.env = Environment(parent_env=self.get_env)

        new_values = []
        for value in values.values:
            self.evaluate_assign_variable(
                o.Assignment(value.line_num, for_loop.element_identifier, value)
            )

            condition_evaluated = self.evaluate_expression(for_loop.conditional_expr)
            if not isinstance(condition_evaluated, o.Boolean):
                raise language_error(
                    condition_evaluated.line_num,
                    f"invalid type for for-loop conditional expression: {type(condition_evaluated).__name__}"
                )

            if condition_evaluated.value:
                new_values.append(
                    self.evaluate_expression(for_loop.expression)
                )

        # Reset environment back to old environment
        self.env = self.get_env.parent_env

        return o.List(for_loop.line_num, new_values)
