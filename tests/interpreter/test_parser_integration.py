import pytest

from interpreter.tokens import tokens as t
from interpreter.tokens.tokenizer import Token
from tests.testing_utils import create_when, assert_expressions_equal
import tests.testing_utils as testing_utils
import interpreter.parser_.ast_objects as o
from utils.utils import LanguageRuntimeException


@pytest.mark.parametrize("source, expected_value", [
    ("true", o.Boolean(1, True)),
    ("false", o.Boolean(1, False))
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
    ("(1,)", [o.Number(1, 1)]),
    ("(1, 2)", [o.Number(1, 1), o.Number(1, 2)]),
    ("(1, 2, 3)", [o.Number(1, 1), o.Number(1, 2), o.Number(1, 3)])
])
def test_list(source, expected_list_values):
    expected_ast = [
        o.List(
            1,
            expected_list_values
        )
    ]

    parser = testing_utils.parser(f"{source};")
    actual_ast = parser.parse()
    assert_expressions_equal(expected_ast, actual_ast)


@pytest.mark.parametrize("source, operator, expression", [
    ("+1", Token(1, "+", t.PLUS), o.Number(1, 1)),
    ("-1", Token(1, "-", t.MINUS), o.Number(1, 1)),
    ("not true", Token(1, "not", t.NOT), o.Boolean(1, True)),
    ("**(1, 2, 3)", Token(1, "**", t.PACK), o.List(1, [o.Number(1, 1), o.Number(1, 2), o.Number(1, 3)]))
])
def test_prefix_expressions(source, operator, expression):
    expected_ast = [
        o.PrefixExpression(1, operator, expression)
    ]

    parser = testing_utils.parser(f"{source};")
    actual_ast = parser.parse()
    assert_expressions_equal(expected_ast, actual_ast)


@pytest.mark.parametrize("source, ast_object", [
    (
        "6!",
        o.PostfixExpression(1, Token(1, "!", t.BANG),o.Number(1, 6))
    ),
    (
        "6!!",
        o.PostfixExpression(1, Token(1, "!", t.BANG), o.PostfixExpression(1, Token(1, "!", t.BANG), o.Number(1, 6)))
    ),
    (
        "6--",
        o.PostfixExpression(1, Token(1, "--", t.DEC), o.Number(1, 6))
    ),
    (
        "6++",
        o.PostfixExpression(1, Token(1, "++", t.INC), o.Number(1, 6))
    ),
    (
        "6++--",
        o.PostfixExpression(1, Token(1, "--", t.DEC), o.PostfixExpression(1, Token(1, "++", t.INC), o.Number(1, 6)))
    ),
    (
        "6--++",
        o.PostfixExpression(1, Token(1, "++", t.INC), o.PostfixExpression(1, Token(1, "--", t.DEC), o.Number(1, 6)))
    ),
])
def test_postfix_operators(source, ast_object):
    expected_ast = [ast_object]

    parser = testing_utils.parser(f"{source};")
    actual_ast = parser.parse()
    assert_expressions_equal(expected_ast, actual_ast)


@pytest.mark.parametrize("source, left, operator, right", [
    ("1+1", o.Number(1, 1), Token(1, "+", t.PLUS), o.Number(1, 1)),
    ("1-1", o.Number(1, 1), Token(1, "-", t.MINUS), o.Number(1, 1)),
    ("1*1", o.Number(1, 1), Token(1, "*", t.MULTIPLY), o.Number(1, 1)),
    ("1/1", o.Number(1, 1), Token(1, "/", t.DIVIDE), o.Number(1, 1)),
    ("a <- (1,)", o.Identifier(1, "a"), Token(1, "<-", t.SEND), o.List(1, [o.Number(1, 1)])),
    ("true == false", o.Boolean(1, True), Token(1, "==", t.EQ), o.Boolean(1, False)),
    ("false != true", o.Boolean(1, False), Token(1, "!=", t.NE), o.Boolean(1, True)),
    ("false and false", o.Boolean(1, False), Token(1, "and", t.AND), o.Boolean(1, False)),
    ("true or true", o.Boolean(1, True), Token(1, "or", t.OR), o.Boolean(1, True)),
    ("true xor true", o.Boolean(1, True), Token(1, "xor", t.XOR), o.Boolean(1, True)),
    ("5 > 3", o.Number(1, 5), Token(1, ">", t.GT), o.Number(1, 3)),
    ("4 >= 2", o.Number(1, 4), Token(1, ">=", t.GE), o.Number(1, 2)),
    ("6 < 12", o.Number(1, 6), Token(1, "<", t.LT), o.Number(1, 12)),
    ("7 <= 13", o.Number(1, 7), Token(1, "<=", t.LE), o.Number(1, 13)),
])
def test_infix_expressions(source, left, operator, right):
    expected_ast = [
        o.InfixExpression(1, left, operator, right)
    ]

    parser = testing_utils.parser(f"{source};")
    actual_ast = parser.parse()
    assert_expressions_equal(expected_ast, actual_ast)


@pytest.mark.parametrize("source, expected_result", [
    (
        "1+2*4",
        o.InfixExpression(
            1,
            o.Number(1, 1),
            Token(1, "+", t.PLUS),
            o.InfixExpression(
                1,
                o.Number(1, 2),
                Token(1, "*", t.MULTIPLY),
                o.Number(1, 4)
            )
        )
    ),
    (
        "n != 0 and n % 2 == 0",
        o.InfixExpression(
            1,
            o.InfixExpression(
                1,
                o.Identifier(1, "n"),
                Token(1, "!=", t.NE),
                o.Number(1, 0)
            ),
            Token(1, "and", t.AND),
            o.InfixExpression(
                1,
                o.InfixExpression(
                    1,
                    o.Identifier(1, "n"),
                    Token(1, "%", t.MOD),
                    o.Number(1, 2)
                ),
                Token(1, "==", t.EQ),
                o.Number(1, 0)
            ),
        )
    ),
    (
        "-(1, 2) <- 5",
        o.InfixExpression(
            1,
            o.PrefixExpression(
                1,
                Token(1, "-", t.MINUS),
                o.List(1, [o.Number(1, 1), o.Number(1, 2)])
            ),
            Token(1, "<-", t.SEND),
            o.Number(1, 5)
        )
    ),

    # Index
    (
        "(1, 2) @ 1 + 1",
        o.InfixExpression(
            1,
            o.List(1, [o.Number(1, 1), o.Number(1, 2)]),
            Token(1, "@", t.INDEX),
            o.InfixExpression(
                1,
                o.Number(1, 1),
                Token(1, "+", t.PLUS),
                o.Number(1, 1)
            ),
        )
    ),
    (
        "(1, 2) @ 0 == 1",
        o.InfixExpression(
            1,
            o.InfixExpression(
                1,
                o.List(1, [o.Number(1, 1), o.Number(1, 2)]),
                Token(1, "@", t.INDEX),
                o.Number(1, 0)
            ),
            Token(1, "==", t.EQ),
            o.Number(1, 1)
        )
    ),
    (
        "len <- (list,) == 10",
        o.InfixExpression(
            1,
            o.InfixExpression(
                1,
                o.BuiltinFunction(1, "len"),
                Token(1, "<-", t.SEND),
                o.List(1, [o.Identifier(1, "list")]),
            ),
            Token(1, "==", t.EQ),
            o.Number(1, 10)
        )
    ),
    (
        "list @ randint <- (0, 10,)",
        o.InfixExpression(
            1,
            o.Identifier(1, "list"),
            Token(1, "@", t.INDEX),
            o.InfixExpression(
                1,
                o.BuiltinFunction(1, "randint"),
                Token(1, "<-", t.SEND),
                o.List(1, [o.Number(1, 0), o.Number(1, 10)]),
            ),
        )
    ),
    (
        "3 ** 2 * 2",
        o.InfixExpression(
            1,
            o.InfixExpression(
                1,
                o.Number(1, 3),
                Token(1, "**", t.PACK),
                o.Number(1, 2)
            ),
            Token(1, "*", t.MULTIPLY),
            o.Number(1, 2)
        )
    )
])
def test_precedence(source, expected_result):
    parser = testing_utils.parser(f"{source};")
    actual_ast = parser.parse()
    assert_expressions_equal([expected_result], actual_ast)


@pytest.mark.parametrize("name, expected_ast", [
    ("print", o.BuiltinFunction(1, "print"))
])
def test_builtin_functions(name, expected_ast):
    parser = testing_utils.parser(f"{name};")
    actual_ast = parser.parse()
    assert_expressions_equal([expected_ast], actual_ast)


@pytest.mark.parametrize("source, expected_error_message", [
    ("2 + (3 + 1;", "Error at line 1: expected CLOSED_PAREN, got SEMICOLON (';')")
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
        "0", o.Number(1, 0)
    ),
    (
        "a", [o.Identifier(1, "a")],
        "a", o.Identifier(1, "a")
    ),
    (
        "a, b", [o.Identifier(1, "a"), o.Identifier(1, "b")],
        "a + b", o.InfixExpression(
            1,
            o.Identifier(1, "a"),
            Token(1, "+", t.PLUS),
            o.Identifier(1, "b")
        )
     )
])
def test_functions(params_str, params_list, body_str, body_ast):
    parser = testing_utils.parser(f"func {params_str}: {body_str};")
    actual_ast = parser.parse()
    expected_ast = [
        o.Function(1, params_list, body_ast)
    ]
    assert_expressions_equal(expected_ast, actual_ast)


def test_function_calls():
    parser = testing_utils.parser(f"(func: 0) <- ();")
    actual_ast = parser.parse()
    expected_ast = [
        o.InfixExpression(
            1,
            o.Function(1, [], o.Number(1, 0.0)),
            Token(1, "<-", t.SEND),
            o.List(1, [])
        )
    ]
    assert_expressions_equal(expected_ast, actual_ast)


@pytest.mark.parametrize("switch_expression, case_expressions", [
    (o.Boolean(1, True), [
        (
            "1 == 1: true",
            o.InfixExpression(2, o.Number(2, 1), Token(2, "==", t.EQ), o.Number(2, 1)),
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
            o.InfixExpression(2, o.Identifier(2, "a"), Token(2, "==", t.EQ), o.Number(2, 1)),
            o.String(2, "1")
        ),
        (
            "a == 2: \"2\"",
            o.InfixExpression(3, o.Identifier(3, "a"), Token(3, "==", t.EQ), o.Number(3, 2)),
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
            o.InfixExpression(2, o.Identifier(2, "a"), Token(2, "==", t.EQ), o.Number(2, 1)),
            o.String(2, "1")
        ),
        (
            "a == 2: \"2\"",
            o.InfixExpression(3, o.Identifier(3, "a"), Token(3, "==", t.EQ), o.Number(3, 2)),
            o.String(3, "2")
        ),
        (
            "a == 3: \"3\"",
            o.InfixExpression(4, o.Identifier(4, "a"), Token(4, "==", t.EQ), o.Number(4, 3)),
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
def test_when(switch_expression, case_expressions):
    source, expected_when_ast = create_when(1, switch_expression, case_expressions)
    source = f"{source};"

    p = testing_utils.parser(source)
    actual_ast = p.parse()

    expected_ast = [expected_when_ast]

    assert_expressions_equal(expected_ast, actual_ast)


def test_for_loop():
    source = "for i in (1, 2, 3): i + 1;"

    expected_for_object = o.ForLoop(
        1,
        "i",
        o.List(1, [o.Number(1, 1), o.Number(1, 2), o.Number(1, 3)]),
        o.Boolean(1, True),
        o.InfixExpression(
            1,
            o.Identifier(1, "i"),
            Token(1, "+", t.PLUS),
            o.Number(1, 1)
        )
    )

    p = testing_utils.parser(source)
    actual_for_ast = p.parse()
    assert_expressions_equal([expected_for_object], actual_for_ast)


def test_for_loop_conditional():
    source = "for i in (1, 2, 3) if i > 2: i;"

    expected_for_object = o.ForLoop(
        1,
        "i",
        o.List(1, [o.Number(1, 1), o.Number(1, 2), o.Number(1, 3)]),
        o.InfixExpression(
            1,
            o.Identifier(1, "i"),
            Token(1, ">", t.GT),
            o.Number(1, 2)
        ),
        o.Identifier(1, "i")
    )

    p = testing_utils.parser(source)
    actual_for_ast = p.parse()
    assert_expressions_equal([expected_for_object], actual_for_ast)