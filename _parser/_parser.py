import typing

from tokens.tokenizer import *
from _parser.ast_objects import *
from utils.utils import raise_error
from typing import Callable


class Parser:

    # Higher precedence is lower on the list (for example, && and || take precedence above everything, so they have a
    # precedence level of 2.
    LOWEST = 1
    EDGE = 2  # =>
    AND_OR = 3  # &&, ||
    EQUALS = 4  # ==, !=
    LESS_GREATER = 5  # <, >
    SUM = 6  # +, -
    PRODUCT = 7  # *, /
    PREFIX = 8  # -X, +X, !X
    CALL = 9  # func()

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0

        self.assignment_operators: list[str] = [
            ASSIGN,
            ASSIGN_ADD,
            ASSIGN_SUB,
            ASSIGN_MUL,
            ASSIGN_DIV
        ]

        self.infix_precedence: dict[str, int] = {
            EQ: self.EQUALS,
            NE: self.EQUALS,
            LT: self.LESS_GREATER,
            LE: self.LESS_GREATER,
            GT: self.LESS_GREATER,
            GE: self.LESS_GREATER,
            AND: self.AND_OR,
            OR: self.AND_OR,
            PLUS: self.SUM,
            MINUS: self.SUM,
            MULTIPLY: self.PRODUCT,
            DIVIDE: self.PRODUCT,
            FUNCTION: self.CALL,
            EDGE: self.EDGE
        }

        self.prefix_denotations: dict[str, Callable[[], Expression]] = {  # prefix: leaf/terminating nodes. Not recursive, nothing on the left
            INTEGER: self.parse_prefix,
            FLOAT: self.parse_prefix,
            BOOLEAN: self.parse_prefix,
            STRING: self.parse_prefix,
            BANG: self.parse_prefix,
            PLUS: self.parse_prefix,
            MINUS: self.parse_prefix,
            IDENTIFIER: self.parse_prefix,  # variable, function
            OPEN_PAREN: self.parse_prefix
        }

        self.postfix_precedence: dict[str, int] = {
            BANG: self.PREFIX
        }

        self.left_denotations: dict[str, Callable[[Expression], Expression]] = {
            PLUS: self.parse_infix,
            MINUS: self.parse_infix,
            MULTIPLY: self.parse_infix,
            DIVIDE: self.parse_infix,
            EDGE: self.parse_infix,
            EQ: self.parse_infix,
            NE: self.parse_infix,
            GT: self.parse_infix,
            GE: self.parse_infix,
            LT: self.parse_infix,
            LE: self.parse_infix,
            AND: self.parse_infix,
            OR: self.parse_infix,
        }

        self.right_denotations: dict[str, Callable[[Expression], Expression]] = {
            BANG: self.parse_postfix
        }

    def expression(self, precedence_level: int = LOWEST) -> Expression:

        # Prefix
        prefix_function: typing.Optional[Callable[[], Expression]] = self.prefix_denotations.get(self.current.type, None)
        if prefix_function is None:
            raise_error(self.current.line_num, f"invalid prefix operator: {self.current.type}")
        left = prefix_function()

        # Postfix comes before infix to allow postfix operators in infix expressions (e.g., 5! + 5)
        while self.current is not None and precedence_level < self.postfix_precedence.get(self.current.type, self.LOWEST):
            postfix_function: typing.Optional[Callable[[Expression], Expression]] = self.right_denotations.get(self.current.type, None)
            if postfix_function is None:
                raise_error(self.current.line_num, f"invalid postfix operator: {self.current.type}")
            left = postfix_function(left)

        # Infix
        while self.current is not None and precedence_level < self.infix_precedence.get(self.current.type, self.LOWEST):
            infix_function: typing.Optional[Callable[[Expression], Expression]] = self.left_denotations.get(self.current.type, None)
            if infix_function is None:
                raise_error(self.current.line_num, f"invalid infix operator: {self.current.type}")
            left = infix_function(left)

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
        else:
            op = self.current
            self.advance()
            right = self.expression(self.infix_precedence.get(op.type, self.LOWEST))
            return BinaryOperation(left, op, right)

    def parse_postfix(self, left: Expression) -> Expression:
        if self.current.type == BANG:
            self.advance()
            return Factorial(left)
        return left

    def advance(self) -> None:
        self.index += 1

    @property
    def current(self) -> Token:
        current = self.tokens[self.index] if self.index < len(self.tokens) else None
        if current is None:
            raise Exception(f"from {self.__class__.__name__}.current: token is None")
        return current

    @property
    def peek(self) -> Token:
        next_token_index = self.index + 1
        next_token = self.tokens[next_token_index] if next_token_index < len(self.tokens) else None
        if next_token is None:
            raise Exception(f"from {self.__class__.__name__}.peek: token is None")
        return next_token

    def parse(self) -> list[Statement]:
        ast = []
        while self.current is not None and self.current.type != EOF:
            result = self.statement()
            self.is_expected_token(SEMICOLON)

            self.advance()
            ast.append(result)
        return ast

    def block_statement(self) -> list[Statement]:
        """Statements between two curly brackets (functions, if-statements, loops, etc.)"""
        statements = []
        while self.current.type != CLOSED_CURLY_BRACKET:
            statements.append(self.statement())
            self.is_expected_token(SEMICOLON)
            self.advance()
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

        # Add a semicolon so users don't have to add one in the code
        self.add_semicolon()

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

        self.add_semicolon()

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

        self.add_semicolon()

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

            value = self.expression(self.infix_precedence.get(op.type, self.LOWEST))
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

    def add_semicolon(self) -> None:
        semicolon_label = "SEMICOLON"
        self.tokens.insert(
            self.index,
            Token(get_token_literal(semicolon_label), get_token_type(semicolon_label), self.current.line_num)
        )
