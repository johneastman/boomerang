import pytest

from interpreter.tokens import tokens as t
from interpreter.tokens.tokenizer import Token
from .testing_utils import create_when, assert_expressions_equal
from . import testing_utils
from ..parser_.ast_objects import BuiltinFunction, Boolean, Number, List, Identifier, InfixExpression, \
    PrefixExpression, Function, String, PostfixExpression
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
    assert_expressions_equal(expected_ast, actual_ast)


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
    assert_expressions_equal(expected_ast, actual_ast)


@pytest.mark.parametrize("source, operator, expression", [
    ("+1", Token(1, "+", t.PLUS), Number(1, 1)),
    ("-1", Token(1, "-", t.MINUS), Number(1, 1)),
    ("!true", Token(1, "!", t.BANG), Boolean(1, True)),
    ("**(1, 2, 3)", Token(1, "**", t.PACK), List(1, [Number(1, 1), Number(1, 2), Number(1, 3)]))
])
def test_prefix_expressions(source, operator, expression):
    expected_ast = [
        PrefixExpression(1, operator, expression)
    ]

    parser = testing_utils.parser(f"{source};")
    actual_ast = parser.parse()
    assert_expressions_equal(expected_ast, actual_ast)


@pytest.mark.parametrize("source, ast_object", [
    ("6!", PostfixExpression(1, Token(1, "!", t.BANG), Number(1, 6))),
    ("6!!", PostfixExpression(1, Token(1, "!", t.BANG), PostfixExpression(1, Token(1, "!", t.BANG), Number(1, 6)))),
    ("6--", PostfixExpression(1, Token(1, "--", t.DEC), Number(1, 6))),
    ("6++", PostfixExpression(1, Token(1, "++", t.INC), Number(1, 6))),
    ("6++--", PostfixExpression(1, Token(1, "--", t.DEC), PostfixExpression(1, Token(1, "++", t.INC), Number(1, 6)))),
    ("6--++", PostfixExpression(1, Token(1, "++", t.INC), PostfixExpression(1, Token(1, "--", t.DEC), Number(1, 6)))),
])
def test_postfix_operators(source, ast_object):
    expected_ast = [ast_object]

    parser = testing_utils.parser(f"{source};")
    actual_ast = parser.parse()
    assert_expressions_equal(expected_ast, actual_ast)


@pytest.mark.parametrize("source, left, operator, right", [
    ("1+1", Number(1, 1), Token(1, "+", t.PLUS), Number(1, 1)),
    ("1-1", Number(1, 1), Token(1, "-", t.MINUS), Number(1, 1)),
    ("1*1", Number(1, 1), Token(1, "*", t.MULTIPLY), Number(1, 1)),
    ("1/1", Number(1, 1), Token(1, "/", t.DIVIDE), Number(1, 1)),
    ("a <- (1,)", Identifier(1, "a"), Token(1, "<-", t.SEND), List(1, [Number(1, 1)])),
    ("true == false", Boolean(1, True), Token(1, "==", t.EQ), Boolean(1, False)),
    ("false != true", Boolean(1, False), Token(1, "!=", t.NE), Boolean(1, True)),
    ("false & false", Boolean(1, False), Token(1, "&", t.AND), Boolean(1, False)),
    ("true | true", Boolean(1, True), Token(1, "|", t.OR), Boolean(1, True)),
    ("5 > 3", Number(1, 5), Token(1, ">", t.GT), Number(1, 3)),
    ("4 >= 2", Number(1, 4), Token(1, ">=", t.GE), Number(1, 2)),
    ("6 < 12", Number(1, 6), Token(1, "<", t.LT), Number(1, 12)),
    ("7 <= 13", Number(1, 7), Token(1, "<=", t.LE), Number(1, 13)),
])
def test_binary_expressions(source, left, operator, right):
    expected_ast = [
        InfixExpression(1, left, operator, right)
    ]

    parser = testing_utils.parser(f"{source};")
    actual_ast = parser.parse()
    assert_expressions_equal(expected_ast, actual_ast)


@pytest.mark.parametrize("source, expected_result", [
    (
        "1+2*4",
        InfixExpression(
            1,
            Number(1, 1),
            Token(1, "+", t.PLUS),
            InfixExpression(
                1,
                Number(1, 2),
                Token(1, "*", t.MULTIPLY),
                Number(1, 4)
            )
        )
    ),
    (
        "n != 0 & n % 2 == 0",
        InfixExpression(
            1,
            InfixExpression(
                1,
                Identifier(1, "n"),
                Token(1, "!=", t.NE),
                Number(1, 0)
            ),
            Token(1, "&", t.AND),
            InfixExpression(
                1,
                InfixExpression(
                    1,
                    Identifier(1, "n"),
                    Token(1, "%", t.MOD),
                    Number(1, 2)
                ),
                Token(1, "==", t.EQ),
                Number(1, 0)
            ),
        )
    ),
    (
        "-(1, 2) <- 5",
        InfixExpression(
            1,
            PrefixExpression(
                1,
                Token(1, "-", t.MINUS),
                List(1, [Number(1, 1), Number(1, 2)])
            ),
            Token(1, "<-", t.SEND),
            Number(1, 5)
        )
    ),

    # Index
    (
        "(1, 2) @ 1 + 1",
        InfixExpression(
            1,
            List(1, [Number(1, 1), Number(1, 2)]),
            Token(1, "@", t.INDEX),
            InfixExpression(
                1,
                Number(1, 1),
                Token(1, "+", t.PLUS),
                Number(1, 1)
            ),
        )
    ),
    (
        "(1, 2) @ 0 == 1",
        InfixExpression(
            1,
            InfixExpression(
                1,
                List(1, [Number(1, 1), Number(1, 2)]),
                Token(1, "@", t.INDEX),
                Number(1, 0)
            ),
            Token(1, "==", t.EQ),
            Number(1, 1)
        )
    ),
    (
        "len <- (list,) == 10",
        InfixExpression(
            1,
            InfixExpression(
                1,
                BuiltinFunction(1, "len"),
                Token(1, "<-", t.SEND),
                List(1, [Identifier(1, "list")]),
            ),
            Token(1, "==", t.EQ),
            Number(1, 10)
        )
    ),
    (
        "list @ random <- (0, 10,)",
        InfixExpression(
            1,
            Identifier(1, "list"),
            Token(1, "@", t.INDEX),
            InfixExpression(
                1,
                BuiltinFunction(1, "random"),
                Token(1, "<-", t.SEND),
                List(1, [Number(1, 0), Number(1, 10)]),
            ),
        )
    )
])
def test_precedence(source, expected_result):
    parser = testing_utils.parser(f"{source};")
    actual_ast = parser.parse()
    assert_expressions_equal([expected_result], actual_ast)


@pytest.mark.parametrize("name, expected_ast", [
    ("print", BuiltinFunction(1, "print"))
])
def test_builtin_functions(name, expected_ast):
    parser = testing_utils.parser(f"{name};")
    actual_ast = parser.parse()
    assert_expressions_equal([expected_ast], actual_ast)


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
    (
        "a, b", [Identifier(1, "a"), Identifier(1, "b")],
        "a + b", InfixExpression(
            1,
            Identifier(1, "a"),
            Token(1, "+", t.PLUS),
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
    assert_expressions_equal(expected_ast, actual_ast)


def test_function_calls():
    parser = testing_utils.parser(f"(func: 0) <- ();")
    actual_ast = parser.parse()
    expected_ast = [
        InfixExpression(
            1,
            Function(1, [], Number(1, 0.0)),
            Token(1, "<-", t.SEND),
            List(1, [])
        )
    ]
    assert_expressions_equal(expected_ast, actual_ast)


@pytest.mark.parametrize("switch_expression, case_expressions", [
    (Boolean(1, True), [
        ("1 == 1: true", InfixExpression(2, Number(2, 1), Token(2, "==", t.EQ), Number(2, 1)), Boolean(2, True)),
        ("else: false", Boolean(3, True), Boolean(3, False))
    ]),
    (Identifier(1, "a"), [
        ("is 1: true", Number(2, 1), Boolean(2, True)),
        ("else: false", Identifier(3, "a"), Boolean(3, False))
    ]),
    (Boolean(1, True), [
        ("a == 1: \"1\"", InfixExpression(2, Identifier(2, "a"), Token(2, "==", t.EQ), Number(2, 1)), String(2, "1")),
        ("a == 2: \"2\"", InfixExpression(3, Identifier(3, "a"), Token(3, "==", t.EQ), Number(3, 2)), String(3, "2")),
        ("else: false", Boolean(4, True), Boolean(4, False))
    ]),
    (Identifier(1, "a"), [
        ("is 1: \"1\"", Number(2, 1), String(2, "1")),
        ("is 2: \"2\"", Number(3, 2), String(3, "2")),
        ("else: false", Identifier(4, "a"), Boolean(4, False))
    ]),
    (Boolean(1, True), [
        ("a == 1: \"1\"", InfixExpression(2, Identifier(2, "a"), Token(2, "==", t.EQ), Number(2, 1)), String(2, "1")),
        ("a == 2: \"2\"", InfixExpression(3, Identifier(3, "a"), Token(3, "==", t.EQ), Number(3, 2)), String(3, "2")),
        ("a == 3: \"3\"", InfixExpression(4, Identifier(4, "a"), Token(4, "==", t.EQ), Number(4, 3)), String(4, "3")),
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

    assert_expressions_equal(expected_ast, actual_ast)
