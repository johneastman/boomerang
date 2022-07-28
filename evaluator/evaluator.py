import typing
import ast

from _parser import _parser
from tokens.tokens import *
from tokens.tokenizer import Token
from evaluator._environment import Environment
from utils import raise_error, ReturnException
import copy
import random


class Evaluator:
    def __init__(self, ast, env):
        self.ast = ast
        self.env = env

        # Map operations to valid data types. This ensures expressions like "1 + true", "!1", "-true", "+false", etc.
        # are invalid.
        self.valid_operation_types = {
            PLUS: [INTEGER, STRING, FLOAT],
            MINUS: [INTEGER, FLOAT],
            MULTIPLY: [INTEGER, FLOAT],
            DIVIDE: [INTEGER, FLOAT],
            EQ: [INTEGER, BOOLEAN, FLOAT, STRING],
            NE: [INTEGER, BOOLEAN, FLOAT, STRING],
            GT: [INTEGER, FLOAT],
            GE: [INTEGER, FLOAT],
            LT: [INTEGER, FLOAT],
            LE: [INTEGER, FLOAT],
            BANG: [BOOLEAN],
            AND: [BOOLEAN],
            OR: [BOOLEAN]
        }

        # Map what types are compatible with others when performing operations (for example, addition can be performed
        # on floats and integers).
        self.compatible_types_for_operations = {
            FLOAT: [FLOAT, INTEGER],
            INTEGER: [INTEGER, FLOAT],
            STRING: [STRING],
            BOOLEAN: [BOOLEAN]
        }

    def evaluate(self):
        return self.evaluate_statements(self.ast)

    def evaluate_statements(self, statements: list[_parser.Statement]):
        evaluated_expressions = []
        for expression in statements:
            evaluated_expression = self.evaluate_expression(expression)
            # `copy.deepcopy` ensures each evaluated expression in `evaluated_expressions` is accurate to the state of
            # the program during the evaluation of that particular expression.
            evaluated_expressions.append(copy.deepcopy(evaluated_expression))

            if isinstance(expression, _parser.Return):
                # Raise an exception for returns so that in the case of early returns (e.g., a return in an if-else
                # block), the rest of the AST below that return block is ignored. Without throwing an exception,
                # the following code would return "false" instead of "true", which is the expected return value.
                # ```
                # if 1 == 1 {
                #     return true;
                # };
                # return false;
                # ```
                raise ReturnException(evaluated_expression)

        # TODO: Figure out how to handle returns for both REPL and regular code execution
        if len(evaluated_expressions) == 0:
            return _parser.NoReturn()
        return evaluated_expressions

    def validate_expression(self, expression):
        value: Token = self.evaluate_expression(expression)
        if isinstance(value, _parser.NoReturn):
            raise_error(value.line_num, "cannot evaluate expression that returns no value")
        return value

    def evaluate_expression(self, expression):
        if type(expression) == _parser.BinaryOperation:
            return self.evaluate_binary_expression(expression)

        elif type(expression) == _parser.UnaryOperation:
            return self.evaluate_unary_expression(expression)

        elif type(expression) == _parser.IfStatement:
            return self.evaluate_if_statement(expression)

        elif type(expression) == _parser.AssignVariable:
            return self.evaluate_assign_variable(expression)

        elif type(expression) == _parser.AssignFunction:
            return self.evaluate_assign_function(expression)

        elif type(expression) == _parser.Identifier:
            return self.evaluate_identifier(expression)

        elif type(expression) == _parser.FunctionCall:
            return self.evaluate_function_call(expression)

        elif type(expression) == _parser.Loop:
            return self.evaluate_loop_statement(expression)

        elif type(expression) == _parser.Print:
            return self.evaluate_print_statement(expression)

        elif type(expression) == _parser.Type:
            return self.evaluate_type_expression(expression)

        elif type(expression) == _parser.Random:
            return Token(str(random.random()), FLOAT, expression.line_num)

        elif type(expression) == _parser.Integer:
            return expression.token

        elif type(expression) == _parser.Float:
            return expression.token

        elif type(expression) == _parser.Boolean:
            return expression.token

        elif type(expression) == _parser.String:
            return expression.token

        elif type(expression) == _parser.Dictionary:
            return self.evaluate_dictionary_expression(expression)

        elif type(expression) == _parser.Return:
            return self.validate_expression(expression.expr)

        elif type(expression) == _parser.Index:
            return self.evaluate_index_expression(expression)

        elif type(expression) == _parser.ExpressionStatement:
            return self.evaluate_expression(expression.expr)

        else:
            raise Exception(f"Unsupported type: {type(expression)}")

    def evaluate_assign_variable(self, variable_assignment: _parser.AssignVariable) -> Token:  # type: ignore
        variable = variable_assignment.name

        if isinstance(variable, _parser.Identifier):
            var_value = self.validate_expression(variable_assignment.value)
            self.env.set_var(variable.token.value, var_value)
            return var_value
        elif isinstance(variable, _parser.Index):
            dictionary: _parser.DictionaryToken = self.validate_expression(variable.left)
            if dictionary.type != DICTIONARY:
                raise_error(dictionary.line_num, f"Expected {DICTIONARY}, got {dictionary.type}")

            # Evaluate each key in the list of unevaluated
            evaluated_keys = [self.evaluate_expression(key) for key in variable.index]
            value = self.evaluate_expression(variable_assignment.value)
            dictionary.update(evaluated_keys, value)

            return _parser.NoReturn(line_num=dictionary.line_num)
        else:
            variable_type = variable_assignment.name.type  # type: ignore
            raise_error(variable_assignment.name.line_num, f"Cannot assign value to type {variable_type}")  # type: ignore

    def evaluate_assign_function(self, function_definition: _parser.AssignFunction) -> Token:
        self.env.set_func(function_definition.name.value, function_definition)
        return _parser.NoReturn(line_num=function_definition.name.line_num)

    def evaluate_identifier(self, identifier: _parser.Identifier) -> Token:  # type: ignore
        # For variables, check the current environment. If it does not exist, check the parent environment.
        # Continue doing this until there are no more parent environments. If the variable does not exist in all
        # scopes, it does not exist anywhere in the code.
        env = self.env
        while env is not None:
            variable_value = env.get_var(identifier.token.value)
            if variable_value is not None:
                return variable_value
            env = env.parent_env

        raise_error(identifier.token.line_num, r"Undefined variable: {expression.token.value}")

    def evaluate_function_call(self, function_call: _parser.FunctionCall) -> Token:
        function_name = function_call.name.value

        function: typing.Optional[_parser.AssignFunction] = None
        env = self.env
        while env is not None:
            f = env.get_func(function_call.name.value)
            if f is not None:
                function = f
            env = env.parent_env

        # If the function is not defined in the functions dictionary, throw an error saying the
        # function is undefined
        if function is None:
            raise_error(function_call.name.line_num, f"Undefined function: {function_name}")

        parameter_identifiers = function.parameters  # type: ignore
        parameter_values = function_call.parameter_values

        if len(parameter_identifiers) != len(parameter_values):
            error_msg = "Incorrect number of arguments. "
            error_msg += f"Function '{function_name}' defined with {len(parameter_identifiers)} parameters "
            error_msg += f"({', '.join(map(lambda t: t.value, parameter_identifiers))}), "
            error_msg += f"but {len(parameter_values)} given."
            raise_error(function_call.name.line_num, error_msg)

        # Map the parameters to their values and set them in the variables dictionary
        evaluated_param_values = {}
        for param_name, param_value in zip(parameter_identifiers, parameter_values):
            evaluated_param_values[param_name.value] = self.validate_expression(param_value)

        # Create a new environment for the function's variables
        self.env = Environment(parent_env=self.env)
        self.env.set_vars(evaluated_param_values)

        # Evaluate every expression in the function body
        statements = function.statements  # type: ignore

        try:
            # If a ReturnException is never thrown, then the function does not return anything.
            self.evaluate_statements(statements)
            return _parser.NoReturn(line_num=function_call.name.line_num)
        except ReturnException as return_exception:
            # If a ReturnException is thrown, return the value of the evaluated expression in the return statement
            return_token = return_exception.token
            return_token.line_num = function_call.name.line_num
            return return_token
        finally:
            # After the function is called, switch to the parent environment
            self.env = self.env.parent_env

    def evaluate_loop_statement(self, loop: _parser.Loop) -> Token:
        while self.validate_expression(loop.condition).value == get_token_literal("TRUE"):
            self.evaluate_statements(loop.statements)
        return _parser.NoReturn()

    def evaluate_if_statement(self, if_statement: _parser.IfStatement) -> Token:
        evaluated_comparison = self.validate_expression(if_statement.comparison)
        if evaluated_comparison.value == get_token_literal("TRUE"):
            return self.evaluate_statements(if_statement.true_statements)
        elif if_statement.false_statements is not None:
            return self.evaluate_statements(if_statement.false_statements)
        return _parser.NoReturn()

    def evaluate_print_statement(self, _print: _parser.Print) -> Token:
        evaluated_params = []
        for param in _print.params:
            result = self.validate_expression(param)
            evaluated_params.append(str(result))
        print(" ".join(evaluated_params))
        return _parser.NoReturn(line_num=_print.line_num)

    def evaluate_type_expression(self, _type: _parser.Type) -> Token:
        num_args = len(_type.params)
        if num_args != 1:
            raise_error(_type.line_num, f"Expected 1 argument; got {num_args}")

        result = self.validate_expression(_type.params[0])
        return Token(result.type, result.type, _type.line_num)

    def evaluate_index_expression(self, index: _parser.Index) -> Token:
        dictionary_token: _parser.DictionaryToken = self.evaluate_expression(index.left)
        if dictionary_token.type != DICTIONARY:
            raise_error(dictionary_token.line_num, f"Expected {DICTIONARY}, got {dictionary_token.type}")

        key = self.validate_expression(index.index)
        value = dictionary_token.get(key)
        if value is None:
            raise_error(key.line_num, f"No key in dictionary: {str(key)}")

        # mypy error: Argument 2 to "set" of "DictionaryToken" has incompatible type "Optional[Token]"; expected "Token"
        # Reason for ignore: 'value' will never be None because an exception is thrown when that value is None
        dictionary_token.set(key, value)  # type: ignore

        # mypy expects an Optional[Token] because 'value' can be None. However, an exception is throws if 'value'
        # is None, so the return type will always be a Token.
        return value  # type: ignore

    def evaluate_dictionary_expression(self, dictionary: _parser.Dictionary) -> _parser.DictionaryToken:
        data = {}
        for key, value in zip(dictionary.keys, dictionary.values):
            eval_key = self.validate_expression(key)
            eval_value = self.validate_expression(value)
            data[eval_key] = eval_value
        return _parser.DictionaryToken(data, dictionary.line_num)

    def evaluate_unary_expression(self, unary_expression):
        expression_result = self.validate_expression(unary_expression.expression)
        op_type = unary_expression.op.type

        valid_type = self.valid_operation_types.get(op_type, [])
        if expression_result.type not in valid_type:
            raise Exception(f"Cannot perform {op_type} operation on {expression_result.type}")

        actual_value = self.get_literal_value(expression_result)

        if op_type == PLUS:
            return Token(str(actual_value), INTEGER, expression_result.line_num)
        elif op_type == MINUS:
            return Token(str(-actual_value), INTEGER, expression_result.line_num)
        elif op_type == BANG:
            value = get_token_literal("FALSE") if actual_value else get_token_literal("TRUE")
            return Token(str(value), BOOLEAN, expression_result.line_num)
        else:
            raise Exception(f"Invalid unary operator: {op_type} ({expression_result.op})")

    def evaluate_binary_expression(self, binary_operation):
        left = self.validate_expression(binary_operation.left)
        right = self.validate_expression(binary_operation.right)
        op_type = binary_operation.op.type

        # Check that the types are compatible. If they are not, the operation cannot be performed.
        #
        # Without this check, someone could run "1 == true" or "false != 2". Both checks are technically valid, but
        # this is invalid because the data types for the left and right expressions are not compatible. However,
        # to account for the fact that some expressions can result in different data types (e.g., two integers resulting
        # in a float, like 3 / 4), we need to allow operations to happen on compatible data types, like floats and
        # integers.
        left_compatible_types = self.compatible_types_for_operations.get(left.type, [])
        right_compatible_types = self.compatible_types_for_operations.get(right.type, [])

        if left.type not in right_compatible_types or right.type not in left_compatible_types:
            raise Exception(f"Cannot perform {op_type} operation on {left.type} and {right.type}")

        # Check that the operation can be performed on the given types. For example, "true > false" is not valid
        valid_type = self.valid_operation_types.get(op_type, [])
        if left.type not in valid_type or right.type not in valid_type:
            raise Exception(f"Cannot perform {op_type} operation on {left.type} and {right.type}")

        left_val = self.get_literal_value(left)
        right_val = self.get_literal_value(right)

        # Math operations
        if op_type == PLUS:
            result = left_val + right_val
            return Token(str(result), self.get_type(result), left.line_num)
        elif op_type == MINUS:
            result = left_val - right_val
            return Token(str(result), self.get_type(result), left.line_num)
        elif op_type == MULTIPLY:
            result = left_val * right_val
            return Token(str(result), self.get_type(result), left.line_num)
        elif op_type == DIVIDE:
            if right_val == 0:
                raise Exception("Division by zero")
            result = left_val / right_val
            return Token(str(left_val / right_val), self.get_type(result), left.line_num)

        # Binary comparisons
        elif op_type == EQ:
            result = left_val == right_val
            value = get_token_literal("TRUE") if result else get_token_literal("FALSE")
            return Token(str(value), BOOLEAN, left.line_num)
        elif op_type == NE:
            result = left_val != right_val
            value = get_token_literal("TRUE") if result else get_token_literal("FALSE")
            return Token(str(value), BOOLEAN, left.line_num)
        elif op_type == GT:
            result = left_val > right_val
            value = get_token_literal("TRUE") if result else get_token_literal("FALSE")
            return Token(str(value), BOOLEAN, left.line_num)
        elif op_type == GE:
            result = left_val >= right_val
            value = get_token_literal("TRUE") if result else get_token_literal("FALSE")
            return Token(str(value), BOOLEAN, left.line_num)
        elif op_type == LT:
            result = left_val < right_val
            value = get_token_literal("TRUE") if result else get_token_literal("FALSE")
            return Token(str(value), BOOLEAN, left.line_num)
        elif op_type == LE:
            result = left_val <= right_val
            value = get_token_literal("TRUE") if result else get_token_literal("FALSE")
            return Token(str(value), BOOLEAN, left.line_num)
        elif op_type == AND:
            result = left_val and right_val
            value = get_token_literal("TRUE") if result else get_token_literal("FALSE")
            return Token(str(value), BOOLEAN, left.line_num)
        elif op_type == OR:
            result = left_val or right_val
            value = get_token_literal("TRUE") if result else get_token_literal("FALSE")
            return Token(str(value), BOOLEAN, left.line_num)
        else:
            raise Exception(f"Invalid binary operator '{binary_operation.op.value}' at line {binary_operation.op.line_num}")

    def get_literal_value(self, token: Token):
        """Convert token values to their Python values so the comparison can be performed. For example, "1" should be
        converted to an integer, and "true" and "false" should be converted to booleans.
        :param token: a Token object representing a literal (number, boolean, etc.)
        :return: Python's representation of the token value
        """
        if token.type == INTEGER:
            return int(token.value)
        elif token.type == FLOAT:
            return float(token.value)
        elif token.type == BOOLEAN:
            return True if token.value == get_token_literal("TRUE") else False
        elif token.type == STRING:
            return token.value
        elif token.type == DICTIONARY:
            # All token values are stored as strings, so to get the actual dictionary, the Python interpreter
            # needs to evaluate the string.
            return ast.literal_eval(token.value)

        raise_error(token.line_num, f"Unsupported type: {token.type}")

    def get_type(self, value: object) -> str:
        if isinstance(value, float):
            return FLOAT
        elif isinstance(value, int):
            return INTEGER
        elif isinstance(value, dict):
            return DICTIONARY
        else:
            return STRING
