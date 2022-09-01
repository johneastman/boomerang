import typing

from tokens.tokenizer import *
from _parser.ast_objects import *
from utils.utils import raise_error
from typing import Callable


class Parser:

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0

        self.assignment_operators = [
            ASSIGN,
            ASSIGN_ADD,
            ASSIGN_SUB,
            ASSIGN_MUL,
            ASSIGN_DIV
        ]

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

    def pointer(self, root_expression: Expression, next_method: Callable[[], Expression]) -> Expression:
        line_num = self.current.line_num
        self.advance()

        def get_nodes(root: Expression) -> Node:
            self.is_expected_token(OPEN_BRACKET)
            self.advance()

            children = []
            while True:

                if self.current.type == CLOSED_BRACKET:
                    # Closed bracket means we're at the end of the child nodes and going back to the outer scope/scope
                    # of the root node.
                    self.advance()
                    break

                value = next_method()

                if self.current.type == EDGE:
                    # Pointer denotes an edge, so we're creating a child node/subtree
                    self.advance()
                    children.append(get_nodes(value))
                else:
                    # A leaf node
                    children.append(Node(value))

                if self.current.type == COMMA:
                    # Commas denote multiple child nodes
                    self.advance()
                    continue

            return Node(root, children=children)

        nodes = get_nodes(root_expression)
        return Tree(nodes, line_num)

    def binary_expression(
            self,
            binary_operators: list[str],
            next_method: Callable[[], Expression]) -> Expression:

        left = next_method()

        while True:
            if self.current is None:
                return left
            elif self.current.type in binary_operators:
                op = self.current
                self.advance()
                right = next_method()
                left = BinaryOperation(left, op, right)
            elif self.current.type == BANG:
                self.advance()
                left = Factorial(left)
            else:
                break

        return left

    def expression(self) -> Expression:
        expression = self.tree()

        if self.current.type == EDGE:
            return self.pointer(expression, self.tree)

        return expression

    def tree(self) -> Expression:
        return self.binary_expression([
            AND, OR
        ], self.boolean)

    def boolean(self) -> Expression:
        return self.binary_expression([
            EQ,
            NE,
            GE,
            GT,
            LE,
            LT
        ], self.addition)

    def addition(self) -> Expression:
        return self.binary_expression([
            PLUS,
            MINUS
        ], self.term)

    def term(self) -> Expression:
        return self.binary_expression([
            MULTIPLY,
            DIVIDE
        ], self.factor)

    def factor(self) -> Expression:
        # mypy ignore: Missing return statement
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
