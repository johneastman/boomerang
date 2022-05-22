import _parser
import tokenizer


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
            else:
                raise Exception(f"Invalid binary operator: {expression.op}")

        elif type(expression) == _parser.UnaryOperation:
            if expression.op.type == tokenizer.PLUS:
                return self.evaluate_expression(expression.expression)
            elif expression.op.type == tokenizer.MINUS:
                return -self.evaluate_expression(expression.expression)
            else:
                raise Exception(f"Invalid unary operator: {expression.op.type} ({expression.op})")

        elif type(expression) == _parser.AssignVariable:
            self.variables[expression.name] = self.evaluate_expression(expression.value)

        elif type(expression) == _parser.AssignFunction:
            function_parameters = expression.parameters
            self.functions[expression.name] = {"params": function_parameters, "statements": expression.statements}
            for i, param in enumerate(function_parameters):
                self.variables[param] = param

        elif type(expression) == _parser.Identifier:
            variable_value = self.variables.get(expression.name_token.value, None)
            if variable_value is None:
                raise Exception(f"Undefined variable: {expression.name_token.value}")
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
            return int(expression.value_token.value)

        elif type(expression) == _parser.Return:
            return self.evaluate_expression(expression.expression)
