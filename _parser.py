import tokenizer


class Number:
    def __init__(self, value_token):
        self.value_token = value_token

    def __repr__(self):
        return f"[{self.__class__.__name__}(value={self.value_token.value})]"


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


class Identifier:
    def __init__(self, name_token):
        self.name_token = name_token

    def __repr__(self):
        return f"[{self.__class__.__name__}(value={self.name_token.value})]"


class FunctionCall:
    def __init__(self, name, parameter_values):
        self.name = name
        self.parameter_values = parameter_values

    def __repr__(self):
        return f"[{self.__class__.__name__}(name={self.name}, parameter_values={self.parameter_values})]"


class BinaryOperation:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"[{class_name}(left={self.left}, op={self.op}, right={self.right})]"


class AssignVariable:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"[{class_name}(name={self.name}, value={self.value})]"


class UnaryOperation:
    def __init__(self, op, expression):
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
        while self.current.type != tokenizer.EOF:

            if self.current.type == tokenizer.CLOSED_CURLY_BRACKET:
                # We've reached the end of a function
                break

            result = self.statement()
            if self.current.type != tokenizer.SEMICOLON:
                self.raise_expected_token_error(tokenizer.SEMICOLON)

            self.advance()
            ast.append(result)

        return ast

    def statement(self):
        if self.current.type == tokenizer.LET:
            return self.let_statement()
        elif self.current.type == tokenizer.FUNCTION:
            return self.function()
        else:
            return self.expression()

    def function(self):
        self.advance()

        if self.current.type != tokenizer.IDENTIFIER:
            self.raise_expected_token_error(tokenizer.IDENTIFIER)
        function_name = self.current.value
        self.advance()

        if self.current.type != tokenizer.OPEN_PAREN:
            self.raise_expected_token_error(tokenizer.OPEN_PAREN)
        self.advance()

        parameters = self.parse_function_header(tokenizer.IDENTIFIER)

        self.advance()

        if self.current.type != tokenizer.OPEN_CURLY_BRACKET:
            self.raise_expected_token_error(tokenizer.OPEN_CURLY_BRACKET)
        self.advance()

        function_statements = self.statements()

        if self.current.type != tokenizer.CLOSED_CURLY_BRACKET:
            self.raise_expected_token_error(tokenizer.CLOSED_CURLY_BRACKET)
        self.advance()

        return AssignFunction(function_name, parameters, function_statements)

    def let_statement(self):
        self.advance()
        if self.current.type != tokenizer.IDENTIFIER:
            self.raise_expected_token_error(tokenizer.IDENTIFIER)
        variable_name = self.current.value

        self.advance()
        if self.current.type != tokenizer.ASSIGN:
            self.raise_expected_token_error(tokenizer.ASSIGN)

        self.advance()
        variable_value = self.expression()

        return AssignVariable(variable_name, variable_value)

    def expression(self):
        left = self.term()
        while True:
            if self.current is None:
                return left
            elif self.current.type in [tokenizer.PLUS, tokenizer.MINUS]:
                op = self.current
                self.advance()
                right = self.term()
                left = BinaryOperation(left, op, right)
            else:
                break

        return left

    def term(self):
        left = self.factor()
        while True:
            if self.current is None:
                return left
            elif self.current.type in [tokenizer.MULTIPLY, tokenizer.DIVIDE]:
                op = self.current
                self.advance()
                right = self.factor()
                left = BinaryOperation(left, op, right)
            else:
                break

        return left

    def factor(self):
        if self.current.type == tokenizer.MINUS:
            op = self.current
            self.advance()
            expression = self.expression()
            return UnaryOperation(op, expression)
        elif self.current.type == tokenizer.OPEN_PAREN:
            self.advance()
            expression = self.expression()
            if self.current.type == tokenizer.CLOSED_PAREN:
                self.advance()
                return expression
            self.raise_expected_token_error(tokenizer.OPEN_PAREN)
        elif self.current.type == tokenizer.NUMBER:
            number_token = self.current
            self.advance()
            return Number(number_token)
        elif self.current.type == tokenizer.IDENTIFIER:
            identifier_token = self.current

            if self.peek.type == tokenizer.OPEN_PAREN:
                self.advance()
                self.advance()

                params = self.parse_function_header(tokenizer.NUMBER)

                self.advance()
                return FunctionCall(identifier_token.value, params)
            else:
                self.advance()
                return Identifier(identifier_token)
        elif self.current.type == tokenizer.RETURN:
            self.advance()
            return Return(self.expression())
        else:
            raise Exception(f"Invalid token: {self.current}")

    def parse_function_header(self, expected_parameter_type):
        params = []

        # This condition in after 'while' handles functions with no parameters. If this was set to 'while True',
        # the parser would expect a NUMBER after the open-paren of the function call and throw the error
        # in `if self.current.type != tokenizer.NUMBER`.
        while self.current.type != tokenizer.CLOSED_PAREN:
            if self.current.type != expected_parameter_type:
                self.raise_expected_token_error(tokenizer.NUMBER)
            params.append(self.current.value)
            self.advance()

            if self.current.type == tokenizer.CLOSED_PAREN:
                break

            if self.current.type != tokenizer.COMMA:
                self.raise_expected_token_error(tokenizer.COMMA)
            self.advance()
        return params

    def raise_expected_token_error(self, expected_token_type):
        raise Exception(f"Expected {expected_token_type}, got {self.current.type} ({self.current.value})")

