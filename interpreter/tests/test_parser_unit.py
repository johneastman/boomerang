import pytest

from . import testing_utils
from ..parser_.ast_objects import Assignment, Number, Function, Identifier, Factorial, BinaryExpression
from ..tokens.tokenizer import Token
from ..tokens.tokens import PLUS


def test_set_expression():
    p = testing_utils.parser("variable = 1;")
    actual_assign_ast = p.parse_assign()

    expected_assign_ast = Assignment(
        1,
        "variable",
        Number(1, 1)
    )

    assert actual_assign_ast == expected_assign_ast


@pytest.mark.parametrize("value, str_repr, is_whole_num", [
    (1.0, "1", True),
    (1.45, "1.45", False)
])
def test_number_string(value, str_repr, is_whole_num):
    n = Number(1, value)
    assert str(n) == str_repr
    assert n.is_whole_number() == is_whole_num


@pytest.mark.parametrize("params_str, params_list", [
    ("()", []),
    ("(a,)", [Identifier(1, "a")]),
    ("(c)", [Identifier(1, "c")]),  # comma after list param is optional
    ("(a, b)", [Identifier(1, "a"), Identifier(1, "b")]),
    ("(a, b, c)", [Identifier(1, "a"), Identifier(1, "b"), Identifier(1, "c")]),
])
def test_parse_function(params_str, params_list):
    p = testing_utils.parser(f"func{params_str}: 0;")
    actual_function_ast = p.parse_function()

    expected_function_ast = Function(
        1,
        params_list,
        Number(1, 0)
    )

    assert actual_function_ast == expected_function_ast


@pytest.mark.parametrize("source, expected_result", [
    ("!", Factorial(1, Number(1, 3))),
    ("+1", BinaryExpression(1, Number(1, 3), Token("+", PLUS, 1), Number(1, 1)))
])
def test_parse_infix(source, expected_result):
    p = testing_utils.parser(source)
    infix_object = p.parse_infix(Number(1, 3))
    assert infix_object == expected_result
