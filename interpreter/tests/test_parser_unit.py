import pytest

from . import testing_utils
from .testing_utils import create_when, assert_expression_equal
from ..parser_.ast_objects import Assignment, Number, Function, Identifier, InfixExpression, Boolean, \
    String, Expression, PostfixExpression
from ..tokens.tokenizer import Token
from ..tokens.tokens import PLUS, EQ, BANG, INC, DEC
from ..utils.utils import LanguageRuntimeException


def test_set_expression():
    p = testing_utils.parser("variable = 1;")
    actual_assign_ast = p.parse_assign()

    expected_assign_ast = Assignment(
        1,
        "variable",
        Number(1, 1)
    )

    assert_expression_equal(expected_assign_ast, actual_assign_ast)


@pytest.mark.parametrize("value, str_repr, is_whole_num", [
    (1.0, "1", True),
    (1.45, "1.45", False)
])
def test_number_string(value, str_repr, is_whole_num):
    n = Number(1, value)
    assert str(n) == str_repr
    assert n.is_whole_number() == is_whole_num


@pytest.mark.parametrize("params_str, params_list", [
    ("", []),
    ("a", [Identifier(1, "a")]),
    ("a, b", [Identifier(1, "a"), Identifier(1, "b")]),
    ("a, b, c", [Identifier(1, "a"), Identifier(1, "b"), Identifier(1, "c")]),
])
def test_parse_function(params_str, params_list):
    p = testing_utils.parser(f"func {params_str}: 0;")
    actual_function_ast = p.parse_function()

    expected_function_ast = Function(
        1,
        params_list,
        Number(1, 0)
    )
    assert_expression_equal(expected_function_ast, actual_function_ast)


@pytest.mark.parametrize("source, expected_result", [
    ("!", PostfixExpression(1, Token(1, "!", BANG), Number(1, 3))),
    ("+1", InfixExpression(1, Number(1, 3), Token(1, "+", PLUS), Number(1, 1)))
])
def test_parse_infix(source, expected_result):
    p = testing_utils.parser(source)
    infix_object = p.parse_infix(Number(1, 3))
    assert_expression_equal(expected_result, infix_object)


@pytest.mark.parametrize("source, token", [
    ("--", Token(1, "--", DEC)),
    ("++", Token(1, "++", INC))
])
def test_parse_prefix(source, token):
    p = testing_utils.parser(source)
    with pytest.raises(LanguageRuntimeException) as e:
        p.parse_prefix()
    assert str(e.value) == f"Error at line 1: invalid prefix operator: {token.type} ({token.value})"


@pytest.mark.parametrize("switch_expression, case_expressions", [
    (Boolean(1, True), [
        ("1 == 1: true", InfixExpression(2, Number(2, 1), Token(2, "==", EQ), Number(2, 1)), Boolean(2, True)),
        ("else: false", Boolean(3, True), Boolean(3, False))
    ]),
    (Identifier(1, "a"), [
        ("is 1: true", Number(2, 1), Boolean(2, True)),
        ("else: false", Identifier(3, "a"), Boolean(3, False))
    ]),
    (Boolean(1, True), [
        ("a == 1: \"1\"", InfixExpression(2, Identifier(2, "a"), Token(2, "==", EQ), Number(2, 1)), String(2, "1")),
        ("a == 2: \"2\"", InfixExpression(3, Identifier(3, "a"), Token(3, "==", EQ), Number(3, 2)), String(3, "2")),
        ("else: false", Boolean(4, True), Boolean(4, False))
    ]),
    (Identifier(1, "a"), [
        ("is 1: \"1\"", Number(2, 1), String(2, "1")),
        ("is 2: \"2\"", Number(3, 2), String(3, "2")),
        ("else: false", Identifier(4, "a"), Boolean(4, False))
    ]),
    (Boolean(1, True), [
        ("a == 1: \"1\"", InfixExpression(2, Identifier(2, "a"), Token(2, "==", EQ), Number(2, 1)), String(2, "1")),
        ("a == 2: \"2\"", InfixExpression(3, Identifier(3, "a"), Token(3, "==", EQ), Number(3, 2)), String(3, "2")),
        ("a == 3: \"3\"", InfixExpression(4, Identifier(4, "a"), Token(4, "==", EQ), Number(4, 3)), String(4, "3")),
        ("else: false", Boolean(5, True), Boolean(5, False))
    ]),
    (Identifier(1, "a"), [
        ("is 1: \"1\"", Number(2, 1), String(2, "1")),
        ("is 2: \"2\"", Number(3, 2), String(3, "2")),
        ("is 3: \"3\"", Number(4, 3), String(4, "3")),
        ("else: false", Identifier(5, "a"), Boolean(5, False))
    ]),
])
def test_when(switch_expression, case_expressions: list[tuple[str, Expression, Expression]]):
    source, expected_when_ast = create_when(1, switch_expression, case_expressions)

    p = testing_utils.parser(source)
    actual_when_ast = p.parse_when()
    assert_expression_equal(expected_when_ast, actual_when_ast)
