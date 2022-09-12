import typing

from tokens.tokenizer import *
from tokens.token_queue import TokenQueue
from _parser.ast_objects import *
from utils.utils import raise_error
from typing import Callable

# Precedence names
LOWEST = "LOWEST"  # default
EDGE = "EDGE"  # =>
AND_OR = "AND_OR"  # &&, ||
EQUALS = "EQUALS"  # ==, !=
LESS_GREATER = "LESS_GREATER"  # <, >, >=, <=
SUM = "SUM"  # +, -
PRODUCT = "PRODUCT"  # *, /
PREFIX = "PREFIX"  # -X, +X, !X, X!
CALL = "CALL"  # function calls (e.g. function())


class Parser:

    def __init__(self, tokens: TokenQueue):
        self.tokens = tokens

        self.assignment_operators: list[str] = [
            ASSIGN,
            ASSIGN_ADD,
            ASSIGN_SUB,
            ASSIGN_MUL,
            ASSIGN_DIV
        ]

        # Higher precedence is lower on the list (for example, && and || take precedence above everything, so they have
        # a precedence level of 2.
        #
        # Storing the precedence levels in this list allows precedences to be rearranged without having to manually
        # change other precedence values. For example, if we want to add a precedence before EDGE, we can just add it
        # to this list, and the parser will automatically handle that precedence's integer value (which is the
        # index + 1).
        self.precedences: list[str] = [
            LOWEST,
            EDGE,
            AND_OR,
            EQUALS,
            LESS_GREATER,
            SUM,
            PRODUCT,
            PREFIX,
            CALL
        ]

        self.infix_precedence: dict[str, str] = {
            EQ: EQUALS,
            NE: EQUALS,
            LT: LESS_GREATER,
            LE: LESS_GREATER,
            GT: LESS_GREATER,
            GE: LESS_GREATER,
            AND: AND_OR,
            OR: AND_OR,
            PLUS: SUM,
            MINUS: SUM,
            MULTIPLY: PRODUCT,
            DIVIDE: PRODUCT,
            EDGE: EDGE,
            BANG: PREFIX
        }

    def parse(self) -> list[Statement]:
        ast = []
        while self.current.type != EOF:
            result = self.statement()
            ast.append(result)
        return ast

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

    def parse_prefix(self) -> Expression:  # Factor
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
            self.is_expected_token(CLOSED_PAREN)

        elif self.current.type == INTEGER:
            number_token = self.current
            self.advance()
            return Integer(int(number_token.value), number_token.line_num)

        elif self.current.type == FLOAT:
            float_token = self.current
            self.advance()
            return Float(float(float_token.value), float_token.line_num)

        elif self.current.type == BOOLEAN:
            bool_val_token = self.current
            value = True if bool_val_token.value == get_token_literal("TRUE") else False
            self.advance()
            return Boolean(value, bool_val_token.line_num)

        elif self.current.type == STRING:
            string_token = self.current
            self.advance()
            return String(string_token.value, string_token.line_num)

        elif self.current.type == IDENTIFIER:
            identifier_token = self.current
            if self.peek.type == OPEN_PAREN:
                return self.function_call(identifier_token)
            else:
                self.advance()
                return Identifier(identifier_token.value, identifier_token.line_num)

        raise_error(self.current.line_num, f"Invalid token: {self.current.type} ({self.current.value})")

    def parse_infix(self, left: Expression) -> Expression:
        if self.current.type == EDGE:
            return self.parse_tree(left)

        # Postfix operators are just infix operators without a right expression
        elif self.current.type == BANG:
            self.advance()
            return Factorial(left)

        else:
            op = self.current
            self.advance()
            right = self.expression(self.infix_precedence.get(op.type, LOWEST))
            return BinaryOperation(left, op, right)

    def block_statement(self) -> list[Statement]:
        """Statements between two curly brackets (functions, if-statements, loops, etc.)"""
        statements = []
        while self.current.type != CLOSED_CURLY_BRACKET:
            statements.append(self.statement())
        return statements

    def statement(self) -> Statement:
        if self.current.type == FUNCTION:
            return self.function()

        elif self.current.type == IF:
            return self.if_statement()

        elif self.current.type == RETURN:
            self.advance()
            return Return(self.expression())

        elif self.current.type == WHILE:
            return self.loop()

        elif self.current.type == SET:
            return self.assign()

        else:
            return ExpressionStatement(self.expression())

    def get_operator_token(self, op_type: str, line_num: int) -> Token:
        operator_token = {
            ASSIGN_ADD: Token(get_token_literal("PLUS"), PLUS, line_num),
            ASSIGN_SUB: Token(get_token_literal("MINUS"), MINUS, line_num),
            ASSIGN_MUL: Token(get_token_literal("MULTIPLY"), MULTIPLY, line_num),
            ASSIGN_DIV: Token(get_token_literal("DIVIDE"), DIVIDE, line_num)
        }
        return operator_token[op_type]

    def create_assignment_ast(self, assignment_operator: Token, name: Identifier, value: Expression) -> SetVariable:
        if assignment_operator.type == ASSIGN:
            return SetVariable(name, value)

        elif assignment_operator.type in self.assignment_operators:
            operator_token = self.get_operator_token(assignment_operator.type, assignment_operator.line_num)
            return SetVariable(name, BinaryOperation(name, operator_token, value))

        else:
            raise_error(assignment_operator.line_num, f"Invalid assignment operator: {assignment_operator.type} "
                                                      f"({assignment_operator.value})")

    def assign(self) -> Statement:
        self.advance()

        self.is_expected_token(IDENTIFIER)
        variable_name = self.current

        self.advance()

        assignment_operator = self.current
        self.is_expected_token(self.assignment_operators)

        self.advance()
        right = self.expression()

        return self.create_assignment_ast(
            assignment_operator,
            Identifier(variable_name.value, variable_name.line_num),
            right
        )

    def loop(self) -> Statement:
        self.advance()

        comparison = self.expression()

        # Open curly bracket
        self.is_expected_token(OPEN_CURLY_BRACKET)
        self.advance()

        loop_statements = self.block_statement()

        # Closed curly bracket
        self.is_expected_token(CLOSED_CURLY_BRACKET)
        self.advance()

        return Loop(comparison, loop_statements)

    def if_statement(self) -> Statement:
        self.advance()

        comparison = self.expression()

        # Open curly bracket
        self.is_expected_token(OPEN_CURLY_BRACKET)
        self.advance()

        if_statements = self.block_statement()

        # Closed curly bracket
        self.is_expected_token(CLOSED_CURLY_BRACKET)
        self.advance()

        else_statements = None
        if self.current.type == ELSE:
            self.advance()

            # Open curly bracket
            self.is_expected_token(OPEN_CURLY_BRACKET)
            self.advance()

            else_statements = self.block_statement()

            # Closed curly bracket
            self.is_expected_token(CLOSED_CURLY_BRACKET)
            self.advance()

        return IfStatement(comparison, if_statements, else_statements)

    def function(self) -> Statement:
        self.advance()

        self.is_expected_token(IDENTIFIER)
        function_name = self.current
        self.advance()

        self.is_expected_token(OPEN_PAREN)
        self.advance()

        parameters = []
        # This condition in after 'while' handles functions with no parameters. If this was set to 'while True',
        # the parser would expect a NUMBER after the open-paren of the function call and throw the error
        # in `if self.current.type != NUMBER`.
        while self.current.type != CLOSED_PAREN:
            self.is_expected_token(IDENTIFIER)
            parameters.append(self.current)
            self.advance()

            if self.current.type == CLOSED_PAREN:
                break

            self.is_expected_token(COMMA)
            self.advance()

        self.advance()

        self.is_expected_token(OPEN_CURLY_BRACKET)
        self.advance()

        function_statements = self.block_statement()

        self.is_expected_token(CLOSED_CURLY_BRACKET)
        self.advance()

        return AssignFunction(function_name, parameters, function_statements)

    def function_call(self, identifier_token: Token) -> Factor:
        self.advance()  # skip identifier
        self.advance()  # skip open paren

        parameters: list[Expression] = []
        # This condition in after 'while' handles functions with no parameters. If this was set to 'while True',
        # the parser would expect a NUMBER after the open-paren of the function call and throw the error.
        # in `if self.current.type != NUMBER`.
        while self.current.type != CLOSED_PAREN:
            parameters.append(self.expression())

            if self.current.type == CLOSED_PAREN:
                break

            # Expect comma or closed paren
            self.is_expected_token(COMMA)
            self.advance()

        self.advance()

        line_num = identifier_token.line_num
        builtin_functions: typing.Dict[str, BuiltinFunction] = {
            "print": Print(parameters, line_num),
            "random": Random(parameters, line_num),
            "add_node": AddNode(parameters, line_num),
            "to_str": ToType(parameters, line_num, String),
            "to_int": ToType(parameters, line_num, Integer),
            "to_float": ToType(parameters, line_num, Float),
            "to_bool": ToType(parameters, line_num, Boolean),
        }
        return builtin_functions.get(
            identifier_token.value,
            FunctionCall(identifier_token.value, parameters, identifier_token.line_num))

    def parse_tree(self, left: Expression) -> Node:
        op = self.current
        line_num = op.line_num
        self.advance()

        self.is_expected_token(OPEN_BRACKET)
        self.advance()

        children: list[Node] = []
        while True:
            if self.current.type == CLOSED_BRACKET:
                # Closed bracket means we're at the end of the child nodes and going back to the outer scope/scope
                # of the root node.
                self.advance()
                break

            value = self.expression(self.infix_precedence.get(op.type, LOWEST))
            if self.current.type == EDGE:
                # mypy error: Argument 1 to "append" of "list" has incompatible type "Expression"; expected "Node"
                # Reason for ignore: due to how 'parse_infix' is written, that method will return a Node object in
                # this context. Because the current token is an EDGE operator, 'parse_infix' will call this method.
                children.append(self.parse_infix(value))  # type: ignore
            else:
                children.append(Node(value, line_num))

            if self.current.type == COMMA:
                # Commas denote multiple child nodes
                self.advance()
                continue

        return Node(left, line_num, children=children)

    def is_expected_token(self, expected_token_type: typing.Union[str, list[str]]) -> None:

        # Multiple token types may be expected, so a list of tokens types can be passed. If just a string is passed,
        # that string will be added to a list
        expected_token_types = [expected_token_type] if isinstance(expected_token_type, str) else expected_token_type

        if self.current.type not in expected_token_types:
            raise_error(
                self.current.line_num,
                f"Expected {expected_token_type}, got {self.current.type} ('{self.current.value}')")
