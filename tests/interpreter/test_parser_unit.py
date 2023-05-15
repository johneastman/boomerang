import pytest

import tests.testing_utils as testing_utils
from tests.testing_utils import create_when, assert_expression_equal
import interpreter.parser_.ast_objects as o
from interpreter.tokens.tokenizer import Token
import interpreter.tokens.tokens as t
from utils.utils import LanguageRuntimeException


def test_current_peek_advance():
    p = testing_utils.parser("i = 1;")

    assert p.current == Token(1, "i", t.IDENTIFIER)
    assert p.peek == Token(1, "=", t.ASSIGN)

    p.advance()

    assert p.current == Token(1, "=", t.ASSIGN)
    assert p.peek == Token(1, "1", t.NUMBER)

    p.advance()

    assert p.current == Token(1, "1", t.NUMBER)
    assert p.peek == Token(1, ";", t.SEMICOLON)

    p.advance()

    assert p.current == Token(1, ";", t.SEMICOLON)
    assert p.peek == Token(1, "", t.EOF)

    p.advance()

    assert p.current == Token(1, "", t.EOF)

    with pytest.raises(LanguageRuntimeException) as e:
        p.peek
    assert str(e.value) == "Error at line 1: unexpected end of file"


@pytest.mark.parametrize("name, level", [
    ("LOWEST", 0),
    ("BOOLEAN", 1),
    ("COMPARE", 2),
    ("INDEX", 3),
    ("SEND", 4),
    ("SUM", 5),
    ("PRODUCT", 6),
    ("POWER", 7),
    ("PREFIX", 8),
    ("POSTFIX", 9)
])
def test_get_precedence_level_by_name(name, level):
    p = testing_utils.parser("")
    assert p.get_precedence_level_by_name(name) == level


@pytest.mark.parametrize("symbol, precedence_level", [
    ("1", 0),
    ("1.43", 0),
    ("\"hello!\"", 0),
    ("true", 0),
    ("false", 0),
    ("or", 1),
    ("and", 1),
    ("xor", 1),
    ("in", 1),
    ("==", 2),
    ("!=", 2),
    (">=", 2),
    ("<=", 2),
    (">", 2),
    ("<", 2),
    ("@", 3),
    ("<-", 4),
    ("-", 5),
    ("+", 5),
    ("*", 6),
    ("%", 6),
    ("/", 6),
    ("**", 7),
    ("not", 8),
    ("!", 8),
    ("++", 9),
    ("--", 9),
])
def test_get_current_precedence_level(symbol, precedence_level):
    p = testing_utils.parser(symbol)
    assert p.get_current_precedence_level() == precedence_level


@pytest.mark.parametrize("source, expected_result", [
    ("()", o.List(1, [])),
    ("(1 + 1)", o.InfixExpression(1, o.Number(1, 1), Token(1, "+", t.PLUS), o.Number(1, 1))),
    ("(1, 2)", o.List(1, [o.Number(1, 1), o.Number(1, 2)])),
])
def test_grouped_expressions(source, expected_result):
    p = testing_utils.parser(source)
    actual_result = p.parse_grouped_expression()
    assert_expression_equal(expected_result, actual_result)


def test_grouped_expressions_errors():
    p = testing_utils.parser("(2")
    with pytest.raises(LanguageRuntimeException) as e:
        p.parse_grouped_expression()
    assert str(e.value) == "Error at line 1: expected CLOSED_PAREN, got EOF ('')"


@pytest.mark.parametrize("source, token", [
    ("--", Token(1, "--", t.DEC)),
    ("++", Token(1, "++", t.INC))
])
def test_parse_prefix_invalid_operators(source, token):
    p = testing_utils.parser(source)
    with pytest.raises(LanguageRuntimeException) as e:
        p.parse_prefix()
    assert str(e.value) == f"Error at line 1: invalid prefix operator: {token.type} ('{token.value}')"


@pytest.mark.parametrize("source, expected_result", [
    # built-in functions
    ("print", o.BuiltinFunction(1, "print")),
    ("randint", o.BuiltinFunction(1, "randint")),
    ("randfloat", o.BuiltinFunction(1, "randfloat")),
    ("len", o.BuiltinFunction(1, "len")),
    ("range", o.BuiltinFunction(1, "range")),
    ("round", o.BuiltinFunction(1, "round")),

    # regular identifiers
    ("i", o.Identifier(1, "i")),
    ("variable", o.Identifier(1, "variable")),
])
def test_parse_identifier(source, expected_result):
    p = testing_utils.parser(source)
    actual_result = p.parse_identifier()
    assert_expression_equal(expected_result, actual_result)


def test_assign_expression():
    p = testing_utils.parser("variable = 1;")
    actual_assign_ast = p.parse_assign()

    expected_assign_ast = o.Assignment(
        1,
        "variable",
        o.Number(1, 1)
    )

    assert_expression_equal(expected_assign_ast, actual_assign_ast)


@pytest.mark.parametrize("source, error", [
    ("1;", "Error at line 1: expected IDENTIFIER, got NUMBER ('1')"),
    ("variable 1;", "Error at line 1: expected ASSIGN, got NUMBER ('1')")
])
def test_assign_errors(source, error):
    p = testing_utils.parser(source)
    with pytest.raises(LanguageRuntimeException) as e:
        p.parse_assign()
    assert str(e.value) == error


@pytest.mark.parametrize("source, expected_result", [
    (")", o.List(1, [o.Number(1, 1)])),
    ("2)", o.List(1, [o.Number(1, 1), o.Number(1, 2)])),
    ("2, 3)", o.List(1, [o.Number(1, 1), o.Number(1, 2), o.Number(1, 3)])),
])
def test_parse_list(source, expected_result):
    p = testing_utils.parser(f"{source};")
    actual_result = p.parse_list(o.Number(1, 1))
    assert_expression_equal(expected_result, actual_result)


def test_parse_list_errors():
    source = "2 3)"
    p = testing_utils.parser(source)
    with pytest.raises(LanguageRuntimeException) as e:
        p.parse_list(o.Number(1, 1))
    assert str(e.value) == "Error at line 1: expected COMMA, got NUMBER ('3')"


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


@pytest.mark.parametrize("source, error", [
    ("func", "Error at line 1: expected IDENTIFIER, got EOF ('')"),
    ("func a", "Error at line 1: expected COMMA, got EOF ('')"),
    ("func a,", "Error at line 1: expected IDENTIFIER, got EOF ('')"),
    ("func:", "Error at line 1: invalid prefix operator: EOF ('')"),
    ("func:;", "Error at line 1: invalid prefix operator: SEMICOLON (';')"),
])
def test_parse_function_errors(source, error):
    p = testing_utils.parser(source)
    with pytest.raises(LanguageRuntimeException) as e:
        p.parse_function()
    assert str(e.value) == error


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
            "a == 3: \"3\"", o.InfixExpression(4, o.Identifier(4, "a"), Token(4, "==", t.EQ), o.Number(4, 3)),
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


@pytest.mark.parametrize("source, error", [
    ("when", "Error at line 1: invalid prefix operator: EOF ('')"),
    ("when:", "Error at line 1: invalid prefix operator: EOF ('')"),
    ("when: true", "Error at line 1: expected COLON, got EOF ('')"),
    ("when: true:", "Error at line 1: invalid prefix operator: EOF ('')"),
    ("when a:", "Error at line 1: expected IS, got EOF ('')"),
    ("when a: is 1", "Error at line 1: expected COLON, got EOF ('')"),
    ("when a: is 1:", "Error at line 1: invalid prefix operator: EOF ('')"),
    ("when a: is 1: 1 else", "Error at line 1: expected COLON, got EOF ('')"),
    ("when a: is 1: 1 else:", "Error at line 1: invalid prefix operator: EOF ('')"),
])
def test_when_errors(source, error):
    p = testing_utils.parser(source)
    with pytest.raises(LanguageRuntimeException) as e:
        p.parse_when()

    assert str(e.value) == error


def test_for_loop():
    source = "for i in (1, 2, 3): i + 1;"

    expected_for_object = o.ForLoop(
        1,
        "i",
        o.List(1, [o.Number(1, 1), o.Number(1, 2), o.Number(1, 3)]),
        o.InfixExpression(
            1,
            o.Identifier(1, "i"),
            Token(1, "+", t.PLUS),
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
def test_for_loop_errors(source, error_message):
    p = testing_utils.parser(source)

    with pytest.raises(LanguageRuntimeException) as e:
        p.parse_for()

    assert str(e.value) == error_message
