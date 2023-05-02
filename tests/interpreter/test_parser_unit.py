import pytest

import tests.testing_utils as testing_utils
from tests.testing_utils import create_when, assert_expression_equal
import interpreter.parser_.ast_objects as o
from interpreter.tokens.tokenizer import Token
from interpreter.tokens.tokens import PLUS, EQ, BANG, INC, DEC
from interpreter.utils.utils import LanguageRuntimeException


def test_set_expression():
    p = testing_utils.parser("variable = 1;")
    actual_assign_ast = p.parse_assign()

    expected_assign_ast = o.Assignment(
        1,
        "variable",
        o.Number(1, 1)
    )

    assert_expression_equal(expected_assign_ast, actual_assign_ast)


@pytest.mark.parametrize("value, str_repr, is_whole_num", [
    (1.0, "1", True),
    (1.45, "1.45", False)
])
def test_number_string(value, str_repr, is_whole_num):
    n = o.Number(1, value)
    assert str(n) == str_repr
    assert n.is_whole_number() == is_whole_num


@pytest.mark.parametrize("params_str, params_list", [
    ("", []),
    ("a", [o.Identifier(1, "a")]),
    ("a, b", [o.Identifier(1, "a"), o.Identifier(1, "b")]),
    ("a, b, c", [o.Identifier(1, "a"), o.Identifier(1, "b"), o.Identifier(1, "c")]),
])
def test_parse_function(params_str, params_list):
    p = testing_utils.parser(f"func {params_str}: 0;")
    actual_function_ast = p.parse_function()

    expected_function_ast = o.Function(
        1,
        params_list,
        o.Number(1, 0)
    )
    assert_expression_equal(expected_function_ast, actual_function_ast)


@pytest.mark.parametrize("source, expected_result", [
    ("!", o.PostfixExpression(1, Token(1, "!", BANG), o.Number(1, 3))),
    ("+1", o.InfixExpression(1, o.Number(1, 3), Token(1, "+", PLUS), o.Number(1, 1)))
])
def test_parse_infix(source, expected_result):
    p = testing_utils.parser(source)
    infix_object = p.parse_infix(o.Number(1, 3))
    assert_expression_equal(expected_result, infix_object)


@pytest.mark.parametrize("source, token", [
    ("--", Token(1, "--", DEC)),
    ("++", Token(1, "++", INC))
])
def test_parse_prefix_invalid_operators(source, token):
    p = testing_utils.parser(source)
    with pytest.raises(LanguageRuntimeException) as e:
        p.parse_prefix()
    assert str(e.value) == f"Error at line 1: invalid prefix operator: {token.type} ('{token.value}')"


@pytest.mark.parametrize("switch_expression, case_expressions", [
    (o.Boolean(1, True), [
        (
            "1 == 1: true",
            o.InfixExpression(2, o.Number(2, 1), Token(2, "==", EQ),o.Number(2, 1)),
            o.Boolean(2, True)
        ),
        (
            "else: false",
            o.Boolean(3, True),
            o.Boolean(3, False)
        )
    ]),
    (o.Identifier(1, "a"), [
        (
            "is 1: true",
            o.Number(2, 1),
            o.Boolean(2, True)
        ),
        (
            "else: false",
            o.Identifier(3, "a"),
            o.Boolean(3, False)
        )
    ]),
    (o.Boolean(1, True), [
        (
            "a == 1: \"1\"",
            o.InfixExpression(2, o.Identifier(2, "a"), Token(2, "==", EQ), o.Number(2, 1)),
            o.String(2, "1")
        ),
        (
            "a == 2: \"2\"",
            o.InfixExpression(3, o.Identifier(3, "a"), Token(3, "==", EQ), o.Number(3, 2)),
            o.String(3, "2")
        ),
        (
            "else: false",
            o.Boolean(4, True),
            o.Boolean(4, False)
        )
    ]),
    (o.Identifier(1, "a"), [
        (
            "is 1: \"1\"",
            o.Number(2, 1),
            o.String(2, "1")
        ),
        (
            "is 2: \"2\"",
            o.Number(3, 2),
            o.String(3, "2")
        ),
        (
            "else: false",
            o.Identifier(4, "a"),
            o.Boolean(4, False)
        )
    ]),
    (o.Boolean(1, True), [
        (
            "a == 1: \"1\"",
            o.InfixExpression(2, o.Identifier(2, "a"), Token(2, "==", EQ), o.Number(2, 1)),
            o.String(2, "1")
        ),
        (
            "a == 2: \"2\"",
            o.InfixExpression(3, o.Identifier(3, "a"), Token(3, "==", EQ), o.Number(3, 2)),
            o.String(3, "2")
        ),
        (
            "a == 3: \"3\"", o.InfixExpression(4, o.Identifier(4, "a"), Token(4, "==", EQ), o.Number(4, 3)),
            o.String(4, "3")
        ),
        (
            "else: false",
            o.Boolean(5, True),
            o.Boolean(5, False)
        )
    ]),
    (o.Identifier(1, "a"), [
        (
            "is 1: \"1\"",
            o.Number(2, 1),
            o.String(2, "1")
        ),
        (
            "is 2: \"2\"",
            o.Number(3, 2),
            o.String(3, "2")
        ),
        (
            "is 3: \"3\"",
            o.Number(4, 3),
            o.String(4, "3")
        ),
        (
            "else: false",
            o.Identifier(5, "a"),
            o.Boolean(5, False)
        )
    ]),
])
def test_when(switch_expression, case_expressions: list[tuple[str, o.Expression, o.Expression]]):
    source, expected_when_ast = create_when(1, switch_expression, case_expressions)

    p = testing_utils.parser(source)
    actual_when_ast = p.parse_when()
    assert_expression_equal(expected_when_ast, actual_when_ast)


def test_for_loop():
    source = "for i in (1, 2, 3): i + 1;"

    expected_for_object = o.ForLoop(
        1,
        "i",
        o.List(1, [o.Number(1, 1), o.Number(1, 2), o.Number(1, 3)]),
        o.InfixExpression(
            1,
            o.Identifier(1, "i"),
            Token(1, "+", PLUS),
            o.Number(1, 1)
        )
    )

    p = testing_utils.parser(source)
    actual_when_ast = p.parse_for()
    assert_expression_equal(expected_for_object, actual_when_ast)


@pytest.mark.parametrize("source, error_message", [
    ("for", "Error at line 1: expected IDENTIFIER, got EOF ('')"),
    ("for i", "Error at line 1: expected IN, got EOF ('')"),
    ("for i in (1, 2)", "Error at line 1: expected COLON, got EOF ('')"),
    ("for i in (1, 2):", "Error at line 1: invalid prefix operator: EOF ('')"),
])
def test_for_loop_error(source, error_message):
    p = testing_utils.parser(source)

    with pytest.raises(LanguageRuntimeException) as e:
        p.parse_for()

    assert str(e.value) == error_message
