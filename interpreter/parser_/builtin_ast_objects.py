from random import random, uniform, randint
from typing import Callable

from interpreter.parser_.ast_objects import Expression, List, Number, String
from utils.utils import language_error


class BuiltinFunction(Expression):
    pass


class Print(BuiltinFunction):
    def __init__(self, line_num: int):
        super().__init__(line_num)

    def ptr(self, other: object) -> "Expression":
        if isinstance(other, List):
            arguments = other.values
            print(", ".join(map(str, arguments)))
            return List(self.line_num, arguments)
        return super().ptr(other)


class Input(BuiltinFunction):

    def __init__(self, line_num: int):
        super().__init__(line_num)

    def ptr(self, other: object) -> "Expression":
        if isinstance(other, List):
            arguments = other.values

            if len(arguments) != 1:
                raise language_error(self.line_num, f"expected 1 argument, got {len(arguments)}")

            prompt = arguments[0]

            if not isinstance(prompt, String):
                raise language_error(
                    self.line_num,
                    f"unsupported type {type(prompt).__name__} for built-in function len"
                )

            value = input(prompt.value)

            return String(self.line_num, value)

        return super().ptr(other)


class RandomInt(BuiltinFunction):

    def __init__(self, line_num: int):
        super().__init__(line_num)

    def ptr(self, other: object) -> "Expression":
        if isinstance(other, List):
            arguments = other.values
            if len(arguments) == 1:
                start: Expression = Number(self.line_num, 0)
                end: Expression = arguments[0]
            elif len(arguments) == 2:
                start, end = arguments
            else:
                raise language_error(
                    self.line_num,
                    f"incorrect number of arguments. Excepts 1 or 2 arguments, but got {len(arguments)}"
                )

            # Validate start value
            if not isinstance(start, Number):
                raise language_error(
                    self.line_num,
                    f"expected Number for start, got {type(start).__name__}"
                )

            if not start.is_whole_number():
                raise language_error(self.line_num, f"start must be a whole number")

            # Validate end value
            if not isinstance(end, Number):
                raise language_error(
                    self.line_num,
                    f"expected Number for end, got {type(end).__name__}"
                )

            if not end.is_whole_number():
                raise language_error(self.line_num, f"end must be a whole number")

            # Ensure start value is less than end value
            if end.value < start.value:
                raise language_error(
                    self.line_num,
                    f"end ({str(end)}) must be greater than start ({str(start)})"
                )

            return Number(
                self.line_num,
                randint(int(start.value), int(end.value))
            )

        return super().ptr(other)


class RandomFloat(BuiltinFunction):

    def __init__(self, line_num: int):
        super().__init__(line_num)

    def ptr(self, other: object) -> "Expression":
        if isinstance(other, List):
            arguments = other.values
            if len(arguments) == 0:
                return Number(self.line_num, random())
            elif len(arguments) == 1:
                start: Expression = Number(self.line_num, 0)
                end: Expression = arguments[0]
            elif len(arguments) == 2:
                start, end = arguments
            else:
                raise language_error(
                    self.line_num,
                    f"incorrect number of arguments. Excepts 0, 1, or 2 arguments, but got {len(arguments)}"
                )

            # Validate start value
            if not isinstance(start, Number):
                raise language_error(
                    self.line_num,
                    f"expected Number for start, got {type(start).__name__}"
                )

            # if not is_float and not start.is_whole_number():
            #     raise language_error(self.line_num, f"start must be a whole number")

            # Validate end value
            if not isinstance(end, Number):
                raise language_error(
                    self.line_num,
                    f"expected Number for end, got {type(end).__name__}"
                )

            # if not is_float and not end.is_whole_number():
            #     raise language_error(self.line_num, f"end must be a whole number")

            # Ensure start value is less than end value
            if end.value < start.value:
                raise language_error(
                    self.line_num,
                    f"end ({str(end)}) must be greater than start ({str(start)})"
                )

            return Number(
                self.line_num,
                uniform(start.value, end.value)
            )

        return super().ptr(other)


class Length(BuiltinFunction):

    def __init__(self, line_num: int):
        super().__init__(line_num)

    def ptr(self, other: object) -> "Expression":
        if isinstance(other, List):
            arguments = other.values
            if len(arguments) != 1:
                raise language_error(self.line_num, f"expected 1 argument, got {len(arguments)}")

            collection = arguments[0]

            if isinstance(collection, String):
                return Number(self.line_num, len(collection.value))
            elif isinstance(collection, List):
                return Number(self.line_num, len(collection.values))
            raise language_error(
                self.line_num,
                f"unsupported type {type(collection).__name__} for built-in function len"
            )

        return super().ptr(other)


class Range(BuiltinFunction):

    def __init__(self, line_num: int):
        super().__init__(line_num)

    def ptr(self, other: object) -> "Expression":
        if isinstance(other, List):
            arguments = other.values

            if len(arguments) == 1:
                start: Expression = Number(self.line_num, 0)
                end: Expression = arguments[0]
                step: Expression = Number(self.line_num, 1)
            elif len(arguments) == 2:
                start, end = arguments
                step = Number(self.line_num, 1)
            elif len(arguments) == 3:
                start, end, step = arguments
            else:
                raise language_error(
                    self.line_num,
                    f"incorrect number of arguments. Excepts 1, 2, or 3 arguments, but got {len(arguments)}"
                )

            # Validate start value
            if not isinstance(start, Number):
                raise language_error(
                    self.line_num,
                    f"expected Number for start, got {type(start).__name__}"
                )

            # Validate end value
            if not isinstance(end, Number):
                raise language_error(
                    self.line_num,
                    f"expected Number for end, got {type(end).__name__}"
                )

            # Validate step value
            if not isinstance(step, Number):
                raise language_error(
                    self.line_num,
                    f"expected Number for step, got {type(step).__name__}"
                )

            if step.value == 0:
                raise language_error(
                    self.line_num,
                    f"step cannot be 0"
                )

            # Make sure step value is correct for start and end. If "start" is greater than "end" but "step" is
            # positive, raise an error. Similarly, if "start" is less than "end" but "step" is negative, raise an error.
            if start.value > end.value and step.value > 0:
                raise language_error(
                    self.line_num,
                    f"step value must be negative if start value is greater than end value"
                )
            elif start.value < end.value and step.value < 0:
                raise language_error(
                    self.line_num,
                    f"step value must be positive if start value is less than end value"
                )

            # If "start" is less than "end", generate numbers in ascending order. Otherwise, if "start" is
            # greater than "end", generate numbers in descending order.
            is_within_range: Callable[[float, float], bool] = \
                (lambda a, b: a < b) if start.value < end.value else (lambda a, b: a > b)

            # Generate the range
            values: list[Expression] = []
            next_value = start.value
            while is_within_range(next_value, end.value):
                values.append(Number(self.line_num, next_value))
                next_value += step.value

            return List(self.line_num, values)

        return super().ptr(other)


class Round(BuiltinFunction):

    def __init__(self, line_num: int):
        super().__init__(line_num)

    def ptr(self, other: object) -> "Expression":
        if isinstance(other, List):
            arguments = other.values

            if len(arguments) != 2:
                raise language_error(
                    self.line_num,
                    f"incorrect number of arguments. Excepts 2 arguments, but got {len(arguments)}"
                )

            number, round_to = arguments

            if not isinstance(number, Number):
                raise language_error(
                    self.line_num,
                    f"expected Number for number, got {type(number).__name__}"
                )

            if not isinstance(round_to, Number):
                raise language_error(
                    self.line_num,
                    f"expected Number for round_to, got {type(round_to).__name__}"
                )

            if not round_to.is_whole_number():
                raise language_error(self.line_num, "round_to must be a whole number")

            if round_to.value < 0:
                raise language_error(self.line_num, "round_to must be greater than or equal to 0")

            return Number(
                self.line_num,
                round(number.value, int(round_to.value))
            )

        return super().ptr(other)


class Format(BuiltinFunction):

    def __init__(self, line_num: int):
        super().__init__(line_num)

    def ptr(self, other: object) -> "Expression":
        if isinstance(other, List):
            arguments = other.values

            if len(arguments) <= 0:
                raise language_error(
                    self.line_num,
                    "incorrect number of arguments. Excepted at least 1 argument, but got 0."
                )

            format_string = arguments[0]

            if not isinstance(format_string, String):
                raise language_error(
                    self.line_num,
                    f"expected String, got {type(format_string).__name__}"
                )

            # For each argument after the format string, replace each ${index} with its value
            new_string = format_string.value
            for i, arg in enumerate(arguments[1:]):
                new_string = new_string.replace(f"${i}", arg.value if isinstance(arg, String) else str(arg))

            return String(format_string.line_num, new_string)

        return super().ptr(other)
