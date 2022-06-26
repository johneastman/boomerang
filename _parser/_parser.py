from tokens.tokens import *
from .ast_objects import *


class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

        self.assignment_operators = [
            ASSIGN,
            ASSIGN_ADD,
            ASSIGN_SUB,
            ASSIGN_MUL,
            ASSIGN_DIV
        ]

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
        ast = []
        while self.current.type != EOF:

            result = self.statement()
            if self.current.type != SEMICOLON:
                self.raise_expected_token_error(SEMICOLON)

            self.advance()
            ast.append(result)

        return ast

    def block_statement(self):
        """Statements between two curly brackets (functions, if-statements, loops, etc.)"""
        statements = []
        while self.current.type != CLOSED_CURLY_BRACKET:
            statements.append(self.statement())

            if self.current.type != SEMICOLON:
                self.raise_expected_token_error(SEMICOLON)
            self.advance()
        return statements

    def statement(self):
        if self.current.type == FUNCTION:
            return self.function()

        elif self.current.type == IF:
            return self.if_statement()

        elif self.current.type == RETURN:
            self.advance()
            return Return(self.expression())

        elif self.current.type == WHILE:
            return self.loop()

        else:
            return self.expression()

    def assign(self, left):
        assignment_operator = self.current
        self.advance()
        right = self.expression()

        if assignment_operator.type == ASSIGN:
            return AssignVariable(left, right)
        else:
            operator_token = {
                ASSIGN_ADD: Token(get_token_literal("PLUS"), PLUS, assignment_operator.line_num),
                ASSIGN_SUB: Token(get_token_literal("MINUS"), MINUS, assignment_operator.line_num),
                ASSIGN_MUL: Token(get_token_literal("MULTIPLY"), MULTIPLY, assignment_operator.line_num),
                ASSIGN_DIV: Token(get_token_literal("DIVIDE"), DIVIDE, assignment_operator.line_num)
            }

            return AssignVariable(
                left,
                BinaryOperation(
                    left,
                    operator_token.get(assignment_operator.type),
                    right
                )
            )

    def loop(self):
        self.advance()

        comparison = self.expression()

        # Open curly bracket
        if self.current.type != OPEN_CURLY_BRACKET:
            self.raise_expected_token_error(OPEN_CURLY_BRACKET)
        self.advance()

        loop_statements = self.block_statement()

        # Closed curly bracket
        if self.current.type != CLOSED_CURLY_BRACKET:
            self.raise_expected_token_error(CLOSED_CURLY_BRACKET)
        self.advance()

        # Add a semicolon so users don't have to add one in the code
        self.add_semicolon()

        return Loop(comparison, loop_statements)

    def if_statement(self):
        self.advance()

        comparison = self.expression()

        # Open curly bracket
        if self.current.type != OPEN_CURLY_BRACKET:
            self.raise_expected_token_error(OPEN_CURLY_BRACKET)
        self.advance()

        if_statements = self.block_statement()

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

            else_statements = self.block_statement()

            # Closed curly bracket
            if self.current.type != CLOSED_CURLY_BRACKET:
                self.raise_expected_token_error(CLOSED_CURLY_BRACKET)
            self.advance()

        self.add_semicolon()

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

        function_statements = self.block_statement()

        if self.current.type != CLOSED_CURLY_BRACKET:
            self.raise_expected_token_error(CLOSED_CURLY_BRACKET)
        self.advance()

        self.add_semicolon()

        return AssignFunction(function_name, parameters, function_statements)

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
            elif self.current.type == OPEN_BRACKET:
                self.advance()
                value = self.expression()
                if self.current.type != CLOSED_BRACKET:
                    self.raise_expected_token_error(CLOSED_BRACKET)
                self.advance()
                return Index(left, value)
            elif self.current.type in self.assignment_operators:
                return self.assign(left)
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

        elif self.current.type == INTEGER:
            number_token = self.current
            self.advance()
            return Number(number_token)

        elif self.current.type == FLOAT:
            float_token = self.current
            self.advance()
            return Float(float_token)

        elif self.current.type == BOOLEAN:
            bool_val_token = self.current
            self.advance()
            return Boolean(bool_val_token)

        elif self.current.type == STRING:
            string_val = self.current
            self.advance()
            return String(string_val)

        elif self.current.type == IDENTIFIER:
            identifier_token = self.current
            if self.peek.type == OPEN_PAREN:
                return self.function_call(identifier_token)
            else:
                self.advance()
                return Identifier(identifier_token)

        elif self.current.type == OPEN_CURLY_BRACKET:
            line_num = self.current.line_num
            self.advance()
            keys = []
            values = []
            while self.current.type != CLOSED_CURLY_BRACKET:
                keys.append(self.expression())

                if self.current.type != COLON:
                    self.raise_expected_token_error(COLON)
                self.advance()

                values.append(self.expression())

                if self.current.type == CLOSED_CURLY_BRACKET:
                    break

                if self.current.type != COMMA:
                    self.raise_expected_token_error(COMMA)
                self.advance()

            self.advance()
            return Dictionary(keys, values, line_num)

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

        builtin_functions = {
            "print": Print(parameters, identifier_token.line_num),
            "type": Type(parameters)
        }
        return builtin_functions.get(identifier_token.value, FunctionCall(identifier_token, parameters))

    def raise_expected_token_error(self, expected_token_type):
        raise Exception(
            f"Expected {expected_token_type}, got {self.current.type} ('{self.current.value}') on line {self.current.line_num}")

    def add_semicolon(self):
        semicolon_label = "SEMICOLON"
        self.tokens.insert(
            self.index,
            Token(get_token_literal(semicolon_label), get_token_type(semicolon_label), self.current.line_num)
        )
