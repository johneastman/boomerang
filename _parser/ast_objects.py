import typing

from tokens.tokens import *
from typing import Optional, Union

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


class Base:
    """Base class for lowest-level objects in the abstract syntax tree.

    Data types line integers, floats, booleans, strings, etc., but also identifiers (variables, functions, etc.)
    """

    def __init__(self,
                 value: typing.Any,
                 line_num: int,
                 conversion_types: list[str]):
        self.value = value
        self.line_num = line_num

        # NOTE: These two lists had to be lists of strings because using just the types was causing issues with mypy
        # and type checking
        self.conversion_types = conversion_types

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

    def bang(self) -> "Base":
        utils.raise_error(self.line_num, f"Cannot perform {BANG} operation on {type(self).__name__}")

    def equals(self, other: "Base") -> "Base":

        if type(self) == type(other):
            return Boolean(self.value == other.value, self.line_num)

        utils.raise_error(
            self.line_num,
            f"Cannot perform {EQ} operation on {type(self).__name__} and {type(other).__name__}")

    def not_equals(self, other: "Base") -> "Base":

        if type(self) == type(other):
            return Boolean(self.value != other.value, self.line_num)

        utils.raise_error(
            self.line_num,
            f"Cannot perform {NE} operation on {type(self).__name__} and {type(other).__name__}")

    def greater_than(self, other: "Base") -> "Base":
        utils.raise_error(
            self.line_num,
            f"Cannot perform {GT} operation on {type(self).__name__} and {type(other).__name__}")

    def greater_than_or_equal(self, other: "Base") -> "Base":
        utils.raise_error(
            self.line_num,
            f"Cannot perform {GE} operation on {type(self).__name__} and {type(other).__name__}")

    def less_than(self, other: "Base") -> "Base":
        utils.raise_error(
            self.line_num,
            f"Cannot perform {LT} operation on {type(self).__name__} and {type(other).__name__}")

    def less_than_or_equal(self, other: "Base") -> "Base":
        utils.raise_error(
            self.line_num,
            f"Cannot perform {LE} operation on {type(self).__name__} and {type(other).__name__}")

    def and_(self, other: "Base") -> "Base":

        if isinstance(other, Boolean):
            return Boolean(self.value and other.value, self.line_num)

        utils.raise_error(
            self.line_num,
            f"Cannot perform {AND} operation on {type(self).__name__} and {type(other).__name__}")

    def or_(self, other: "Base") -> "Base":

        if isinstance(other, Boolean):
            return Boolean(self.value or other.value, self.line_num)

        utils.raise_error(
            self.line_num,
            f"Cannot perform {OR} operation on {type(self).__name__} and {type(other).__name__}")

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

    def convert_to(self, _type: typing.Type["Base"]) -> "Base":
        if type(self) == _type:
            # Do not try to convert the object if the type of 'self' is the same as '_type'. This check is why the type
            # of self does not need to be declared in 'self.conversion_types'
            return self

        if _type.__name__ not in self.conversion_types:
            utils.raise_error(self.line_num, f"cannot convert {self.__class__.__name__} to {_type.__name__}")

        try:
            if _type == Integer:
                return Integer(int(self), self.line_num)
            elif _type == Float:
                return Float(float(self), self.line_num)
            elif _type == String:
                return String(str(self), self.line_num)
            elif _type == Boolean:
                return Boolean(bool(self), self.line_num)
            else:
                raise Exception(f"Invalid type: {_type.__name__}")
        except (TypeError, ValueError):
            utils.raise_error(
                self.line_num,
                f"cannot convert '{str(self)}' of type {self.__class__.__name__} to {_type.__name__}")


class Integer(Base, Factor):
    def __init__(self, value: int, line_num: int) -> None:
        conversion_types = [
            Float.__name__,
            String.__name__
        ]
        super().__init__(value, line_num, conversion_types)

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

    def greater_than(self, other: "Base") -> "Base":
        result = self.value > other.value
        if isinstance(other, Integer):
            return Boolean(result, self.line_num)

        elif isinstance(other, Float):
            return Boolean(result, self.line_num)

        return super().greater_than(other)

    def greater_than_or_equal(self, other: "Base") -> "Base":
        result = self.value >= other.value
        if isinstance(other, Integer):
            return Boolean(result, self.line_num)

        elif isinstance(other, Float):
            return Boolean(result, self.line_num)

        return super().greater_than_or_equal(other)

    def less_than(self, other: "Base") -> "Base":
        result = self.value < other.value
        if isinstance(other, Integer):
            return Boolean(result, self.line_num)

        elif isinstance(other, Float):
            return Boolean(result, self.line_num)

        return super().less_than(other)

    def less_than_or_equal(self, other: "Base") -> "Base":
        result = self.value >= other.value
        if isinstance(other, Integer):
            return Boolean(result, self.line_num)

        elif isinstance(other, Float):
            return Boolean(result, self.line_num)

        return super().less_than_or_equal(other)


class Float(Base, Factor):
    def __init__(self, value: float, line_num: int) -> None:
        conversion_types = [
            Integer.__name__,
            String.__name__
        ]
        super().__init__(value, line_num, conversion_types)

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


class Boolean(Base, Factor):
    def __init__(self, value: bool, line_num: int):
        conversion_types = [
            String.__name__
        ]
        super().__init__(value, line_num, conversion_types)

    def bang(self) -> "Base":
        return Boolean(not self.value, self.line_num)

    def __str__(self) -> str:
        return get_token_literal("TRUE") if self.value else get_token_literal("FALSE")


class String(Base, Factor):
    def __init__(self, value: str, line_num: int) -> None:

        conversion_types = [
            Integer.__name__,
            Float.__name__
        ]

        super().__init__(value, line_num, conversion_types)

    def add(self, other: Base) -> Base:
        if isinstance(other, String):
            return String(self.value + other.value, self.line_num)
        return super().add(other)

    def __str__(self) -> str:
        return f"\"{self.value}\""


class Node(Base, Factor):
    def __init__(self, value: Union[Expression, "Base"], line_num: int, children: Optional[list["Node"]] = None) -> None:
        super().__init__(value, line_num, [])
        self.children = [] if children is None else children

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return False
        return self.value == other.value and self.children == other.children

    def add_node(self, node: "Node", add_path: str) -> None:

        root: Node = self
        tmp: Node = root

        parsed_add_path = filter(None, add_path.split("."))
        for node_value in parsed_add_path:
            for child in tmp.children:
                if str(child.value) == node_value:
                    tmp = child
                    break
        tmp.children.append(node)

    def __str__(self) -> str:
        pointer_literal = get_token_literal("EDGE")
        open_bracket_literal = get_token_literal("OPEN_BRACKET")
        closed_bracket_literal = get_token_literal("CLOSED_BRACKET")

        def traverse(node: Node) -> str:
            if len(node.children) == 0:
                return str(node.value)
            return f"{node.value} {pointer_literal} {open_bracket_literal}" \
                   f"{', '.join(traverse(child) for child in node.children)}{closed_bracket_literal}"

        if len(self.children) == 0:
            # To ensure the string representation is reflective of the actual syntax, a tree with no children is
            # displayed as '"root" => []' because that is how a tree with one root node and no children is defined
            # syntactically.
            return f"{self.value} {pointer_literal} {open_bracket_literal}{closed_bracket_literal}"
        return traverse(self)

    def __repr__(self) -> str:
        return self.__str__()


# class Tree(Base, Factor):
#     def __init__(self, value: Optional[Node], line_num: int) -> None:
#         super().__init__(value, line_num, [])
#
#     def add_node(self, node: Node, add_path: str) -> None:
#         assert isinstance(self.value, Node)  # for mypy type checks
#
#         root: Node = self.value
#         tmp: Node = root
#
#         parsed_add_path = filter(None, add_path.split("."))
#         for node_value in parsed_add_path:
#             for child in tmp.children:
#                 if str(child.value.value) == node_value:  # type: ignore
#                     tmp = child
#                     break
#         tmp.children.append(node)
#
#     def __str__(self) -> str:
#         assert isinstance(self.value, Node)
#
#         pointer_literal = get_token_literal("EDGE")
#         open_bracket_literal = get_token_literal("OPEN_BRACKET")
#         closed_bracket_literal = get_token_literal("CLOSED_BRACKET")
#
#         def traverse(node: Node) -> str:
#             if len(node.children) == 0:
#                 return str(node.value)
#             return f"{node.value} {pointer_literal} {open_bracket_literal}" \
#                    f"{', '.join(traverse(child) for child in node.children)}{closed_bracket_literal}"
#
#         if len(self.value.children) == 0:
#             # To ensure the string representation is reflective of the actual syntax, a tree with no children is
#             # displayed as '"root" => []' because that is how a tree with one root node and no children is defined
#             # syntactically.
#             return f"{self.value.value} {pointer_literal} {open_bracket_literal}{closed_bracket_literal}"
#         return traverse(self.value)


class NoReturn(Base, Factor):
    def __init__(self, line_num: int = 0) -> None:
        super().__init__("", line_num, [])


class Identifier(Factor):
    def __init__(self, value: str, line_num: int) -> None:
        self.value = value
        self.line_num = line_num

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Identifier):
            return False
        return self.value == other.value and self.line_num == other.line_num


class FunctionCall(Factor):
    def __init__(self, name: str, parameter_values: list[Expression], line_num: int) -> None:
        self.name = name
        self.parameter_values = parameter_values
        self.line_num = line_num

    def __repr__(self) -> str:
        return f"[{self.__class__.__name__}(name={self.name}, parameter_values={self.parameter_values})]"


class BuiltinFunction(Factor):
    def __init__(self, params: list[Expression], line_num: int, num_params: int) -> None:
        self.params = params
        self.line_num = line_num
        self.num_params = num_params

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BuiltinFunction):
            return False
        return self.params == other.params and self.line_num == other.line_num

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}({self.params}, {self.line_num})"


class Print(BuiltinFunction):
    def __init__(self, params: list[Expression], line_num: int) -> None:
        super().__init__(params, line_num, -1)


class AddNode(BuiltinFunction):
    def __init__(self, params: list[Expression], line_num: int) -> None:
        super().__init__(params, line_num, 3)


class Random(BuiltinFunction):
    def __init__(self, params: list[Expression], line_num: int) -> None:
        super().__init__(params, line_num, 0)


class ToType(BuiltinFunction):
    def __init__(self, params: list[Expression], line_num: int, _type: typing.Type[Base]) -> None:
        super().__init__(params, line_num, 1)
        self.type: typing.Type[Base] = _type


class Return(Statement):
    def __init__(self, expr: Expression) -> None:
        self.expr = expr

    def __repr__(self) -> str:
        return f"[{self.__class__.__name__}(value={self.expr})]"


class Loop(Statement):
    def __init__(self, condition: Expression, statements: list[Statement]) -> None:
        self.condition = condition
        self.statements = statements

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(condition: {self.condition}, statements: {self.statements})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Loop):
            return False
        return self.condition == other.condition and self.statements == other.statements


class AssignFunction(Statement):
    def __init__(self, name: "Token", parameters: list["Token"], statements: list[Statement]) -> None:
        self.name = name
        self.parameters = parameters
        self.statements = statements

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(parameters={self.parameters}, statements={self.statements})"


class IfStatement(Statement):
    def __init__(self,
                 comparison: Expression,
                 true_statements: list[Statement],
                 false_statements: Optional[list[Statement]]) -> None:
        self.comparison = comparison
        self.true_statements = true_statements
        self.false_statements = false_statements


class Factorial(Expression):
    def __init__(self, expr: Expression) -> None:
        self.expr = expr


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
