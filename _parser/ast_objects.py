from tokens.tokenizer import Token


class Base:
    """Base class for lowest-level objects in the abstract syntax tree.

    Data types line integers, floats, booleans, strings, etc., but also identifiers (variables, functions, etc.)
    """
    def __init__(self, token: Token):
        self.token = token

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.token == other.token

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"{class_name}(token={self.token})"


class Number(Base):
    def __init__(self, token: Token):
        super().__init__(token)


class Float(Base):
    def __init__(self, token: Token):
        super().__init__(token)


class Boolean(Base):
    def __init__(self, token: Token):
        super().__init__(token)


class String(Base):
    def __init__(self, token: Token):
        super().__init__(token)


class Identifier(Base):
    def __init__(self, token: Token):
        super().__init__(token)


class Dictionary:
    def __init__(self, keys, values, line_num):
        self.keys = keys
        self.values = values
        self.line_num = line_num

    def __eq__(self, other):
        if not isinstance(other, Dictionary):
            return False
        return self.keys == other.keys and self.values == other.values

    def __repr__(self):
        return f"Dictionary(keys={self.keys}, values={self.values})"


class NoReturn(Token):
    def __init__(self, line_num=0):
        super().__init__(None, None, line_num)

    def __eq__(self, other):
        if not isinstance(other, NoReturn):
            return False
        return self.value == other.value and self.type == other.type and self.line_num == other.line_num


class Index:
    def __init__(self, left, index):
        self.left = left
        self.index = index

    def __eq__(self, other):
        if not isinstance(other, Index):
            return False
        return self.left == other.left and self.index == other.index

    def __repr__(self):
        return f"Index(left={self.left}, index={self.index})"


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

    def __eq__(self, other):
        if not isinstance(other, Type):
            return False
        return self.value == other.value

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
        return f"{class_name}(name={self.name}, value={self.value})"


class UnaryOperation:
    def __init__(self, op: Token, expression):
        self.op = op
        self.expression = expression

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"[{class_name}(op={self.op}, expression={self.expression})]"