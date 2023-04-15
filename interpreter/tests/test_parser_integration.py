import pytest

from interpreter.tokens.tokens import *
from interpreter.tokens.tokenizer import Token
from .testing_utils import create_when
from ..parser_ import parser_
from . import testing_utils
from ..parser_.ast_objects import BuiltinFunction, Boolean, Number, List, Identifier, BinaryExpression, \
    UnaryExpression, Function, String, PostfixExpression
from ..utils.utils import LanguageRuntimeException


@pytest.mark.parametrize("source, expected_value", [
    ("true", Boolean(1, True)),
    ("false", Boolean(1, False))
])
def test_boolean(source, expected_value):
    expected_ast = [
        expected_value
    ]

    parser = testing_utils.parser(f"{source};")
    actual_ast = parser.parse()
    assert actual_ast == expected_ast


@pytest.mark.parametrize("source, expected_list_values", [
    ("()", []),
    ("(1,)", [Number(1, 1)]),
    ("(1, 2)", [Number(1, 1), Number(1, 2)]),
    ("(1, 2, 3)", [Number(1, 1), Number(1, 2), Number(1, 3)])
])
def test_list(source, expected_list_values):
    expected_ast = [
        List(
            1,
            expected_list_values
        )
    ]

    parser = testing_utils.parser(f"{source};")
    actual_ast = parser.parse()
    assert actual_ast == expected_ast


@pytest.mark.parametrize("source, operator, expression", [
    ("+1", Token(1, "+", PLUS), Number(1, 1)),
    ("-1", Token(1, "-", MINUS), Number(1, 1)),
    ("!true", Token(1, "!", BANG), Boolean(1, True))
])
def test_unary_expressions(source, operator, expression):
    expected_ast = [
        UnaryExpression(1, operator, expression)
    ]

    parser = testing_utils.parser(f"{source};")
    actual_ast = parser.parse()
    assert actual_ast == expected_ast


@pytest.mark.parametrize("source, ast_object", [
    ("6!", PostfixExpression(1, Token(1, "!", BANG), Number(1, 6))),
    ("6!!", PostfixExpression(1, Token(1, "!", BANG), PostfixExpression(1, Token(1, "!", BANG), Number(1, 6)))),
    ("6--", PostfixExpression(1, Token(1, "--", DEC), Number(1, 6))),
    ("6++", PostfixExpression(1, Token(1, "++", INC), Number(1, 6))),
    ("6++--", PostfixExpression(1, Token(1, "--", DEC), PostfixExpression(1, Token(1, "++", INC), Number(1, 6)))),
    ("6--++", PostfixExpression(1, Token(1, "++", INC), PostfixExpression(1, Token(1, "--", DEC), Number(1, 6)))),
])
def test_suffix_operators(source, ast_object):
    expected_ast = [ast_object]

    parser = testing_utils.parser(f"{source};")
    actual_ast = parser.parse()
    assert actual_ast == expected_ast


@pytest.mark.parametrize("source, left, operator, right", [
    ("1+1", Number(1, 1), Token(1, "+", PLUS), Number(1, 1)),
    ("1-1", Number(1, 1), Token(1, "-", MINUS), Number(1, 1)),
    ("1*1", Number(1, 1), Token(1, "*", MULTIPLY), Number(1, 1)),
    ("1/1", Number(1, 1), Token(1, "/", DIVIDE), Number(1, 1)),
    ("a <- (1,)", Identifier(1, "a"), Token(1, "<-", POINTER), List(1, [Number(1, 1)])),
    ("true == false", Boolean(1, True), Token(1, "==", EQ), Boolean(1, False)),
    ("false != true", Boolean(1, False), Token(1, "!=", NE), Boolean(1, True)),
    ("false & false", Boolean(1, False), Token(1, "&", AND), Boolean(1, False)),
    ("true | true", Boolean(1, True), Token(1, "|", OR), Boolean(1, True)),
    ("5 > 3", Number(1, 5), Token(1, ">", GT), Number(1, 3)),
    ("4 >= 2", Number(1, 4), Token(1, ">=", GE), Number(1, 2)),
    ("6 < 12", Number(1, 6), Token(1, "<", LT), Number(1, 12)),
    ("7 <= 13", Number(1, 7), Token(1, "<=", LE), Number(1, 13)),
])
def test_binary_expressions(source, left, operator, right):
    expected_ast = [
        BinaryExpression(1, left, operator, right)
    ]

    parser = testing_utils.parser(f"{source};")
    actual_ast = parser.parse()
    assert actual_ast == expected_ast


def test_precedence_multiply():
    expected_ast = [
        BinaryExpression(
            1,
            Number(1, 1),
            Token(1, "+", PLUS),
            BinaryExpression(
                1,
                Number(1, 2),
                Token(1, "*", MULTIPLY),
                Number(1, 4)
            )
        )
    ]

    parser = testing_utils.parser("1+2*4;")
    actual_ast = parser.parse()
    assert actual_ast == expected_ast


@pytest.mark.parametrize("name, ast_object", [
    ("print", BuiltinFunction(1, "print"))
])
def test_builtin_functions(name, ast_object):
    parser = testing_utils.parser(f"{name};")
    actual_ast = parser.parse()
    assert actual_ast == [ast_object]


@pytest.mark.parametrize("source, expected_error_message", [
    ("2 + (3 + 1;", "Error at line 1: Expected CLOSED_PAREN, got SEMICOLON (';')")
])
def test_unexpected_token(source, expected_error_message):
    parser = testing_utils.parser(source)
    with pytest.raises(LanguageRuntimeException) as e:
        parser.parse()
    actual_error_mst = str(e.value)
    assert actual_error_mst == expected_error_message


@pytest.mark.parametrize("params_str, params_list, body_str, body_ast", [
    (
        # No parameters
        "", [],
        "0", Number(1, 0)
    ),
    (
        "a", [Identifier(1, "a")],
        "a", Identifier(1, "a")
    ),
    ("a, b", [Identifier(1, "a"), Identifier(1, "b")],
     "a + b", BinaryExpression(
            1,
            Identifier(1, "a"),
            Token(1, "+", PLUS),
            Identifier(1, "b")
        )
     )
])
def test_functions(params_str, params_list, body_str, body_ast):
    parser = testing_utils.parser(f"func {params_str}: {body_str};")
    actual_ast = parser.parse()
    expected_ast = [
        Function(1, params_list, body_ast)
    ]
    assert actual_ast == expected_ast


def test_function_calls():
    parser = testing_utils.parser(f"(func: 0) <- ();")
    actual_ast = parser.parse()
    expected_ast = [
        BinaryExpression(
            1,
            Function(1, [], Number(1, 0.0)),
            Token(1, "<-", POINTER),
            List(1, [])
        )
    ]
    assert actual_ast == expected_ast


@pytest.mark.parametrize("switch_expression, case_expressions", [
    (Boolean(1, True), [
        ("1 == 1: true", BinaryExpression(2, Number(2, 1), Token(2, "==", EQ), Number(2, 1)), Boolean(2, True)),
        ("else: false", Boolean(3, True), Boolean(3, False))
    ]),
    (Identifier(1, "a"), [
        ("is 1: true", Number(2, 1), Boolean(2, True)),
        ("else: false", Identifier(3, "a"), Boolean(3, False))
    ]),
    (Boolean(1, True), [
        ("a == 1: \"1\"", BinaryExpression(2, Identifier(2, "a"), Token(2, "==", EQ), Number(2, 1)), String(2, "1")),
        ("a == 2: \"2\"", BinaryExpression(3, Identifier(3, "a"), Token(3, "==", EQ), Number(3, 2)), String(3, "2")),
        ("else: false", Boolean(4, True), Boolean(4, False))
    ]),
    (Identifier(1, "a"), [
        ("is 1: \"1\"", Number(2, 1), String(2, "1")),
        ("is 2: \"2\"", Number(3, 2), String(3, "2")),
        ("else: false", Identifier(4, "a"), Boolean(4, False))
    ]),
    (Boolean(1, True), [
        ("a == 1: \"1\"", BinaryExpression(2, Identifier(2, "a"), Token(2, "==", EQ), Number(2, 1)), String(2, "1")),
        ("a == 2: \"2\"", BinaryExpression(3, Identifier(3, "a"), Token(3, "==", EQ), Number(3, 2)), String(3, "2")),
        ("a == 3: \"3\"", BinaryExpression(4, Identifier(4, "a"), Token(4, "==", EQ), Number(4, 3)), String(4, "3")),
        ("else: false", Boolean(5, True), Boolean(5, False))
    ]),
    (Identifier(1, "a"), [
        ("is 1: \"1\"", Number(2, 1), String(2, "1")),
        ("is 2: \"2\"", Number(3, 2), String(3, "2")),
        ("is 3: \"3\"", Number(4, 3), String(4, "3")),
        ("else: false", Identifier(5, "a"), Boolean(5, False))
    ]),
])
def test_when(switch_expression, case_expressions):
    source, expected_when_ast = create_when(1, switch_expression, case_expressions)
    source = f"{source};"

    p = testing_utils.parser(source)
    actual_ast = p.parse()

    expected_ast = [expected_when_ast]

    assert actual_ast == expected_ast
