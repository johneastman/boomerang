from tokens.tokens import *
from tokens.tokenizer import Token


class Number:
    def __init__(self, token: Token):
        self.token = token

    def __eq__(self, other):
        if not isinstance(other, Number):
            return False
        return self.token == other.token

    def __repr__(self):
        return f"Number(token={self.token})"


class Boolean:
    def __init__(self, token: Token):
        self.token = token

    def __eq__(self, other):
        if not isinstance(other, Number):
            return False
        return self.token == other.token

    def __repr__(self):
        return f"Boolean(token={self.token})"


class NoReturn(Token):
    def __init__(self, line_num=0):
        super().__init__(None, None, line_num)


class Identifier:
    def __init__(self, token: Token):
        self.token = token

    def __eq__(self, other):
        if not isinstance(other, Number):
            return False
        return self.token == other.token

    def __repr__(self):
        return f"Identifier(token={self.token})"


class Return:
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"[{self.__class__.__name__}(value={self.expression})]"


class Loop:
    def __init__(self, condition, statements):
        self.condition = condition
        self.statements = statements

    def __repr__(self):
        return f"[{self.__class__.__name__}(condition: {self.condition}, statements: {self.statements})]"


class AssignFunction:
    def __init__(self, parameters, statements):
        self.parameters = parameters
        self.statements = statements

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"[{class_name}(parameters={self.parameters}, statements={self.statements})]"


class IfStatement:
    def __init__(self, comparison: Token, true_statements, false_statements):
        self.comparison = comparison
        self.true_statements = true_statements
        self.false_statements = false_statements


class Print:
    def __init__(self, params, line_num):
        self.params = params
        self.line_num = line_num

    def __repr__(self):
        return f"print({', '.join(repr(expr) for expr in self.params)}"


class Type:
    def __init__(self, value: Token):
        self.value = value

    def __repr__(self):
        return f"Type({self.value})"


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

    def __eq__(self, other):
        if not isinstance(other, BinaryOperation):
            return False

        return self.left == other.left and self.op == other.op and self.right == other.right


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
            self.advance()
            if self.current.type != IDENTIFIER:
                self.raise_expected_token_error(IDENTIFIER)
            return self.assign(self.current)

        elif self.current.type == IF:
            return self.if_statement()

        elif self.current.type == RETURN:
            self.advance()
            return Return(self.expression())

        elif self.current.type == WHILE:
            return self.loop()

        else:
            return self.expression()

    def assign(self, variable_name_token):
        self.advance()
        if self.current.type not in self.assignment_operators:
            self.raise_expected_token_error(", ".join(self.assignment_operators))

        assignment_operator = self.current

        self.advance()
        variable_value = self.expression()

        if assignment_operator.type == ASSIGN:
            return AssignVariable(variable_name_token, variable_value)
        else:
            operator_token = {
                ASSIGN_ADD: Token(get_token_literal("PLUS"), PLUS, variable_name_token.line_num),
                ASSIGN_SUB: Token(get_token_literal("MINUS"), MINUS, variable_name_token.line_num),
                ASSIGN_MUL: Token(get_token_literal("MULTIPLY"), MULTIPLY, variable_name_token.line_num),
                ASSIGN_DIV: Token(get_token_literal("DIVIDE"), DIVIDE, variable_name_token.line_num)
            }

            return AssignVariable(
                variable_name_token,
                BinaryOperation(
                    Identifier(variable_name_token),
                    operator_token.get(assignment_operator.type),
                    variable_value
                )
            )

    def loop(self):
        self.advance()

        comparison = self.expression()

        # Open curly bracket
        if self.current.type != OPEN_CURLY_BRACKET:
            self.raise_expected_token_error(OPEN_CURLY_BRACKET)
        self.advance()

        loop_statements = self.statements()

        # Closed curly bracket
        if self.current.type != CLOSED_CURLY_BRACKET:
            self.raise_expected_token_error(CLOSED_CURLY_BRACKET)
        self.advance()

        return Loop(comparison, loop_statements)

    def if_statement(self):
        self.advance()

        comparison = self.expression()

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

        # if self.current.type != IDENTIFIER:
        #     self.raise_expected_token_error(IDENTIFIER)
        # function_name = self.current
        # self.advance()

        if self.current.type != OPEN_PAREN:
            self.raise_expected_token_error(OPEN_PAREN)
        self.advance()

        parameters = []
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

        return AssignFunction(parameters, function_statements)

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

        elif self.current.type == BOOLEAN:
            bool_val_token = self.current
            self.advance()
            return Boolean(bool_val_token)

        elif self.current.type == FUNCTION:
            return self.function()

        elif self.current.type == IDENTIFIER:
            identifier_token = self.current
            if self.peek.type == OPEN_PAREN:
                return self.function_call(identifier_token)
            elif self.peek.type in self.assignment_operators:
                return self.assign(identifier_token)
            else:
                self.advance()
                return Identifier(identifier_token)

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
        raise Exception(f"Expected {expected_token_type}, got {self.current.type} ('{self.current.value}') on line {self.current.line_num}")
