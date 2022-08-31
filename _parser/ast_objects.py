import typing

from tokens.tokenizer import Token
from tokens.tokens import *
from typing import Optional, Union


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


class Node(Factor):
    def __init__(self, value: Union[Expression, "Base"], children=None):
        self.value = value
        self.children: list[Node] = [] if children is None else children

    def __eq__(self, other: object):
        if not isinstance(other, Node):
            return False
        return self.value == other.value and self.children == other.children

    def __str__(self):
        return f"{self.__class__.__name__}(value={self.value}, children={self.children})"

    def __repr__(self):
        return self.__str__()


class Base:
    """Base class for lowest-level objects in the abstract syntax tree.

    Data types line integers, floats, booleans, strings, etc., but also identifiers (variables, functions, etc.)
    """

    def __init__(self,
                 value: typing.Union[int, str, float, bool, Optional[Node]],
                 line_num: int,
                 compatible_operators: list[str],
                 compatible_types: list[str]):
        self.value = value
        self.line_num = line_num

        self.compatible_operators = compatible_operators
        self.compatible_types = compatible_types

    def __str__(self) -> str:
        return str(self.value)

    def __int__(self):
        if any(isinstance(self, t) for t in [String, Boolean, Tree]):
            utils.raise_error(self.line_num, f"cannot convert {self.__class__.__name__} to {Integer.__name__}")
        return int(self.value)  # type: ignore

    def __eq__(self, other: object):
        if not isinstance(other, self.__class__):
            return False

        if not isinstance(self.value, type(other.value)):
            return False

        return self.value == other.value and self.line_num == other.line_num

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"{class_name}(value={self.value}, line_num={self.line_num})"

    def is_type_compatible(self, other: object) -> bool:
        """Check that the types are compatible. If they are not, the operation cannot be performed.

        Without this check, someone could run "1 == true" or "false != 2". Both checks are technically valid, but
        this is invalid because the data types for the left and right expressions are not compatible. However,
        to account for the fact that some expressions can result in different data types (e.g., two integers resulting
        in a float, like 3 / 4), we need to allow operations to happen on compatible data types, like floats and
        integers.
        """
        if not isinstance(other, Base):
            return False

        return type(self).__name__ in other.compatible_types or type(other).__name__ in self.compatible_types

    def is_operator_compatible(self, other: object, operator: str):
        """Check that the operation can be performed on the given types. For example, "true > false" is not valid"""
        # 'other' is None for unary operations. We just need to check that the operator is compatible with this object.
        if other is None:
            return operator in self.compatible_operators

        # 'other' is not None for binary operations, and we need to check operator compatibility for both 'self' and
        # 'other'.
        if not isinstance(other, Base):
            return False

        return operator in self.compatible_operators or operator in other.compatible_operators

    def is_compatible_with(self, other: object, operator: str) -> bool:
        if not isinstance(other, Base):
            # TODO: Add logging/throw error because this is an internal issue
            return False

        if not self.is_type_compatible(other):
            return False

        if not self.is_operator_compatible(other, operator):
            return False

        return True


class Integer(Factor, Base):
    def __init__(self, value: int, line_num: int):
        operators = [
            PLUS,
            MINUS,
            MULTIPLY,
            DIVIDE,
            EQ,
            NE,
            GT,
            GE,
            LT,
            LE
        ]

        types = [
            Integer.__name__,
            Float.__name__
        ]
        super().__init__(value, line_num, operators, types)


class Float(Factor, Base):
    def __init__(self, value: float, line_num: int):
        operators = [
            PLUS,
            MINUS,
            MULTIPLY,
            DIVIDE,
            EQ,
            NE,
            GT,
            GE,
            LT,
            LE
        ]

        types = [
            Integer.__name__,
            Float.__name__
        ]
        super().__init__(value, line_num, operators, types)


class Boolean(Factor, Base):
    def __init__(self, value: bool, line_num: int):
        operators = [
            EQ,
            NE,
            BANG,
            AND,
            OR
        ]

        types = [
            Boolean.__name__
        ]
        super().__init__(value, line_num, operators, types)

    def __str__(self):
        return get_token_literal("TRUE") if self.value else get_token_literal("FALSE")


class String(Factor, Base):
    def __init__(self, value: str, line_num: int):
        operators = [
            PLUS,
            EQ,
            NE
        ]

        types = [
            String.__name__
        ]
        super().__init__(value, line_num, operators, types)

    def __str__(self):
        return f"\"{self.value}\""


class Tree(Factor, Base):
    def __init__(self, value: Optional[Node], line_num: int):
        super().__init__(value, line_num, [], [Tree.__name__])

    def add_node(self, node: Node, add_path: str) -> None:
        assert isinstance(self.value, Node)  # for mypy type checks

        root: Node = self.value
        tmp: Node = root

        parsed_add_path = filter(None, add_path.split("."))
        for node_value in parsed_add_path:
            for child in tmp.children:
                if str(child.value.value) == node_value:  # type: ignore
                    tmp = child
                    break
        tmp.children.append(node)

    def __str__(self) -> str:
        assert isinstance(self.value, Node)

        pointer_literal = get_token_literal('POINTER')
        open_bracket_literal = get_token_literal("OPEN_BRACKET")
        closed_bracket_literal = get_token_literal("CLOSED_BRACKET")

        def traverse(node: Node):
            if len(node.children) == 0:
                return str(node.value)
            return f"{node.value} {pointer_literal} {open_bracket_literal}" \
                   f"{', '.join(traverse(child) for child in node.children)}{closed_bracket_literal}"

        if len(self.value.children) == 0:
            # To ensure the string representation is reflective of the actual syntax, a tree with no children is
            # displayed as '"root" => []' because that is how a tree with one root node and no children is defined
            # syntactically.
            return f"{self.value.value} {pointer_literal} {open_bracket_literal}{closed_bracket_literal}"
        return traverse(self.value)


class NoReturn(Factor, Base):
    def __init__(self, line_num: int = 0) -> None:
        super().__init__("", line_num, [], [])


class Identifier(Factor):
    def __init__(self, value: str, line_num: int) -> None:
        self.value = value
        self.line_num = line_num

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Identifier):
            return False
        return self.value == other.value and self.line_num == other.line_num


class FunctionCall(Factor):
    def __init__(self, name: Token, parameter_values):
        self.name = name
        self.parameter_values = parameter_values

    def __repr__(self):
        return f"[{self.__class__.__name__}(name={self.name}, parameter_values={self.parameter_values})]"


class BuiltinFunction(Factor):
    def __init__(self, params: list[Expression], line_num: int, num_params: int):
        self.params = params
        self.line_num = line_num
        self.num_params = num_params

    def __eq__(self, other: object):
        if not isinstance(other, BuiltinFunction):
            return False
        return self.params == other.params and self.line_num == other.line_num

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"{class_name}({self.params}, {self.line_num})"


class Print(BuiltinFunction):
    def __init__(self, params: list[Expression], line_num: int):
        super().__init__(params, line_num, -1)


class AddNode(BuiltinFunction):
    def __init__(self, params: list[Expression], line_num: int):
        super().__init__(params, line_num, 3)


class Random(BuiltinFunction):
    def __init__(self, params: list[Expression], line_num: int):
        super().__init__(params, line_num, 0)


class ToType(BuiltinFunction):
    def __init__(self, params: list[Expression], line_num: int, _type: typing.Type):
        super().__init__(params, line_num, 1)
        self.type: typing.Type = _type

        # Ignore for mypy because "str", "int", etc are Type objects and "String", "Integer", etc. are Base objects
        self.types: dict[typing.Type, typing.Type[Base]] = {
            str: String,  # type: ignore
            int: Integer  # type: ignore
        }

    def get_language_type(self) -> Optional[typing.Type[Base]]:
        return self.types.get(self.type, None)


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
        return f"{self.__class__.__name__}(condition: {self.condition}, statements: {self.statements})"

    def __eq__(self, other: object):
        if not isinstance(other, Loop):
            return False
        return self.condition == other.condition and self.statements == other.statements


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


class Factorial(Expression):
    def __init__(self, expr: Expression):
        self.expr = expr


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


class SetVariable(Statement):
    def __init__(self, name: Identifier, value: Expression):
        self.name = name
        self.value = value

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"{class_name}(name={self.name}, value={self.value})"

    def __eq__(self, other):
        if not isinstance(other, SetVariable):
            return False
        return self.name == other.name and self.value == other.value


class UnaryOperation(Factor):
    def __init__(self, op: Token, expression):
        self.op = op
        self.expression = expression

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"[{class_name}(op={self.op}, expression={self.expression})]"
