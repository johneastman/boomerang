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


class Float:
    def __init__(self, token: Token):
        self.token = token

    def __eq__(self, other):
        if not isinstance(other, Number):
            return False
        return self.token == other.token

    def __repr__(self):
        return f"Float(token={self.token})"


class Boolean:
    def __init__(self, token: Token):
        self.token = token

    def __eq__(self, other):
        if not isinstance(other, Number):
            return False
        return self.token == other.token

    def __repr__(self):
        return f"Boolean(token={self.token})"


class String:
    def __init__(self, token: Token):
        self.token = token

    def __eq__(self, other):
        if not isinstance(other, Number):
            return False
        return self.token == other.token

    def __repr__(self):
        return f"String(token={self.token})"


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


class AssignFunction(Token):
    def __init__(self, name: Token, parameters, statements):
        self.name = name
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