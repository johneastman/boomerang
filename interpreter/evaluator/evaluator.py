import typing

from interpreter.parser_.ast_objects import Expression, BinaryExpression, UnaryExpression, Identifier, Number, String, \
    Assignment, Error, Boolean, List, BuiltinFunction, Function, FunctionCall, When, PostfixExpression
from interpreter.tokens.tokens import *
from interpreter.evaluator.environment_ import Environment
from interpreter.utils.utils import language_error, LanguageRuntimeException
import copy
from functools import reduce


class Evaluator:
    def __init__(self, ast: list[Expression], env: typing.Optional[Environment]) -> None:
        self.ast = ast
        self.env = env

    @property
    def get_env(self) -> Environment:
        if self.env is None:
            raise Exception("Environment is None")
        return self.env

    def evaluate(self) -> typing.List[Expression]:
        return self.evaluate_statements(self.ast)

    def evaluate_statements(self, statements: list[Expression]) -> list[Expression]:
        evaluated_expressions = []
        try:
            for expression in statements:
                evaluated_expression = self.evaluate_expression(expression)
                # `copy.deepcopy` ensures each evaluated expression in `evaluated_expressions` is accurate to the state
                # of the program during the evaluation of that particular expression.
                evaluated_expressions.append(copy.deepcopy(evaluated_expression))

            # TODO: Figure out how to handle returns for both REPL and regular code execution
            return evaluated_expressions
        except LanguageRuntimeException as e:
            evaluated_expressions.append(Error(e.line_num, str(e)))
            return evaluated_expressions

    def evaluate_expression(self, expression: Expression) -> Expression:

        if isinstance(expression, BinaryExpression):
            return self.evaluate_binary_expression(expression)

        elif isinstance(expression, UnaryExpression):
            return self.evaluate_unary_expression(expression)

        elif isinstance(expression, Assignment):
            return self.evaluate_assign_variable(expression)

        elif isinstance(expression, When):
            return self.evaluate_when(expression)

        elif isinstance(expression, Identifier):
            return self.evaluate_identifier(expression)

        elif isinstance(expression, PostfixExpression):
            return self.evaluate_postfix_expression(expression)

        elif isinstance(expression, List):
            # Initially, I had this code for evaluating lists:
            #
            #     for i in range(len(expression.values)):
            #         expression.values[i] = self.evaluate_expression(expression.values[i])
            #     return expression
            #
            # But that was causing infinite recursion due to a strange behavior where values were being changed
            # without explicitly being changed. Creating a new list object with the evaluates values of the old
            # list fixed the issue.
            values: list[Expression] = []
            for element_expression in expression.values:
                element_value = self.evaluate_expression(element_expression)
                values.append(element_value)
            return List(expression.line_num, values)

        # Base Types
        elif isinstance(expression, Number):
            return expression

        elif isinstance(expression, String):
            return expression

        elif isinstance(expression, Boolean):
            return expression

        elif isinstance(expression, BuiltinFunction):
            return expression

        elif isinstance(expression, Error):
            return expression

        elif isinstance(expression, Function):
            return expression

        # This is a program-specific error because a missing object type would come about during development, not
        # when a user is using this programming language.
        raise Exception(f"Unsupported type: {type(expression).__name__}")

    def evaluate_postfix_expression(self, postfix_expression: PostfixExpression) -> Expression:
        result = self.evaluate_expression(postfix_expression.expression)
        op = postfix_expression.operator

        if op.type == BANG:
            # Factorial
            return result.fac()
        elif op.type == DEC:
            # Decrement
            return result.dec()
        elif op.type == INC:
            # Increment
            return result.inc()

        raise language_error(result.line_num, f"invalid postfix operator: {op.type} ({op.value})")

    def evaluate_assign_variable(self, variable: Assignment) -> Expression:
        var_value: Expression = self.evaluate_expression(variable.value)
        self.get_env.set_var(variable.variable, var_value)
        return var_value

    def evaluate_identifier(self, identifier: Identifier) -> Expression:
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

    def evaluate_unary_expression(self, unary_expression: UnaryExpression) -> Expression:
        expression_result = self.evaluate_expression(unary_expression.expression)
        op = unary_expression.operator

        if op.type == PLUS:
            return expression_result.abs()

        elif op.type == MINUS:
            return expression_result.neg()

        elif op.type == BANG:
            return expression_result.bang()

        raise Exception(f"Invalid unary operator: {op.type} ({op.value})")

    def evaluate_binary_expression(self, binary_operation: BinaryExpression) -> Expression:
        left = self.evaluate_expression(binary_operation.left)

        right = self.evaluate_expression(binary_operation.right)
        op = binary_operation.operator

        # Math operations
        if op.type == PLUS:
            return left.add(right)

        elif op.type == MINUS:
            return left.sub(right)

        elif op.type == MULTIPLY:
            return left.mul(right)

        elif op.type == DIVIDE:
            return left.div(right)

        elif op.type == POINTER:
            result = left.pointer(right)
            if isinstance(result, FunctionCall):
                return self.evaluate_function_call(result)
            return result

        # Comparison Operations
        elif op.type == EQ:
            return left.eq(right)

        elif op.type == NE:
            return left.ne(right)

        elif op.type == GT:
            return left.gt(right)

        elif op.type == GE:
            return left.ge(right)

        elif op.type == LT:
            return left.lt(right)

        elif op.type == LE:
            return left.le(right)

        # Boolean Operations
        elif op.type == AND:
            return left.and_(right)

        elif op.type == OR:
            return left.or_(right)

        raise language_error(op.line_num, f"Invalid binary operator '{op.value}'")

    def evaluate_function_call(self, function_call: FunctionCall) -> Expression:
        line_num: int = function_call.line_num
        function_definition: Function = function_call.function
        call_params: List = function_call.call_params

        if len(call_params.values) != len(function_definition.parameters):
            raise language_error(line_num, f"Expected {len(function_definition.parameters)}, got {len(call_params.values)}")

        self.env = Environment(parent_env=self.get_env)

        # Set parameters as variables in new environment
        for ident, value in zip(function_definition.parameters, call_params.values):
            self.evaluate_assign_variable(
                Assignment(ident.line_num, ident.value, value)
            )

        return_value = self.evaluate_expression(function_definition.body)

        # Reset environment back to old environment
        self.env = self.get_env.parent_env

        return_value.line_num = line_num
        return return_value

    def evaluate_when(self, when: When) -> Expression:

        switch_expression = self.evaluate_expression(when.expression)

        for condition, return_expr in when.case_expressions:
            evaluated_condition = self.evaluate_expression(condition)

            is_equal = evaluated_condition.eq(switch_expression)
            if not isinstance(is_equal, Boolean):
                raise language_error(when.line_num, "must be boolean expression")

            if is_equal.value:
                result = self.evaluate_expression(return_expr)
                result.line_num = when.line_num
                return result

        # When expressions should always return something because of the "else" clause. If nothing
        # is returned, there is a bug in the code.
        raise Exception(f"Error at line {when.line_num}: When statement did not return")
