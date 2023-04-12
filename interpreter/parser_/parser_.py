import typing
from interpreter.tokens.tokenizer import Token
from interpreter.tokens.token_queue import TokenQueue
from interpreter.parser_.ast_objects import *
from interpreter.tokens.tokens import *
from interpreter.utils.utils import language_error, unexpected_token_error

# Precedence names
LOWEST = "LOWEST"  # default
ASSIGN = "ASSIGN"
COMPARE = "COMPARE"  # ==, !=, &&, ||, <, >, >=, <=
SUM = "SUM"  # +, -
PRODUCT = "PRODUCT"  # *, /
SEND = "SEND"  # <-


class Parser:

    def __init__(self, tokens: TokenQueue):
        self.tokens = tokens

        # Higher precedence is lower on the list (for example, && and || take precedence above everything, so they have
        # a precedence level of 2.
        #
        # Storing the precedence levels in this list allows precedences to be rearranged without having to manually
        # change other precedence values. For example, if we want to add a precedence before EDGE, we can just add it
        # to this list, and the parser will automatically handle that precedence's integer value (which is the
        # index + 1).
        self.precedences: list[str] = [
            LOWEST,
            ASSIGN,
            COMPARE,
            SUM,
            PRODUCT,
            SEND,
        ]

        self.infix_precedence: dict[str, str] = {
            POINTER: SEND,
            PLUS: SUM,
            MINUS: SUM,
            BANG: SUM,
            OR: SUM,
            AND: SUM,
            MULTIPLY: PRODUCT,
            DIVIDE: PRODUCT,
            EQ: COMPARE,
            NE: COMPARE,
            LT: COMPARE,
            LE: COMPARE,
            GT: COMPARE,
            GE: COMPARE,
        }

    def parse(self) -> list[Expression]:
        return self.parse_statements(EOF)

    def parse_statements(self, end_type: str) -> list[Expression]:
        """Parse statements within a certain scope (set by 'end_type')

        For block statements, that value will be a closed curly bracket. For program statements, that value will be an
        end-of-file token.
        """
        statements = []
        while self.current.type != end_type:
            statements.append(self.expression())
            self.is_expected_token(SEMICOLON)
            self.advance()
        return statements

    def advance(self) -> None:
        self.tokens.next()

    @property
    def peek(self) -> Token:
        return self.tokens.peek()

    @property
    def current(self) -> Token:
        return self.tokens.current

    def get_precedence_level(self, precedence_name: str) -> int:
        """Get the precedence level of a given precedence. The precedences are stores in 'self.precedences' from lowest
        to highest, so the precedence value is just the index + 1, where LOWEST is 1.

        :param precedence_name: precedence name/label (see top of this file above Parser class)
        :return: the precedence level
        """
        return self.precedences.index(precedence_name) + 1

    def get_next_precedence_level(self, precedence_dict: dict[str, str]) -> int:
        """Get the precedence level of the next operator in the expression.

        :param precedence_dict: token-precedence mapping for the next token in the expression
        :return: precedence level for token type in 'precedence_dict'
        """
        precedence_name = precedence_dict.get(self.current.type, LOWEST)
        return self.get_precedence_level(precedence_name)

    def expression(self, precedence_name: str = LOWEST) -> Expression:
        precedence_level = self.get_precedence_level(precedence_name)

        # Prefix
        left = self.parse_prefix()

        # Infix
        while self.current is not None and precedence_level < self.get_next_precedence_level(self.infix_precedence):
            left = self.parse_infix(left)

        return left

    def parse_prefix(self) -> Expression:

        if self.current.type == IDENTIFIER and self.peek.type == ASSIGN:
            return self.parse_assign()

        if self.current.type in [MINUS, PLUS, BANG]:
            return self.parse_unary_expression()

        elif self.current.type == OPEN_PAREN:
            return self.parse_grouped_expression()

        elif self.current.type == NUMBER:
            return self.parse_number()

        elif self.current.type == STRING:
            return self.parse_string()

        elif self.current.type == BOOLEAN:
            return self.parse_boolean()

        elif self.current.type == IDENTIFIER:
            return self.parse_identifier()

        elif self.current.type == FUNCTION:
            return self.parse_function()

        raise language_error(self.current.line_num, f"Invalid token: {self.current.type} ({self.current.value})")

    def parse_infix(self, left: Expression) -> Expression:
        op = self.current
        self.advance()
        right = self.expression(self.infix_precedence.get(op.type, LOWEST))
        return BinaryExpression(op.line_num, left, op, right)

    def parse_number(self) -> Number:
        number_token = self.current
        self.advance()
        return Number(number_token.line_num, float(number_token.value))

    def parse_string(self) -> String:
        string_token = self.current
        self.advance()
        return String(string_token.line_num, string_token.value)

    def parse_boolean(self) -> Boolean:
        boolean_token = self.current
        self.advance()
        return Boolean(
            boolean_token.line_num,
            boolean_token.value == get_token_literal("TRUE")
        )

    def parse_unary_expression(self) -> UnaryExpression:
        op = self.current
        self.advance()
        expression = self.expression()
        return UnaryExpression(op.line_num, op, expression)

    def parse_grouped_expression(self) -> Expression:
        self.advance()

        # An open paren immediately followed by a closed paren is an empty list
        if self.current.type == CLOSED_PAREN:
            self.advance()
            return List(self.current.line_num, [])

        # If a token other than a closed paren comes after the open paren, parse the expression
        expression = self.expression()

        if self.current.type == CLOSED_PAREN:
            self.advance()
            return expression

        # If the token after the expression is a comma, we're parsing a list
        elif self.current.type == COMMA:
            self.advance()
            return self.parse_list(expression)

        raise unexpected_token_error(self.current.line_num, CLOSED_PAREN, self.current)

    def parse_identifier(self) -> Identifier | BuiltinFunction:
        identifier_token = self.current
        self.advance()

        if identifier_token.value in BuiltinFunction.builtin_function_names:
            return BuiltinFunction(identifier_token.line_num, identifier_token.value)

        return Identifier(identifier_token.line_num, identifier_token.value)

    def parse_assign(self) -> Expression:
        self.is_expected_token(IDENTIFIER)
        variable_name = self.current

        # Skip over assignment operator
        self.advance()

        self.is_expected_token(ASSIGN)

        self.advance()
        right = self.expression()

        return Assignment(variable_name.line_num, variable_name.value, right)

    def parse_list(self, first_expression: Expression) -> List:
        line_num = self.current.line_num
        values = [first_expression]

        while True:
            if self.current.type == CLOSED_PAREN:
                self.advance()
                break

            expression = self.expression(LOWEST)
            values.append(expression)

            if self.current.type == CLOSED_PAREN:
                self.advance()
                break

            self.is_expected_token(COMMA)

            self.advance()

        # Return list object
        return List(line_num, values)

    def parse_function(self) -> Function:
        line_num: int = self.current.line_num
        self.advance()  # skip function keyword

        self.is_expected_token(OPEN_PAREN)
        self.advance()

        params = []
        while True:
            if self.current.type == CLOSED_PAREN:
                self.advance()
                break

            expression = self.expression(LOWEST)

            if not isinstance(expression, Identifier):
                raise language_error(
                    expression.line_num,
                    f"Unsupported type {type(expression)} for function definition parameter. Expected Identifier."
                )

            params.append(expression)

            if self.current.type == CLOSED_PAREN:
                self.advance()
                break

            self.is_expected_token(COMMA)

            self.advance()

        self.is_expected_token(COLON)
        self.advance()

        expression = self.expression(LOWEST)

        return Function(line_num, params, expression)

    def add_semicolon(self) -> None:
        self.tokens.add("SEMICOLON")

    def is_expected_token(self, expected_token_type: str) -> None:
        if self.current.type != expected_token_type:
            raise unexpected_token_error(self.current.line_num, expected_token_type, self.current)
