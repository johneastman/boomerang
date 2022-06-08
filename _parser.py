from tokenizer import *


class TokenValue:
    def __init__(self, token: Token):
        self.token = token

    @property
    def value(self):
        return self.token.value

    @property
    def type(self):
        return self.token.type

    @property
    def line_num(self):
        return self.token.line_num

    def __repr__(self):
        return f"[{self.__class__.__name__}(value={self.value})]"


class Number(TokenValue):
    def __init__(self, token: Token):
        super().__init__(token)


class Boolean(TokenValue):
    def __init__(self, token: Token):
        super().__init__(token)


class Null(TokenValue):
    def __init__(self, token: Token):
        super().__init__(token)


class Identifier(TokenValue):
    def __init__(self, token: Token):
        super().__init__(token)


class Return:
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"[{self.__class__.__name__}(value={self.expression})]"


class AssignFunction:
    def __init__(self, name, parameters, statements):
        self.name = name
        self.parameters = parameters
        self.statements = statements

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"[{class_name}(name={self.name}, parameters={self.parameters}, statements={self.statements})]"


class IfStatement:
    def __init__(self, comparison, true_statements, false_statements):
        self.comparison = comparison
        self.true_statements = true_statements
        self.false_statements = false_statements


class BuiltinFunction:
    def __init__(self, name: Token, params):
        self.name = name
        self.parameters = params

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"[{class_name}(name={self.name}, parameters={self.parameters})]"


class FunctionCall:
    def __init__(self, name: Token, parameter_values):
        self.name = name
        self.parameter_values = parameter_values

    def __repr__(self):
        return f"[{self.__class__.__name__}(name={self.name}, parameter_values={self.parameter_values})]"


class BinaryOperation:
    def __init__(self, left, op: Token, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"[{class_name}(left={self.left}, op={self.op}, right={self.right})]"


class AssignVariable:
    def __init__(self, name: Token, value):
        self.name = name
        self.value = value

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"[{class_name}(name={self.name}, value={self.value})]"


class UnaryOperation:
    def __init__(self, op: Token, expression):
        self.op = op
        self.expression = expression

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"[{class_name}(op={self.op}, expression={self.expression})]"


class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def advance(self):
        self.index += 1

    @property
    def current(self):
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    @property
    def peek(self):
        next_token_index = self.index + 1
        return self.tokens[next_token_index] if next_token_index < len(self.tokens) else None

    def parse(self):
        return self.statements()

    def statements(self):
        ast = []
        while self.current.type != EOF:

            if self.current.type == CLOSED_CURLY_BRACKET:
                # We've reached the end of a function
                break

            result = self.statement()
            if self.current.type != SEMICOLON:
                self.raise_expected_token_error(SEMICOLON)

            self.advance()
            ast.append(result)

        return ast

    def statement(self):
        if self.current.type == LET:
            return self.let_statement()
        elif self.current.type == FUNCTION:
            return self.function()
        elif self.current.type == IF:
            return self.if_statement()
        else:
            return self.expression()

    def if_statement(self):
        self.advance()

        # Open parenthesis
        if self.current.type != OPEN_PAREN:
            self.raise_expected_token_error(OPEN_PAREN)
        self.advance()

        comparison = self.expression()

        # Closed parenthesis
        if self.current.type != CLOSED_PAREN:
            self.raise_expected_token_error(CLOSED_PAREN)
        self.advance()

        # Open curly bracket
        if self.current.type != OPEN_CURLY_BRACKET:
            self.raise_expected_token_error(OPEN_CURLY_BRACKET)
        self.advance()

        if_statements = self.statements()

        # Closed curly bracket
        if self.current.type != CLOSED_CURLY_BRACKET:
            self.raise_expected_token_error(CLOSED_CURLY_BRACKET)
        self.advance()

        else_statements = None
        if self.current.type == ELSE:
            self.advance()

            # Open curly bracket
            if self.current.type != OPEN_CURLY_BRACKET:
                self.raise_expected_token_error(OPEN_CURLY_BRACKET)
            self.advance()

            else_statements = self.statements()

            # Closed curly bracket
            if self.current.type != CLOSED_CURLY_BRACKET:
                self.raise_expected_token_error(CLOSED_CURLY_BRACKET)
            self.advance()

        return IfStatement(comparison, if_statements, else_statements)

    def function(self):
        self.advance()

        if self.current.type != IDENTIFIER:
            self.raise_expected_token_error(IDENTIFIER)
        function_name = self.current
        self.advance()

        if self.current.type != OPEN_PAREN:
            self.raise_expected_token_error(OPEN_PAREN)
        self.advance()

        parameters = []
        # This condition in after 'while' handles functions with no parameters. If this was set to 'while True',
        # the parser would expect a NUMBER after the open-paren of the function call and throw the error
        # in `if self.current.type != NUMBER`.
        while self.current.type != CLOSED_PAREN:
            if self.current.type != IDENTIFIER:
                self.raise_expected_token_error(IDENTIFIER)
            parameters.append(self.current)
            self.advance()

            if self.current.type == CLOSED_PAREN:
                break

            if self.current.type != COMMA:
                self.raise_expected_token_error(COMMA)
            self.advance()

        self.advance()

        if self.current.type != OPEN_CURLY_BRACKET:
            self.raise_expected_token_error(OPEN_CURLY_BRACKET)
        self.advance()

        function_statements = self.statements()

        if self.current.type != CLOSED_CURLY_BRACKET:
            self.raise_expected_token_error(CLOSED_CURLY_BRACKET)
        self.advance()

        return AssignFunction(function_name, parameters, function_statements)

    def let_statement(self):
        self.advance()
        if self.current.type != IDENTIFIER:
            self.raise_expected_token_error(IDENTIFIER)
        variable_name_token = self.current

        self.advance()
        if self.current.type != ASSIGN:
            self.raise_expected_token_error(ASSIGN)

        self.advance()
        variable_value = self.expression()

        return AssignVariable(variable_name_token, variable_value)

    def binary_expression(self, binary_operators: list, next_method):
        left = next_method()

        while True:
            if self.current is None:
                return left
            elif self.current.type in binary_operators:
                op = self.current
                self.advance()
                right = next_method()
                left = BinaryOperation(left, op, right)
            else:
                break

        return left

    def expression(self):
        return self.binary_expression([
            AND, OR
        ], self.boolean)

    def boolean(self):
        return self.binary_expression([
            EQ,
            NE,
            GE,
            GT,
            LE,
            LT
        ], self.addition)

    def addition(self):
        return self.binary_expression([
            PLUS,
            MINUS
        ], self.term)

    def term(self):
        return self.binary_expression([
            MULTIPLY,
            DIVIDE
        ], self.factor)

    def factor(self):
        if self.current.type in [MINUS, PLUS, BANG]:
            op = self.current
            self.advance()
            expression = self.expression()
            return UnaryOperation(op, expression)

        elif self.current.type == OPEN_PAREN:
            self.advance()
            expression = self.expression()
            if self.current.type == CLOSED_PAREN:
                self.advance()
                return expression
            self.raise_expected_token_error(CLOSED_PAREN)

        elif self.current.type == NUMBER:
            number_token = self.current
            self.advance()
            return Number(number_token)

        elif self.current.type == NULL:
            null_token = self.current
            self.advance()
            return Null(null_token)

        elif self.current.type == BOOLEAN:
            bool_val_token = self.current
            self.advance()
            return Boolean(bool_val_token)

        elif self.current.type == IDENTIFIER:
            identifier_token = self.current
            if self.peek.type == OPEN_PAREN:
                return self.function_call(identifier_token)
            else:
                self.advance()
                return Identifier(identifier_token)

        elif self.current.type == RETURN:
            self.advance()
            return Return(self.expression())

        else:
            raise Exception(f"Invalid token: {self.current}")

    def function_call(self, identifier_token):
        self.advance()
        self.advance()

        parameters = []
        # This condition in after 'while' handles functions with no parameters. If this was set to 'while True',
        # the parser would expect a NUMBER after the open-paren of the function call and throw the error.
        # in `if self.current.type != NUMBER`.
        while self.current.type != CLOSED_PAREN:
            parameters.append(self.expression())

            if self.current.type == CLOSED_PAREN:
                break

            if self.current.type != COMMA:
                self.raise_expected_token_error(" or ".join([COMMA, CLOSED_PAREN]))
            self.advance()

        self.advance()

        builtin_functions = [
            "print"
        ]

        # For built-in function calls, return a BuiltinFunction object.
        if identifier_token.value in builtin_functions:
            return BuiltinFunction(identifier_token, parameters)
        return FunctionCall(identifier_token, parameters)

    def raise_expected_token_error(self, expected_token_type):
        raise Exception(f"Expected {expected_token_type}, got {self.current.type} ({self.current.value})")

