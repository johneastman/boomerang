import tokens.tokens
from tokens.tokenizer import Token
from tokens.tokens import *
from typing import Optional
from utils import raise_error


class Statement:
    pass


class Expression(Statement):
    pass


class BooleanExpression(Expression):
    pass


class AdditionExpression(BooleanExpression):
    pass


class Term(AdditionExpression):
    pass


class Factor(Term):
    pass


class ExpressionStatement(Statement):
    def __init__(self, expr: Expression):
        self.expr = expr

    def __eq__(self, other: object):
        if not isinstance(other, ExpressionStatement):
            return False
        return self.expr == other.expr


class Base:
    """Base class for lowest-level objects in the abstract syntax tree.

    Data types line integers, floats, booleans, strings, etc., but also identifiers (variables, functions, etc.)
    """

    def __init__(self, token: Token):
        self.token = token

    def __eq__(self, other: object):
        if not isinstance(other, self.__class__):
            return False
        return self.token == other.token

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"{class_name}(token={self.token})"


class BuiltinFunction(Factor):

    def __init__(self, params: list[Expression], line_num: int):
        self.params = params
        self.line_num = line_num

    def __eq__(self, other: object):
        if not isinstance(other, BuiltinFunction):
            return False
        return self.params == other.params and self.line_num == other.line_num

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"{class_name}({self.params}, {self.line_num})"


class Print(BuiltinFunction):
    def __init__(self, params: list[Expression], line_num: int):
        super().__init__(params, line_num)


class Type(BuiltinFunction):
    def __init__(self, params: list[Expression], line_num: int):
        super().__init__(params, line_num)


class Random(BuiltinFunction):
    def __init__(self, params: list[Expression], line_num: int):
        super().__init__(params, line_num)


class Number(Base, Factor):
    def __init__(self, token: Token):
        super().__init__(token)


class Float(Base, Factor):
    def __init__(self, token: Token):
        super().__init__(token)


class Boolean(Base, Factor):
    def __init__(self, token: Token):
        super().__init__(token)


class String(Base, Factor):
    def __init__(self, token: Token):
        super().__init__(token)


class Identifier(Base, Factor):
    def __init__(self, token: Token):
        super().__init__(token)


class Dictionary(Factor):
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
    def __init__(self, line_num: int = 0):
        super().__init__("", "", line_num)

    def __eq__(self, other):
        if not isinstance(other, NoReturn):
            return False
        return self.value == other.value and self.type == other.type and self.line_num == other.line_num


class DictionaryToken(Token):
    """Token object for storing dictionaries.

    We could use a Python dictionary as the internal structure--that would probably be more efficient. However,
    this implementation allows for storing the keys and values as full token. This implementations means we don't have
    to recreate the token after fetching the literal value from the dictionary or interpret the token type from the
    Python data type.
    """

    def __init__(self, data: dict[Token, Token], line_num: int) -> None:
        self.data = data
        super().__init__(self.string(), tokens.tokens.DICTIONARY, line_num)

    def set(self, key: Token, value: Token) -> None:
        self.data[key] = value
        self.value = self.string()

    def update(self, keys: list[Token], value: Token) -> None:
        self.data = self._update(self.data, keys, value)

    def _update(self, dictionary: dict[Token, Token], keys: list[Token], value: Token, index: int = 0) -> dict[Token, Token]:
        key: Token = keys[index]

        if index == len(keys) - 1:
            # Set the variable
            dictionary[key] = value
            return dictionary

        # mypy error: error: Incompatible types in assignment (expression has type "Optional[Token]", variable has type "Optional[DictionaryToken]"
        # Reason for ignore: DictionaryToken is a subclass of Token
        next_dict: Optional[DictionaryToken] = dictionary.get(key, None)  # type: ignore
        if next_dict is None:
            raise_error(key.line_num, f"No key in dictionary: {str(key)}")

        # Update the parent key with the new values of the child dictionary
        #
        # mypy error: error: Item "None" of "Optional[DictionaryToken]" has no attribute "data"
        # Reason for ignore: 'next_dict' will never be None because an exception is thrown when that value is None
        dictionary[key] = DictionaryToken(self._update(next_dict.data, keys, value, index=index + 1), key.line_num)  # type: ignore
        return dictionary

    def string(self) -> str:
        def traverse(d: dict[Token, Token]):
            s = "{"
            for i, (k, v) in enumerate(d.items()):
                if isinstance(v, dict):
                    s += f"{display_val(k)}: {traverse(v)}"
                else:
                    s += f"{display_val(k)}: {display_val(v)}"

                # Don't add a comma after the last element in the list of key-pair values
                if i < len(d.items()) - 1:
                    s += ", "
            s += "}"
            return s

        def display_val(t: Token) -> str:
            if t.type == STRING:
                return f"\"{t.value}\""
            return t.value

        return traverse(self.data)

    def get(self, key: Token) -> Optional[Token]:
        return self.data.get(key, None)

    def __str__(self) -> str:
        return self.string()

    def __repr__(self):
        return f"{self.__class__.__name__}(data={self.data}, value={self.value}, type={self.type}, line_num={self.line_num})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DictionaryToken):
            return False

        return self.value == other.value and self.type == other.type and self.line_num == other.line_num \
               and self.data == other.data


class Index(Expression):
    def __init__(self, left: Expression, indices: list[Expression]):
        self.left = left
        self.index = indices

    def __eq__(self, other: object):
        if not isinstance(other, Index):
            return False
        return self.left == other.left and self.index == other.index

    def __repr__(self):
        return f"Index(left={self.left}, index={self.index})"


class Return(Statement):
    def __init__(self, expr: Expression):
        self.expr = expr

    def __repr__(self):
        return f"[{self.__class__.__name__}(value={self.expr})]"


class Loop(Statement):
    def __init__(self, condition: Expression, statements: list[Statement]):
        self.condition = condition
        self.statements = statements

    def __repr__(self):
        return f"[{self.__class__.__name__}(condition: {self.condition}, statements: {self.statements})]"


class AssignFunction(Statement):
    def __init__(self, name: Token, parameters, statements):
        self.name = name
        self.parameters = parameters
        self.statements = statements

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"{class_name}(parameters={self.parameters}, statements={self.statements})"


class IfStatement(Statement):
    def __init__(self,
                 comparison: Expression,
                 true_statements: list[Statement],
                 false_statements: Optional[list[Statement]]):
        self.comparison = comparison
        self.true_statements = true_statements
        self.false_statements = false_statements


class FunctionCall(Factor):
    def __init__(self, name: Token, parameter_values):
        self.name = name
        self.parameter_values = parameter_values

    def __repr__(self):
        return f"[{self.__class__.__name__}(name={self.name}, parameter_values={self.parameter_values})]"


class BinaryOperation(Expression):
    def __init__(self, left: Expression, op: Token, right: Expression):
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


class AssignVariable(Statement):
    def __init__(self, name: Expression, value: Expression):
        self.name = name
        self.value = value

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"{class_name}(name={self.name}, value={self.value})"


class UnaryOperation(Factor):
    def __init__(self, op: Token, expression):
        self.op = op
        self.expression = expression

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"[{class_name}(op={self.op}, expression={self.expression})]"
