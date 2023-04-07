import typing

from tokens.tokens import *

if typing.TYPE_CHECKING:
    from tokens.tokenizer import Token


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
    def __init__(self, expr: Expression) -> None:
        self.expr = expr

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(expr: {self.expr})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ExpressionStatement):
            return False
        return self.expr == other.expr


class Base(Expression):
    """Base class for lowest-level objects in the abstract syntax tree.

    Data types line integers, floats, booleans, strings, etc., but also identifiers (variables, functions, etc.)
    """

    def __init__(self,
                 value: typing.Any,
                 line_num: int):
        self.value = value
        self.line_num = line_num

    def add(self, other: "Base") -> "Base":
        utils.raise_error(
            self.line_num,
            f"Cannot perform {PLUS} operation on {type(self).__name__} and {type(other).__name__}")

    def subtract(self, other: "Base") -> "Base":
        utils.raise_error(
            self.line_num,
            f"Cannot perform {MINUS} operation on {type(self).__name__} and {type(other).__name__}")

    def multiply(self, other: "Base") -> "Base":
        utils.raise_error(
            self.line_num,
            f"Cannot perform {MULTIPLY} operation on {type(self).__name__} and {type(other).__name__}")

    def divide(self, other: "Base") -> "Base":
        utils.raise_error(
            self.line_num,
            f"Cannot perform {DIVIDE} operation on {type(self).__name__} and {type(other).__name__}")

    def negative(self) -> "Base":
        utils.raise_error(self.line_num, f"Cannot perform {MINUS} operation on {type(self).__name__}")

    def positive(self) -> "Base":
        utils.raise_error(self.line_num, f"Cannot perform {PLUS} operation on {type(self).__name__}")

    def __str__(self) -> str:
        return str(self.value)

    def __float__(self) -> float:
        return float(self.value)

    def __int__(self) -> int:
        return int(self.value)

    def __eq__(self, other: object) -> bool:
        """FOR TESTING"""
        if not isinstance(other, self.__class__):
            return False

        return self.value == other.value and self.line_num == other.line_num

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(value={self.value}, line_num={self.line_num})"


class NoReturn(Base, Factor):
    def __init__(self, line_num: int = 0) -> None:
        super().__init__("", line_num)


class Integer(Base, Factor):
    def __init__(self, value: int, line_num: int) -> None:
        super().__init__(value, line_num)

    def negative(self) -> "Base":
        return Integer(-self.value, self.line_num)

    def positive(self) -> "Base":
        return self

    def add(self, other: Base) -> Base:
        result = self.value + other.value
        if isinstance(other, Integer):
            return Integer(result, self.line_num)
        elif isinstance(other, Float):
            return Float(result, self.line_num)

        return super().add(other)

    def subtract(self, other: Base) -> Base:
        result = self.value - other.value
        if isinstance(other, Integer):
            return Integer(result, self.line_num)
        elif isinstance(other, Float):
            return Float(result, self.line_num)

        utils.raise_error(
            self.line_num,
            f"Cannot perform {PLUS} operation on {type(self).__name__} and {type(other).__name__}"
        )

    def multiply(self, other: Base) -> Base:
        result = self.value * other.value
        if isinstance(other, Integer):
            return Integer(result, self.line_num)
        elif isinstance(other, Float):
            return Float(result, self.line_num)

        utils.raise_error(
            self.line_num,
            f"Cannot perform {PLUS} operation on {type(self).__name__} and {type(other).__name__}"
        )

    def divide(self, other: Base) -> Base:

        if other.value == 0:
            utils.raise_error(self.line_num, "division by zero")

        result = self.value / other.value
        if isinstance(other, Integer):
            return Float(result, self.line_num)
        elif isinstance(other, Float):
            return Float(result, self.line_num)

        utils.raise_error(
            self.line_num,
            f"Cannot perform {PLUS} operation on {type(self).__name__} and {type(other).__name__}"
        )


class Float(Base, Factor):
    def __init__(self, value: float, line_num: int) -> None:
        super().__init__(value, line_num)

    def negative(self) -> "Base":
        return Float(-self.value, self.line_num)

    def positive(self) -> "Base":
        return self

    def add(self, other: Base) -> Base:
        result = self.value + other.value
        if isinstance(other, Integer):
            return Float(result, self.line_num)
        elif isinstance(other, Float):
            return Float(result, self.line_num)

        utils.raise_error(
            self.line_num,
            f"Cannot perform {PLUS} operation on {type(self).__name__} and {type(other).__name__}"
        )

    def subtract(self, other: Base) -> Base:
        result = self.value - other.value
        if isinstance(other, Integer):
            return Float(result, self.line_num)
        elif isinstance(other, Float):
            return Float(result, self.line_num)

        utils.raise_error(
            self.line_num,
            f"Cannot perform {PLUS} operation on {type(self).__name__} and {type(other).__name__}"
        )

    def multiply(self, other: Base) -> Base:
        result = self.value * other.value
        if isinstance(other, Integer):
            return Float(result, self.line_num)
        elif isinstance(other, Float):
            return Float(result, self.line_num)

        utils.raise_error(
            self.line_num,
            f"Cannot perform {PLUS} operation on {type(self).__name__} and {type(other).__name__}"
        )

    def divide(self, other: Base) -> Base:

        if other.value == 0:
            utils.raise_error(self.line_num, "division by zero")

        result = self.value / other.value
        if isinstance(other, Integer):
            return Float(result, self.line_num)
        elif isinstance(other, Float):
            return Float(result, self.line_num)

        utils.raise_error(
            self.line_num,
            f"Cannot perform {PLUS} operation on {type(self).__name__} and {type(other).__name__}"
        )


class Identifier(Factor):
    def __init__(self, value: str, line_num: int) -> None:
        self.value = value
        self.line_num = line_num

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Identifier):
            return False
        return self.value == other.value and self.line_num == other.line_num


class BinaryOperation(Expression):
    def __init__(self, left: Expression, op: "Token", right: Expression) -> None:
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self) -> str:
        class_name: str = self.__class__.__name__
        return f"[{class_name}(left={self.left}, op={self.op}, right={self.right})]"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BinaryOperation):
            return False

        return self.left == other.left and self.op == other.op and self.right == other.right


class SetVariable(Statement):
    def __init__(self, name: Identifier, value: Expression) -> None:
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(name={self.name}, value={self.value})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SetVariable):
            return False
        return self.name == other.name and self.value == other.value


class UnaryOperation(Factor):
    def __init__(self, op: "Token", expression: Expression) -> None:
        self.op = op
        self.expression = expression

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"[{class_name}(op={self.op}, expression={self.expression})]"
