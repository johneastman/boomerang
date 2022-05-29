import _parser
import tokenizer

# TODO: Return a Value object for values (numbers, booleans, etc.) instead of the raw value so we can check the type
#  and throw errors for incompatible types in comparison operators.


class Evaluator:
    def __init__(self, ast):
        self.ast = ast
        self.variables = {}
        self.functions = {}

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
            self.variables[expression.name.value] = self.evaluate_expression(expression.value)

        elif type(expression) == _parser.AssignFunction:
            function_parameters = expression.parameters
            self.functions[expression.name] = {"params": function_parameters, "statements": expression.statements}
            for i, param in enumerate(function_parameters):
                self.variables[param] = param

        elif type(expression) == _parser.Identifier:
            variable_value = self.variables.get(expression.value, None)
            if variable_value is None:
                raise Exception(f"Undefined variable '{expression.value}' at line {expression.line_num}")
            return variable_value

        elif type(expression) == _parser.FunctionCall:
            function = self.functions.get(expression.name, None)

            # If the function is not defined in the functions dictionary, throw an error saying the
            # function is undefined
            if function is None:
                raise Exception(f"Undefined function: {expression.name}")

            # Map the parameters to their values and set them in the variables dictionary
            for param_name, param_value in zip(function["params"], expression.parameter_values):
                self.evaluate_expression(_parser.AssignVariable(param_name, param_value))

            # Evaluate every expression in the function body
            # TODO: Retrieve the last value in this list to get the returned value
            statements = function["statements"]
            executed_expressions = [self.evaluate_expression(expression) for expression in statements]

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
