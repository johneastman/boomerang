import typing
from functools import reduce

from interpreter.tokens.token import Token
from interpreter.tokens.tokens import get_token_literal, PLUS, MINUS, MULTIPLY, DIVIDE, POINTER, BANG, GT, GE, \
    LT, LE, AND, OR, MOD
from interpreter.utils.utils import language_error, divide_by_zero_error


class Expression:
    def __init__(self, line_num: int):
        self.line_num = line_num

        # For displaying object representations
        self.class_name = self.__class__.__name__

    def __str__(self) -> str:
        raise Exception(f"__str__ method in {type(self).__name__} not implemented.")

    def __repr__(self, **kwargs: typing.Any) -> str:
        variables = {**{"line_num": self.line_num}, **kwargs}
        return f"{self.class_name}({', '.join(list(map(lambda p: f'{p[0]}={repr(p[1])}', variables.items())))})"

    def eq(self, _: object) -> "Expression":
        return Boolean(self.line_num, False)

    def ne(self, _: object) -> "Expression":
        return Boolean(self.line_num, False)

    def abs(self) -> "Expression":
        raise language_error(self.line_num, f"Invalid type {type(self).__name__} for absolute value")

    def neg(self) -> "Expression":
        raise language_error(self.line_num, f"Invalid type {type(self).__name__} for negation")

    def fac(self) -> "Expression":
        raise language_error(self.line_num, f"Invalid type {type(self).__name__} for factorial")

    def inc(self) -> "Expression":
        raise language_error(self.line_num, f"Invalid type {type(self).__name__} for increment")

    def dec(self) -> "Expression":
        raise language_error(self.line_num, f"Invalid type {type(self).__name__} for decrement")

    def and_(self, other: object) -> "Expression":
        raise language_error(self.line_num, f"Invalid types {type(self).__name__} and {type(other).__name__} for {AND}")

    def or_(self, other: object) -> "Expression":
        raise language_error(self.line_num, f"Invalid types {type(self).__name__} and {type(other).__name__} for {OR}")

    def gt(self, other: object) -> "Expression":
        raise language_error(self.line_num, f"Invalid types {type(self).__name__} and {type(other).__name__} for {GT}")

    def ge(self, other: object) -> "Expression":
        raise language_error(self.line_num, f"Invalid types {type(self).__name__} and {type(other).__name__} for {GE}")

    def lt(self, other: object) -> "Expression":
        raise language_error(self.line_num, f"Invalid types {type(self).__name__} and {type(other).__name__} for {LT}")

    def le(self, other: object) -> "Expression":
        raise language_error(self.line_num, f"Invalid types {type(self).__name__} and {type(other).__name__} for {LE}")

    def add(self, other: object) -> "Expression":
        raise language_error(self.line_num,
                             f"Invalid types {type(self).__name__} and {type(other).__name__} for {PLUS}")

    def sub(self, other: object) -> "Expression":
        raise language_error(self.line_num,
                             f"Invalid types {type(self).__name__} and {type(other).__name__} for {MINUS}")

    def mul(self, other: object) -> "Expression":
        raise language_error(self.line_num,
                             f"Invalid types {type(self).__name__} and {type(other).__name__} for {MULTIPLY}")

    def div(self, other: object) -> "Expression":
        raise language_error(self.line_num,
                             f"Invalid types {type(self).__name__} and {type(other).__name__} for {DIVIDE}")

    def mod(self, other: object) -> "Expression":
        raise language_error(self.line_num,
                             f"Invalid types {type(self).__name__} and {type(other).__name__} for {MOD}")

    def ptr(self, other: object) -> "Expression":
        raise language_error(self.line_num,
                             f"Invalid types {type(self).__name__} and {type(other).__name__} for {POINTER}")

    def bang(self) -> "Expression":
        raise language_error(self.line_num, f"Invalid type {type(self).__name__} for {BANG}")


class Number(Expression):
    def __init__(self, line_num: int, value: float):
        super().__init__(line_num)
        self.value = value

    def __str__(self) -> str:
        return str(self.__display_value())

    def __repr__(self, **kwargs: typing.Any) -> str:
        return super().__repr__(value=self.__display_value())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Number):
            return False
        return self.line_num == other.line_num and self.value == other.value

    def __display_value(self) -> float:
        if self.is_whole_number():
            return int(self.value)
        return self.value

    def eq(self, other: object) -> Expression:
        if isinstance(other, Number):
            return Boolean(self.line_num, self.value == other.value)
        return super().eq(other)

    def ne(self, other: object) -> "Expression":
        if isinstance(other, Number):
            return Boolean(self.line_num, self.value != other.value)
        return super().ne(other)

    def abs(self) -> "Expression":
        return Number(self.line_num, abs(self.value))

    def neg(self) -> "Expression":
        return Number(self.line_num, -self.value)

    def fac(self) -> "Expression":
        if not self.is_whole_number():
            raise language_error(self.line_num, "expression for factorial must be whole number")

        base_number = int(self.value)

        if base_number == 0 or base_number == 1:
            return Number(self.line_num, 1)

        if base_number < 0:
            # For negative numbers, factorial is offset by 1 from its positive counterparts.
            # For example, -1! == 2!, -2! == 3!, -3! = 4!, etc.
            start_number = abs(base_number) + 1
        else:
            start_number = base_number

        # No need to start at 1 because 1 multiplied by anything is itself
        return Number(
            self.line_num,
            reduce(lambda a, b: a * b, [i for i in range(2, start_number + 1)])
        )

    def inc(self) -> "Expression":
        return Number(self.line_num, self.value + 1)

    def dec(self) -> "Expression":
        return Number(self.line_num, self.value - 1)

    def gt(self, other: object) -> "Expression":
        if isinstance(other, Number):
            return Boolean(self.line_num, self.value > other.value)
        return super().gt(other)

    def ge(self, other: object) -> "Expression":
        if isinstance(other, Number):
            return Boolean(self.line_num, self.value >= other.value)
        return super().ge(other)

    def lt(self, other: object) -> "Expression":
        if isinstance(other, Number):
            return Boolean(self.line_num, self.value < other.value)
        return super().lt(other)

    def le(self, other: object) -> "Expression":
        if isinstance(other, Number):
            return Boolean(self.line_num, self.value <= other.value)
        return super().le(other)

    def add(self, other: object) -> Expression:
        if isinstance(other, Number):
            return Number(self.line_num, self.value + other.value)

        return super().add(other)

    def sub(self, other: object) -> Expression:
        if isinstance(other, Number):
            return Number(self.line_num, self.value - other.value)

        return super().sub(other)

    def mul(self, other: object) -> Expression:
        if isinstance(other, Number):
            return Number(self.line_num, self.value * other.value)

        return super().mul(other)

    def div(self, other: object) -> Expression:
        if isinstance(other, Number):
            if other.value == 0:
                raise divide_by_zero_error(self.line_num)
            return Number(self.line_num, self.value / other.value)

        return super().div(other)

    def mod(self, other: object) -> "Expression":
        if isinstance(other, Number):
            if other.value == 0:
                raise divide_by_zero_error(self.line_num)
            return Number(self.line_num, self.value % other.value)

        return super().mod(other)

    def is_whole_number(self) -> bool:
        """
        Originally used "self.value.is_integer()" but that caused this error:
            AttributeError: 'int' object has no attribute 'is_integer'

        To fix that error, I changed the code to "float(self.value).is_integer()", converting "self.value"
        to a float. However, that produced this error:
            OverflowError: int too large to convert to float
        """
        return self.value % 1 == 0


class String(Expression):
    def __init__(self, line_num: int, value: str):
        super().__init__(line_num)
        self.value = value

    def __str__(self) -> str:
        return f"\"{self.value}\""

    def __repr__(self, **kwargs: typing.Any) -> str:
        return super().__repr__(value=self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, String):
            return False
        return self.line_num == other.line_num and self.value == other.value

    def eq(self, other: object) -> Expression:
        if isinstance(other, String):
            return Boolean(self.line_num, self.value == other.value)
        return super().eq(other)

    def ne(self, other: object) -> Expression:
        if isinstance(other, String):
            return Boolean(self.line_num, self.value != other.value)
        return super().ne(other)

    def add(self, other: object) -> Expression:
        if isinstance(other, String):
            return String(self.line_num, self.value + other.value)

        return super().add(other)


class Boolean(Expression):
    def __init__(self, line_num: int, value: bool):
        super().__init__(line_num)
        self.value = value

    def __str__(self) -> str:
        return get_token_literal("TRUE") if self.value else get_token_literal("FALSE")

    def __repr__(self, **kwargs: typing.Any) -> str:
        return super().__repr__(value=self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Boolean):
            return False
        return self.line_num == other.line_num and self.value == other.value

    def eq(self, other: object) -> Expression:
        if isinstance(other, Boolean):
            return Boolean(self.line_num, self.value == other.value)
        return super().eq(other)

    def ne(self, other: object) -> "Expression":
        if isinstance(other, Boolean):
            return Boolean(self.line_num, self.value != other.value)
        return super().ne(other)

    def bang(self) -> "Expression":
        return Boolean(self.line_num, not self.value)

    def and_(self, other: object) -> "Expression":
        if isinstance(other, Boolean):
            return Boolean(self.line_num, self.value and other.value)
        return super().and_(other)

    def or_(self, other: object) -> "Expression":
        if isinstance(other, Boolean):
            return Boolean(self.line_num, self.value or other.value)
        return super().or_(other)


class List(Expression):
    def __init__(self, line_num: int, values: list[Expression]):
        super().__init__(line_num)
        self.values = values

    def __str__(self) -> str:
        return f"({', '.join(map(str, self.values))})"

    def __repr__(self, **kwargs: typing.Any) -> str:
        return super().__repr__(values=self.values)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, List):
            return False
        return self.line_num == other.line_num and self.values == other.values

    def eq(self, other: object) -> Expression:
        if isinstance(other, List):
            return Boolean(self.line_num, self.values == other.values)
        return super().eq(other)

    def ne(self, other: object) -> "Expression":
        if isinstance(other, List):
            return Boolean(self.line_num, self.values != other.values)
        return super().ne(other)

    def ptr(self, other: object) -> "Expression":
        if isinstance(other, Number) or isinstance(other, String) or isinstance(other, Boolean):
            self.values.append(other)
            return List(self.line_num, self.values)
        elif isinstance(other, List):
            self.values.extend(other.values)
            return List(self.line_num, self.values)

        return super().ptr(other)


class Identifier(Expression):
    def __init__(self, line_num: int, value: str):
        super().__init__(line_num)
        self.value = value

    def __str__(self) -> str:
        return self.value

    def __repr__(self, **kwargs: typing.Any) -> str:
        return super().__repr__(value=self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Identifier):
            return False
        return self.line_num == other.line_num and self.value == other.value


class Function(Expression):
    def __init__(self, line_num: int, parameters: list[Identifier], body: Expression):
        super().__init__(line_num)
        self.parameters = parameters
        self.body = body

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self, **kwargs: typing.Any) -> str:
        return super().__repr__(parameters=self.parameters, body=self.body)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Function):
            return False
        return self.line_num == other.line_num and self.parameters == other.parameters and self.body == other.body

    def ptr(self, other: object) -> "Expression":
        if isinstance(other, List):
            return FunctionCall(self.line_num, self, other)
        return super().ptr(other)


class FunctionCall(Expression):
    def __init__(self, line_num: int, function: Function, call_params: List):
        super().__init__(line_num)
        self.function = function
        self.call_params = call_params

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self, **kwargs: typing.Any) -> str:
        return super().__repr__(function=self.function, call_params=self.call_params)


class When(Expression):
    def __init__(self, line_num: int, expression: Expression, case_expressions: list[tuple[Expression, Expression]]):
        super().__init__(line_num)
        self.expression = expression
        self.case_expressions = case_expressions

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, When):
            return False
        return self.line_num == other.line_num and self.expression == other.expression and \
            self.case_expressions == other.case_expressions

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self, **kwargs: typing.Any) -> str:
        return super().__repr__(expression=self.expression, case_expressions=self.case_expressions)


class Output(Expression):
    """Stores representation of what is printed to the console.
    """

    def __init__(self, line_num: int, value: str):
        super().__init__(line_num)
        self.value = value

    def __str__(self) -> str:
        return self.value

    def __repr__(self, **kwargs: typing.Any) -> str:
        return super().__repr__(value=self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Output):
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

    def __repr__(self, **kwargs: typing.Any) -> str:
        return super().__repr__(name=self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BuiltinFunction):
            return False
        return self.line_num == other.line_num and self.name == other.name

    def ptr(self, other: object) -> "Expression":
        if isinstance(other, List):
            match self.name:
                case self.print_:
                    return Output(
                        self.line_num,
                        ", ".join(map(str, other.values))
                    )
                case _:
                    raise Exception(f"Unimplemented builtin function {self.name}")

        return super().ptr(other)


class UnaryExpression(Expression):
    def __init__(self, line_num: int, operator: Token, expression: Expression):
        super().__init__(line_num)
        self.operator = operator
        self.expression = expression

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self, **kwargs: typing.Any) -> str:
        return super().__repr__(operator=self.operator, expression=self.expression)

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

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self, **kwargs: typing.Any) -> str:
        return super().__repr__(left=self.left, operator=self.operator, right=self.right)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BinaryExpression):
            return False
        return self.line_num == other.line_num and self.left == other.left and self.operator == other.operator and self.right == other.right


class PostfixExpression(Expression):
    def __init__(self, line_num: int, operator: Token, expression: Expression):
        super().__init__(line_num)
        self.operator = operator
        self.expression = expression

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self, **kwargs: typing.Any) -> str:
        return super().__repr__(operator=self.operator, expression=self.expression)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PostfixExpression):
            return False
        return self.line_num == other.line_num and self.operator == other.operator and self.expression == other.expression


class Assignment(Expression):
    def __init__(self, line_num: int, name: str, value: Expression):
        super().__init__(line_num)
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self, **kwargs: typing.Any) -> str:
        return super().__repr__(name=self.name, value=self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Assignment):
            return False
        return self.line_num == other.line_num and self.name == other.name and self.value == other.value


class Error(Expression):
    def __init__(self, line_num: int, message: str):
        super().__init__(line_num)
        self.message = message

    def __str__(self) -> str:
        return self.message

    def __repr__(self, **kwargs: typing.Any) -> str:
        return super().__repr__(message=self.message)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Error):
            return False
        return self.line_num == other.line_num and self.message == other.message
