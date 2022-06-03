import _parser
import tokenizer

# TODO: Return a Value object for values (numbers, booleans, etc.) instead of the raw value so we can check the type
#  and throw errors for incompatible types in comparison operators.
GLOBAL = "GLOBAL"


class Environment:
    def __init__(self, parent_env):
        self.variables = {}
        self.parent_env = parent_env


class Evaluator:
    def __init__(self, ast):
        self.ast = ast
        self.variables = {}
        self.functions = {}
        self.current_scope = GLOBAL

        self.env = {
            GLOBAL: {}
        }

        # Global scope: functions and variables defined outside functions (in the main file)
        # Each function has its own scope with its own variables

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
                return int(self.evaluate_expression(expression.left) / self.evaluate_expression(expression.right))
            elif expression.op.type == tokenizer.EQ:
                return self.evaluate_expression(expression.left) == self.evaluate_expression(expression.right)
            elif expression.op.type == tokenizer.NOT_EQ:
                return self.evaluate_expression(expression.left) != self.evaluate_expression(expression.right)
            elif expression.op.type == tokenizer.GREATER_EQUAL:
                return self.evaluate_expression(expression.left) >= self.evaluate_expression(expression.right)
            elif expression.op.type == tokenizer.GREATER:
                return self.evaluate_expression(expression.left) > self.evaluate_expression(expression.right)
            elif expression.op.type == tokenizer.LESS_EQ:
                return self.evaluate_expression(expression.left) <= self.evaluate_expression(expression.right)
            elif expression.op.type == tokenizer.LESS:
                return self.evaluate_expression(expression.left) < self.evaluate_expression(expression.right)
            else:
                raise Exception(f"Invalid binary operator '{expression.op.value}' at line {expression.op.line_num}")

        elif type(expression) == _parser.UnaryOperation:
            if expression.op.type == tokenizer.PLUS:
                return self.evaluate_expression(expression.expression)
            elif expression.op.type == tokenizer.MINUS:
                return -self.evaluate_expression(expression.expression)
            elif expression.op.type == tokenizer.BANG:
                return not self.evaluate_expression(expression.expression)
            else:
                raise Exception(f"Invalid unary operator: {expression.op.type} ({expression.op})")

        elif type(expression) == _parser.AssignVariable:
            self.env[self.current_scope][expression.name.value] = self.evaluate_expression(expression.value)
            return "null"

        elif type(expression) == _parser.AssignFunction:
            self.functions[expression.name.value] = expression
            return "null"

        elif type(expression) == _parser.Identifier:
            variables = self.env[self.current_scope]
            variable_value = variables.get(expression.value, None)
            if variable_value is None:
                raise Exception(f"Undefined variable at line {expression.line_num}: {expression.value}")
            return variable_value

        elif type(expression) == _parser.FunctionCall:
            function_name = expression.name.value
            function = self.functions.get(function_name, None)

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

            self.current_scope = function_name
            self.env[self.current_scope] = {}
            # Map the parameters to their values and set them in the variables dictionary
            for param_name, param_value in zip(parameter_identifiers, parameter_values):
                self.evaluate_expression(_parser.AssignVariable(param_name, param_value))

            # Evaluate every expression in the function body
            statements = function.statements
            executed_expressions = [self.evaluate_expression(expression) for expression in statements]

            self.current_scope = GLOBAL

            return executed_expressions[-1] if type(statements[-1]) == _parser.Return else "null"

        elif type(expression) == _parser.BuiltinFunction:
            if expression.name == "print":
                evaluated_params = []
                for param in expression.parameters:
                    result = self.evaluate_expression(param)
                    evaluated_params.append(result)

                print(", ".join(map(str, evaluated_params)))
            return "null"

        elif type(expression) == _parser.Number:
            return int(expression.value)

        elif type(expression) == _parser.Boolean:
            return True if expression.type == tokenizer.TRUE else False

        elif type(expression) == _parser.Return:
            return self.evaluate_expression(expression.expression)
