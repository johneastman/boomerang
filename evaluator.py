import operator

import _parser
import tokenizer
from _environment import Environment

# TODO: Return a Value object for values (numbers, booleans, etc.) instead of the raw value so we can check the type
#  and throw errors for incompatible types in comparison operators.


class Evaluator:
    def __init__(self, ast, env):
        self.ast = ast
        self.env = env

        # Map operations to valid data types. This ensures expressions like "1 + true", "!1", "-true", "+false", etc.
        # are invalid.
        self.valid_operation_types = {
            tokenizer.PLUS: [tokenizer.NUMBER],
            tokenizer.MINUS: [tokenizer.NUMBER],
            tokenizer.MULTIPLY: [tokenizer.NUMBER],
            tokenizer.DIVIDE: [tokenizer.NUMBER],
            tokenizer.EQ: [tokenizer.NUMBER, tokenizer.TRUE, tokenizer.FALSE],
            tokenizer.NE: [tokenizer.NUMBER, tokenizer.TRUE, tokenizer.FALSE],
            tokenizer.GT: [tokenizer.NUMBER],
            tokenizer.GE: [tokenizer.NUMBER],
            tokenizer.LT: [tokenizer.NUMBER],
            tokenizer.LE: [tokenizer.NUMBER],
            tokenizer.BANG: [tokenizer.TRUE, tokenizer.FALSE]
        }

        # How to convert token values to their Python values so the comparison can be performed
        # accurately. For example, "1" should be converted to an integer.
        self.convert_literal = {
            tokenizer.NUMBER: int,
            tokenizer.TRUE: lambda _: True,
            tokenizer.FALSE: lambda _: False
        }

    def evaluate(self):
        return self.evaluate_statements(self.ast)

    def evaluate_statements(self, statements):
        return [self.evaluate_expression(expression) for expression in statements]

    def evaluate_boolean_expressions(self, expression: _parser.BinaryOperation, _operator):
        """Evaluate a boolean expression and cast the result to a _parser.Boolean object so the expected value for
        the language is returned (e.g., "true" => True in Python; "false" => False in Python).

        :param expression: a binary operation
        :param _operator: the operation being performed (less-than, greater-than-or-equal, not-equal, equal, etc.)
        :return: evaluated _parser.Boolean object
        """
        left_value = self.evaluate_expression(expression.left)
        right_value = self.evaluate_expression(expression.right)
        result = _operator(left_value, right_value)
        result_token = tokenizer.Token(result, tokenizer.TRUE if result else tokenizer.FALSE, 0)
        return self.evaluate_expression(_parser.Boolean(result_token))

    def evaluate_expression(self, expression):
        if type(expression) == _parser.BinaryOperation:
            return self.evaluate_binary_expression(expression)

        elif type(expression) == _parser.UnaryOperation:
            return self.evaluate_unary_expression(expression)

        elif type(expression) == _parser.IfStatement:
            evaluated_comparison = self.evaluate_expression(expression.comparison)
            if evaluated_comparison.value == "true":
                self.evaluate_statements(expression.true_statements)
            elif expression.false_statements is not None:
                self.evaluate_statements(expression.false_statements)

        elif type(expression) == _parser.AssignVariable:
            self.env.set_var(expression.name.value, self.evaluate_expression(expression.value))
            return tokenizer.Token("null", tokenizer.NULL, expression.name.line_num)

        elif type(expression) == _parser.AssignFunction:
            self.env.set_func(expression.name.value, expression)
            return tokenizer.Token("null", tokenizer.NULL, expression.name.line_num)

        elif type(expression) == _parser.Identifier:
            # For variables, check the current environment. If it does not exist, check the parent environment.
            # Continue doing this until there are no more parent environments. If the variable does not exist in all
            # scopes, it does not exist anywhere in the code.
            env = self.env
            while env is not None:
                variable_value = env.get_var(expression.value)
                if variable_value is not None:
                    return variable_value
                env = env.parent_env

            raise Exception(f"Undefined variable at line {expression.line_num}: {expression.value}")

        elif type(expression) == _parser.FunctionCall:
            function_name = expression.name.value
            function = self.env.get_func(function_name)

            # If the function is not defined in the functions dictionary, throw an error saying the
            # function is undefined
            if function is None:
                raise Exception(f"Undefined function at line {expression.name.line_num}: {function_name}")

            parameter_identifiers = function.parameters
            parameter_values = expression.parameter_values

            if len(parameter_identifiers) != len(parameter_values):
                error_msg = "Incorrect number of arguments. "
                error_msg += f"Function '{function_name}' defined with {len(parameter_identifiers)} parameters "
                error_msg += f"({', '.join(map(lambda t: t.value, parameter_identifiers))}), "
                error_msg += f"but {len(parameter_values)} given."
                raise Exception(error_msg)

            # Map the parameters to their values and set them in the variables dictionary
            evaluated_param_values = {}
            for param_name, param_value in zip(parameter_identifiers, parameter_values):
                evaluated_param_values[param_name.value] = self.evaluate_expression(param_value)

            # Create a new environment for the function's variables
            self.env = Environment(parent_env=self.env)
            self.env.set_vars(evaluated_param_values)

            # Evaluate every expression in the function body
            statements = function.statements
            executed_expressions = self.evaluate_statements(statements)

            # After the function is called, switch to the parent environment
            self.env = self.env.parent_env

            return executed_expressions[-1] if type(statements[-1]) == _parser.Return else "null"

        elif type(expression) == _parser.BuiltinFunction:
            if expression.name.value == "print":
                evaluated_params = []
                for param in expression.parameters:
                    result = self.evaluate_expression(param)
                    evaluated_params.append(result)

                print(", ".join(map(lambda v: str(v.value), evaluated_params)))
            return tokenizer.Token("null", tokenizer.NULL, expression.name.line_num)

        elif type(expression) == _parser.Number:
            return expression.token

        elif type(expression) == _parser.Null:
            return expression.token

        elif type(expression) == _parser.Boolean:
            return expression.token

        elif type(expression) == _parser.Return:
            return self.evaluate_expression(expression.expression)

    def evaluate_unary_expression(self, unary_expression):
        expression_result = self.evaluate_expression(unary_expression.expression)
        op_type = unary_expression.op.type

        valid_type = self.valid_operation_types.get(op_type, [])
        if expression_result.type not in valid_type:
            raise Exception(f"Cannot perform {op_type} operation on {expression_result.type}")

        actual_value = self.convert_literal[expression_result.type](expression_result.value)

        if op_type == tokenizer.PLUS:
            return tokenizer.Token(actual_value, tokenizer.NUMBER, expression_result.line_num)
        elif op_type == tokenizer.MINUS:
            return tokenizer.Token(-actual_value, tokenizer.NUMBER, expression_result.line_num)
        elif op_type == tokenizer.BANG:
            value, _type = ("false", tokenizer.FALSE) if actual_value else ("true", tokenizer.TRUE)
            return tokenizer.Token(value, _type, expression_result.line_num)
        else:
            raise Exception(f"Invalid unary operator: {op_type} ({expression_result.op})")

    def evaluate_binary_expression(self, binary_operation):
        left = self.evaluate_expression(binary_operation.left)
        right = self.evaluate_expression(binary_operation.right)
        op_type = binary_operation.op.type

        # Check that the types are the same. If they are not, the operation cannot be performed. This is for operations
        # that can be performed on all types (NUMBER, TRUE, FALSE, etc.). Without this check, someone could run
        # "1 == true" or "false != 2". Both checks are technically valid, but this is invalid because the data types
        # for the left and right expressions are not the same.
        if left.type != right.type:
            raise Exception(f"Cannot perform {op_type} operation on {left.type} and {right.type}")

        # Check that the operation can be performed on the given types. For example, "true > false" is not valid
        valid_type = self.valid_operation_types.get(op_type, [])
        if left.type not in valid_type or right.type not in valid_type:
            raise Exception(f"Cannot perform {op_type} operation on {left.type} and {right.type}")

        left_val = self.convert_literal[left.type](left.value)
        right_val = self.convert_literal[right.type](right.value)

        # Math operations
        if op_type == tokenizer.PLUS:
            return tokenizer.Token(left_val + right_val, tokenizer.NUMBER, left.line_num)
        elif op_type == tokenizer.MINUS:
            return tokenizer.Token(left_val - right_val, tokenizer.NUMBER, left.line_num)
        elif op_type == tokenizer.MULTIPLY:
            return tokenizer.Token(left_val * right_val, tokenizer.NUMBER, left.line_num)
        elif op_type == tokenizer.DIVIDE:
            if right_val == 0:
                raise Exception("Division by zero")
            return tokenizer.Token(left_val + right_val, tokenizer.NUMBER, left.line_num)

        # Binary comparisons
        elif op_type == tokenizer.EQ:
            result = left_val == right_val
            value, _type = ("true", tokenizer.TRUE) if result else ("false", tokenizer.FALSE)
            return tokenizer.Token(value, _type, left.line_num)
        elif op_type == tokenizer.NE:
            result = left_val != right_val
            value, _type = ("true", tokenizer.TRUE) if result else ("false", tokenizer.FALSE)
            return tokenizer.Token(value, _type, left.line_num)
        elif op_type == tokenizer.GT:
            result = left_val > right_val
            value, _type = ("true", tokenizer.TRUE) if result else ("false", tokenizer.FALSE)
            return tokenizer.Token(value, _type, left.line_num)
        elif op_type == tokenizer.GE:
            result = left_val >= right_val
            value, _type = ("true", tokenizer.TRUE) if result else ("false", tokenizer.FALSE)
            return tokenizer.Token(value, _type, left.line_num)
        elif op_type == tokenizer.LT:
            result = left_val < right_val
            value, _type = ("true", tokenizer.TRUE) if result else ("false", tokenizer.FALSE)
            return tokenizer.Token(value, _type, left.line_num)
        elif op_type == tokenizer.LE:
            result = left_val <= right_val
            value, _type = ("true", tokenizer.TRUE) if result else ("false", tokenizer.FALSE)
            return tokenizer.Token(value, _type, left.line_num)
        else:
            raise Exception(f"Invalid binary operator '{binary_operation.op.value}' at line {binary_operation.op.line_num}")
