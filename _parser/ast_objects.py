import typing

import tokens.tokens
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
    def __init__(self, value: Expression, children=None):
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

    def __init__(self, value: typing.Union[int, str, float, Optional[Node]], line_num: int):
        self.value = value
        self.line_num = line_num

    def __str__(self):
        return str(self.value)

    def __eq__(self, other: object):
        if not isinstance(other, self.__class__):
            return False

        if not isinstance(self.value, type(other.value)):
            return False

        return self.value == other.value and self.line_num == other.line_num

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"{class_name}(value={self.value}, line_num={self.line_num})"

    def __hash__(self):
        return hash((self.value, self.line_num))


class Integer(Factor, Base):
    def __init__(self, value: int, line_num: int):
        super().__init__(value, line_num)

    __hash__ = super.__hash__


class Float(Factor, Base):
    def __init__(self, value: float, line_num: int):
        super().__init__(value, line_num)

    __hash__ = super.__hash__


class Boolean(Factor, Base):
    def __init__(self, value: bool, line_num: int):
        super().__init__(value, line_num)

    __hash__ = super.__hash__

    def __str__(self):
        return get_token_literal("TRUE") if self.value else get_token_literal("FALSE")


class String(Factor, Base):
    def __init__(self, value: str, line_num: int):
        super().__init__(value, line_num)

    __hash__ = super.__hash__

    def __str__(self):
        return f"\"{self.value}\""


class Identifier(Factor, Base):
    def __init__(self, value: str, line_num: int):
        super().__init__(value, line_num)


class NoReturn(Factor, Base):
    def __init__(self, line_num: int = 0):
        super().__init__("", line_num)


class Tree(Factor, Base):
    def __init__(self, value: Optional[Node], line_num: int):
        super().__init__(value, line_num)

    def insert(self, item):
        temp: Node = Node(item)
        if self.value is None:
            self.value = temp
        else:
            # mypy error: Incompatible types in assignment (expression has type "Union[str, float, Node]", variable has type "Node")
            # reason for ignore: Node is in Union[str, float, Node]
            ptr: Node = self.value  # type: ignore
            while len(ptr.children) > 0:
                ptr = ptr.children[0]
            ptr.children.append(temp)
        return self.value

    def __str__(self) -> str:
        nodes: list[Node] = []
        # mypy error: Incompatible types in assignment (expression has type "Union[int, str, float, Node, None]",
        #             variable has type "Optional[Node]")
        # reason for ignore: Optional[Node] means "Node" or "None"
        tmp: Optional[Node] = self.value  # type: ignore
        while tmp is not None:
            nodes.append(tmp)
            tmp = tmp.children[0] if len(tmp.children) > 0 else None
        return f" {get_token_literal('POINTER')} ".join(map(lambda n: str(n.value), nodes))


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


class Random(BuiltinFunction):
    def __init__(self, params: list[Expression], line_num: int):
        super().__init__(params, line_num)


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


class Factorial(Expression):
    def __init__(self, expr: Expression):
        self.expr = expr


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


class SetVariable(Statement):
    def __init__(self, name: Expression, value: Expression):
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
