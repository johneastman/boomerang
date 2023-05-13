from copy import copy

from interpreter.tokens.token_queue import TokenQueue
from interpreter.tokens.token import Token
import interpreter.parser_.ast_objects as o
from interpreter.tokens import tokens as t
from utils.utils import language_error, unexpected_token_error

# Precedence names
LOWEST = "LOWEST"  # default
COMPARE = "COMPARE"  # ==, !=, <, >, >=, <=
BOOLEAN = "BOOLEAN"  # and, or, xor, in
SUM = "SUM"  # +, -
PRODUCT = "PRODUCT"  # *, /
POWER = "POWER"  # **
PREFIX = "PREFIX"  # Before an expression: !, -, +
POSTFIX = "POSTFIX"  # after an expression: !, --, ++
SEND = "SEND"  # <-
INDEX = "INDEX"  # @


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
            BOOLEAN,
            COMPARE,
            INDEX,
            SEND,
            SUM,
            PRODUCT,
            POWER,
            PREFIX,
            POSTFIX
        ]

        self.infix_precedence: dict[str, str] = {
            t.SEND: SEND,
            t.PLUS: SUM,
            t.MINUS: SUM,
            t.NOT: PREFIX,
            t.BANG: PREFIX,
            t.DEC: POSTFIX,
            t.INC: POSTFIX,
            t.OR: BOOLEAN,
            t.AND: BOOLEAN,
            t.XOR: BOOLEAN,
            t.IN: BOOLEAN,
            t.MULTIPLY: PRODUCT,
            t.DIVIDE: PRODUCT,
            t.MOD: PRODUCT,
            t.PACK: POWER,
            t.EQ: COMPARE,
            t.NE: COMPARE,
            t.LT: COMPARE,
            t.LE: COMPARE,
            t.GT: COMPARE,
            t.GE: COMPARE,
            t.INDEX: INDEX
        }

    def parse(self) -> list[o.Expression]:
        return self.parse_statements(t.EOF)

    def parse_statements(self, end_type: str) -> list[o.Expression]:
        """Parse statements within a certain scope (set by 'end_type')

        For block statements, that value will be a closed curly bracket. For program statements, that value will be an
        end-of-file token.
        """
        statements = []
        while self.current.type != end_type:
            statements.append(self.expression())
            self.is_expected_token(t.SEMICOLON)
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

    def expression(self, precedence_name: str = LOWEST) -> o.Expression:
        precedence_level = self.get_precedence_level(precedence_name)

        # Prefix
        left = self.parse_prefix()

        # Infix
        while self.current is not None and precedence_level < self.get_next_precedence_level(self.infix_precedence):
            left = self.parse_infix(left)

        return left

    def parse_prefix(self) -> o.Expression:

        if self.current.type == t.IDENTIFIER and self.peek.type == t.ASSIGN:
            return self.parse_assign()

        elif self.current.type in [t.MINUS, t.PLUS, t.NOT, t.PACK]:
            return self.parse_prefix_expression()

        elif self.current.type == t.OPEN_PAREN:
            return self.parse_grouped_expression()

        elif self.current.type == t.NUMBER:
            return self.parse_number()

        elif self.current.type == t.STRING:
            return self.parse_string()

        elif self.current.type == t.BOOLEAN:
            return self.parse_boolean()

        elif self.current.type == t.IDENTIFIER:
            return self.parse_identifier()

        elif self.current.type == t.FUNCTION:
            return self.parse_function()

        elif self.current.type == t.WHEN:
            return self.parse_when()

        elif self.current.type == t.FOR:
            return self.parse_for()

        raise language_error(
            self.current.line_num,
            f"invalid prefix operator: {self.current.type} ({repr(self.current.value)})")

    def parse_infix(self, left: o.Expression) -> o.InfixExpression | o.PostfixExpression:
        op = self.current
        self.advance()

        # Postfix operators go here
        if op.type in [t.BANG, t.DEC, t.INC]:
            return o.PostfixExpression(op.line_num, op, left)

        right = self.expression(self.infix_precedence.get(op.type, LOWEST))
        return o.InfixExpression(op.line_num, left, op, right)

    def parse_number(self) -> o.Number:
        number_token = self.current
        self.advance()
        return o.Number(number_token.line_num, float(number_token.value))

    def parse_string(self) -> o.String:
        string_token = self.current
        self.advance()
        return o.String(string_token.line_num, string_token.value)

    def parse_boolean(self) -> o.Boolean:
        boolean_token = self.current
        self.advance()
        return o.Boolean(
            boolean_token.line_num,
            boolean_token.value == t.get_token_literal("TRUE")
        )

    def parse_prefix_expression(self) -> o.PrefixExpression:
        op = self.current
        self.advance()
        expression = self.expression(PREFIX)
        return o.PrefixExpression(op.line_num, op, expression)

    def parse_grouped_expression(self) -> o.Expression:
        self.advance()

        # An open paren immediately followed by a closed paren is an empty list
        if self.current.type == t.CLOSED_PAREN:
            self.advance()
            return o.List(self.current.line_num, [])

        # If a token other than a closed paren comes after the open paren, parse the expression
        expression = self.expression()

        if self.current.type == t.CLOSED_PAREN:
            self.advance()
            return expression

        # If the token after the expression is a comma, we're parsing a list
        elif self.current.type == t.COMMA:
            self.advance()
            return self.parse_list(expression)

        raise unexpected_token_error(self.current.line_num, t.CLOSED_PAREN, self.current)

    def parse_identifier(self) -> o.Identifier | o.BuiltinFunction:
        identifier_token = self.current
        self.advance()

        if identifier_token.value in o.BuiltinFunction.builtin_function_names:
            return o.BuiltinFunction(identifier_token.line_num, identifier_token.value)

        return o.Identifier(identifier_token.line_num, identifier_token.value)

    def parse_assign(self) -> o.Expression:
        self.is_expected_token(t.IDENTIFIER)
        variable_name = self.current

        # Skip over identifier token
        self.advance()

        # Confirm current token is an assignment operator. If it is, skip over it.
        self.is_expected_token(t.ASSIGN)
        self.advance()

        right = self.expression()

        return o.Assignment(variable_name.line_num, variable_name.value, right)

    def parse_list(self, first_expression: o.Expression) -> o.List:
        line_num = self.current.line_num
        values = [first_expression]

        while True:
            if self.current.type == t.CLOSED_PAREN:
                self.advance()
                break

            expression = self.expression()
            values.append(expression)

            if self.current.type == t.CLOSED_PAREN:
                self.advance()
                break

            self.is_expected_token(t.COMMA)

            self.advance()

        # Return list object
        return o.List(line_num, values)

    def parse_function(self) -> o.Function:
        line_num: int = self.current.line_num
        self.advance()  # skip function keyword

        # Parse function parameters
        params = []
        while self.current.type != t.COLON:
            self.is_expected_token(t.IDENTIFIER)

            params.append(o.Identifier(self.current.line_num, self.current.value))
            self.advance()

            if self.current.type == t.COLON:
                break

            self.is_expected_token(t.COMMA)
            self.advance()

        self.is_expected_token(t.COLON)
        self.advance()

        # Function body
        body = self.expression()

        return o.Function(line_num, params, body)

    def parse_when(self) -> o.When:
        line_num = self.current.line_num

        self.advance()  # skip over "when" token

        # If the token after "when" is a colon, assume the if-else implementation is being used.
        # Otherwise, assume the switch implementation is being used.
        if self.current.type != t.COLON:
            # Switch
            is_switch = True
            switch_expression = self.expression()
        else:
            # if-else
            switch_expression = o.Boolean(line_num, True)
            is_switch = False

        self.is_expected_token(t.COLON)
        self.advance()

        expressions: list[tuple[o.Expression, o.Expression]] = []

        # Comparison expression
        while True:

            if is_switch:
                # For the switch statement, cases start with the "is" token
                self.is_expected_token(t.IS)
                self.advance()

            comparison_expression = self.expression()

            self.is_expected_token(t.COLON)
            self.advance()

            return_expression = self.expression()

            expressions.append((comparison_expression, return_expression))

            if self.current.type == t.ELSE:
                break

        self.is_expected_token(t.ELSE)
        else_line_num = self.current.line_num
        self.advance()

        self.is_expected_token(t.COLON)
        self.advance()

        # Else expression
        else_return_expression = self.expression()

        # Make a copy so the line numbers are different between the "when" and "else"
        else_expression = copy(switch_expression)
        else_expression.line_num = else_line_num

        expressions.append((else_expression, else_return_expression))

        return o.When(line_num, switch_expression, expressions)

    def parse_for(self) -> o.ForLoop:
        line_num = self.current.line_num

        # Skip "for" token
        self.advance()

        self.is_expected_token(t.IDENTIFIER)
        element_identifier = self.current
        self.advance()

        self.is_expected_token(t.IN)
        self.advance()

        values = self.expression()

        self.is_expected_token(t.COLON)
        self.advance()

        expression = self.expression()

        return o.ForLoop(line_num, element_identifier.value, values, expression)

    def add_semicolon(self) -> None:
        self.tokens.add("SEMICOLON")

    def is_expected_token(self, expected_token_type: str) -> None:
        if self.current.type != expected_token_type:
            raise unexpected_token_error(self.current.line_num, expected_token_type, self.current)
