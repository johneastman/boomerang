import tokens


class Node:

    def __init__(self, token):
        self.token = token

    def token_literal(self):
        return self.token.literal

    def string(self):
        return self.token_literal()


class Identifier(Node):
    def __init__(self, token, value):
        super().__init__(token)
        self.value = value

    def string(self):
        return f"{self.value}"


class LetStatement(Node):

    def __init__(self, token: tokens.Token, name: Identifier, expression):
        super().__init__(token)
        self.name = name
        self.expression = expression

    def string(self):
        return f"{super().string()} {self.name.value} = {self.expression}"


class ReturnStatement(Node):
    def __init__(self, token, expression):
        super().__init__(token)
        self.expression = expression

    def string(self):
        return f"{super().string()} {self.expression}"


class ExpressionStatement(Node):
    def __init__(self, token, expression):
        super().__init__(token)
        self.expression = expression

    def string(self):
        return self.expression


class Program:
    def __init__(self):
        self.statements = []

    def token_literal(self):
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        else:
            return ""


class Parser:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.curr_token = None
        self.peek_token = None
        self.errors = []

        self.next_token()
        self.next_token()

    def peek_error(self, token_type):
        msg = f"expected next token to be {token_type} but got {self.peek_token.type} instead."
        self.errors.append(msg)

    def next_token(self):
        self.curr_token = self.peek_token
        self.peek_token = self.tokenizer.next_token()

    def parse_program(self):
        program = Program()

        while self.curr_token.type != tokens.EOF:
            statement = self.parse_statement()
            if statement is not None:
                program.statements.append(statement)

            self.next_token()

        return program

    def parse_statement(self):
        if self.curr_token.type == tokens.LET:
            return self.parse_let_statement()
        elif self.curr_token.type == tokens.RETURN:
            return self.parse_return_statement()
        else:
            return None

    def parse_let_statement(self):
        let_token = self.curr_token

        if not self.expect_peek(tokens.IDENT):
            return None

        identifier_token = self.curr_token

        if not self.expect_peek(tokens.ASSIGN):
            return None

        # TODO: Skipping expressions for now
        while not self.curr_token.type == tokens.SEMICOLON:
            self.next_token()

        ident = Identifier(identifier_token, identifier_token.literal)
        return LetStatement(let_token, ident, None)

    def parse_return_statement(self):

        return_statement = ReturnStatement(self.curr_token, None)

        self.next_token()

        # TODO: Skipping expressions for now
        while not self.curr_token.type == tokens.SEMICOLON:
            self.next_token()

        return return_statement

    def expect_peek(self, token_type):
        if self.peek_token.type == token_type:
            self.next_token()
            return True

        self.peek_error(token_type)
        return False

