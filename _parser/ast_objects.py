import typing

from tokens.tokenizer import Token


class Node:
    def __init__(self, type_: str, line_num: int, value: str = "", params: typing.Optional[dict[str, "Node"]] = None):
        self.type = type_
        self.line_num = line_num

        self.value = value
        self.params = params if params is not None else {}

    def get_param(self, key: str) -> "Node":
        value = self.params.get(key, None)
        if value is None:
            raise Exception(f"No param with key '{key}' found. Node: {repr(self)}")
        return value

    def __eq__(self, other: object) -> bool:
        # Implementation needed for tests
        if not isinstance(other, Node):
            return False

        return self.type == other.type and self.line_num == other.line_num and self.value == other.value and self.params == other.params

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(type={self.type}, line_num={self.line_num}, value={self.value}, params={self.params})"

    def __str__(self) -> str:
        return self.value


def create_integer(value: int, line_num: int) -> Node:
    return Node("integer", line_num, str(value))


def create_float(value: float, line_num: int) -> Node:
    return Node("float", line_num, str(value))


def create_identifier(value: str, line_num: int) -> Node:
    return Node("identifier", line_num, value)


def create_unary_expression(operator: Token, expression: Node) -> Node:
    params = {
        "expression": expression,
        "operator": Node(operator.type, operator.line_num, operator.value)
    }
    return Node("unary_expression", operator.line_num, "", params)


def create_binary_expression(left: Node, operator: Token, right: Node) -> Node:
    params = {
        "left": left,
        "operator": Node(operator.type, operator.line_num, operator.value),
        "right": right
    }
    return Node("binary_expression", operator.line_num, "", params)


def create_assignment_statement(identifier: str, line_num: int, value: Node) -> Node:
    params = {
        "identifier": create_identifier(identifier, line_num),
        "value": value
    }
    return Node("assign", line_num, "", params)
