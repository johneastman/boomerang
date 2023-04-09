import typing

from interpreter.tokens.tokenizer import Token
from interpreter.tokens.tokens import PLUS, MINUS, MULTIPLY, DIVIDE, get_token_literal, POINTER
from interpreter.utils.utils import language_error


class Expression:
    def __init__(self, line_num: int):
        self.line_num = line_num

    def __repr__(self) -> str:
        return self.__str__()

    def __add__(self, other: object) -> "Expression":
        raise language_error(self.line_num, f"Invalid types {type(self).__name__} and {type(other).__name__} for {PLUS}")

    def __sub__(self, other: object) -> "Expression":
        raise language_error(self.line_num, f"Invalid types {type(self).__name__} and {type(other).__name__} for {MINUS}")

    def __mul__(self, other: object) -> "Expression":
        raise language_error(self.line_num, f"Invalid types {type(self).__name__} and {type(other).__name__} for {MULTIPLY}")

    def __truediv__(self, other: object) -> "Expression":
        raise language_error(self.line_num, f"Invalid types {type(self).__name__} and {type(other).__name__} for {DIVIDE}")

    def pointer(self, other: object) -> "Expression":
        raise language_error(self.line_num, f"Invalid types {type(self).__name__} and {type(other).__name__} for {POINTER}")


class Number(Expression):
    def __init__(self, line_num: int, value: float):
        super().__init__(line_num)
        self.value = value

    def __str__(self) -> str:
        if self.is_whole_number():
            return str(int(self.value))
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Number):
            return False
        return self.line_num == other.line_num and self.value == other.value

    def __add__(self, other: object) -> Expression:
        if isinstance(other, Number):
            return Number(self.line_num, self.value + other.value)

        return super().__add__(other)

    def __sub__(self, other: object) -> Expression:
        if isinstance(other, Number):
            return Number(self.line_num, self.value - other.value)

        return super().__sub__(other)

    def __mul__(self, other: object) -> Expression:
        if isinstance(other, Number):
            return Number(self.line_num, self.value * other.value)

        return super().__sub__(other)

    def __truediv__(self, other: object) -> Expression:
        if isinstance(other, Number):
            return Number(self.line_num, self.value / other.value)

        return super().__sub__(other)

    def is_whole_number(self) -> bool:
        return self.value.is_integer()


class String(Expression):
    def __init__(self, line_num: int, value: str):
        super().__init__(line_num)
        self.value = value

    def __str__(self) -> str:
        return f"\"{self.value}\""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, String):
            return False
        return self.line_num == other.line_num and self.value == other.value

    def __add__(self, other: object) -> Expression:
        if isinstance(other, String):
            return String(self.line_num, self.value + other.value)

        return super().__add__(other)


class Boolean(Expression):
    def __init__(self, line_num: int, value: bool):
        super().__init__(line_num)
        self.value = value

    def __str__(self) -> str:
        return get_token_literal("TRUE") if self.value else get_token_literal("FALSE")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Boolean):
            return False
        return self.line_num == other.line_num and self.value == other.value


class List(Expression):
    def __init__(self, line_num: int, values: list[Expression]):
        super().__init__(line_num)
        self.values = values

    def __str__(self) -> str:
        return f"({', '.join(map(str, self.values))})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, List):
            return False
        return self.line_num == other.line_num and self.values == other.values

    def pointer(self, other: object) -> "Expression":
        if isinstance(other, Number) or isinstance(other, String) or isinstance(other, Boolean):
            self.values.append(other)
            return List(self.line_num, self.values)
        elif isinstance(other, List):
            self.values.extend(other.values)
            return List(self.line_num, self.values)

        return super().pointer(other)


class Identifier(Expression):
    def __init__(self, line_num: int, value: str):
        super().__init__(line_num)
        self.value = value

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Identifier):
            return False
        return self.line_num == other.line_num and self.value == other.value


class BuiltinFunction(Expression):

    print_ = "print"

    builtin_function_names = [
        print_
    ]

    def __init__(self, line_num: int, name: str):
        super().__init__(line_num)
        self.name = name

    def __str__(self) -> str:
        return f"<built-in function {self.name}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BuiltinFunction):
            return False
        return self.line_num == other.line_num and self.name == other.name

    def pointer(self, other: object) -> "Expression":
        if isinstance(other, List):
            match self.name:
                case self.print_:
                    print(", ".join(map(str, other.values)))
                case _:
                    raise Exception(f"Unimplemented builtin function {self.name}")

            return self

        return super().pointer(other)


class UnaryExpression(Expression):
    def __init__(self, line_num: int, operator: Token, expression: Expression):
        super().__init__(line_num)
        self.operator = operator
        self.expression = expression

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UnaryExpression):
            return False
        return self.line_num == other.line_num and self.operator == other.operator and self.expression == other.expression


class BinaryExpression(Expression):
    def __init__(self, line_num: int, left: Expression, operator: Token, right: Expression):
        super().__init__(line_num)
        self.left = left
        self.operator = operator
        self.right = right

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BinaryExpression):
            return False
        return self.line_num == other.line_num and self.left == other.left and self.operator == other.operator and self.right == other.right


class Assignment(Expression):
    def __init__(self, line_num: int, variable: str, value: Expression):
        super().__init__(line_num)
        self.variable = variable
        self.value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Assignment):
            return False
        return self.line_num == other.line_num and self.variable == other.variable and self.value == other.value


class Error(Expression):
    def __init__(self, line_num: int, message: str):
        super().__init__(line_num)
        self.message = message

    def __str__(self) -> str:
        return self.message

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Error):
            return False
        return self.line_num == other.line_num and self.message == other.message
