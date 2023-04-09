import pytest

from interpreter.tokens.tokens import *
from interpreter.tokens.tokenizer import Token
from ..parser_ import parser_
from . import testing_utils
from ..parser_.ast_objects import BuiltinFunction, Boolean, Number, List, Identifier, BinaryExpression, UnaryExpression

boolean_values = [
    ("true", Boolean(1, True)),
    ("false", Boolean(1, False))
]


@pytest.mark.parametrize("source, expected_value", boolean_values)
def test_boolean(source, expected_value):
    expected_ast = [
        expected_value
    ]

    parser = testing_utils.parser(f"{source};")
    actual_ast = parser.parse()
    assert actual_ast == expected_ast


list_values = [
    ("()", []),
    ("(1,)", [Number(1, 1)]),
    ("(1, 2)", [Number(1, 1), Number(1, 2)]),
    ("(1, 2, 3)", [Number(1, 1), Number(1, 2), Number(1, 3)])
]


@pytest.mark.parametrize("source, expected_list_values", list_values)
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


unary_expressions = [
    ("+1", Token("+", PLUS, 1), Number(1, 1)),
    ("-1", Token("-", MINUS, 1), Number(1, 1)),
    ("!true", Token("!", BANG, 1), Boolean(1, True))
]


@pytest.mark.parametrize("source, operator, expression", unary_expressions)
def test_unary_expressions(source, operator, expression):
    expected_ast = [
        UnaryExpression(1, operator, expression)
    ]

    parser = testing_utils.parser(f"{source};")
    actual_ast = parser.parse()
    assert actual_ast == expected_ast


binary_expressions = [
    ("1+1", Number(1, 1), Token("+", PLUS, 1), Number(1, 1)),
    ("1-1", Number(1, 1), Token("-", MINUS, 1), Number(1, 1)),
    ("1*1", Number(1, 1), Token("*", MULTIPLY, 1), Number(1, 1)),
    ("1/1", Number(1, 1), Token("/", DIVIDE, 1), Number(1, 1)),
    ("a <- (1,)", Identifier(1, "a"), Token("<-", POINTER, 1), List(1, [Number(1, 1)])),
    ("true == false", Boolean(1, True), Token("==", EQ, 1), Boolean(1, False)),
    ("false != true", Boolean(1, False), Token("!=", NE, 1), Boolean(1, True)),
    ("false & false", Boolean(1, False), Token("&", AND, 1), Boolean(1, False)),
    ("true | true", Boolean(1, True), Token("|", OR, 1), Boolean(1, True)),
    ("5 > 3", Number(1, 5), Token(">", GT, 1), Number(1, 3)),
    ("4 >= 2", Number(1, 4), Token(">=", GE, 1), Number(1, 2)),
    ("6 < 12", Number(1, 6), Token("<", LT, 1), Number(1, 12)),
    ("7 <= 13", Number(1, 7), Token("<=", LE, 1), Number(1, 13)),
]


@pytest.mark.parametrize("source, left, operator, right", binary_expressions)
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
            Token("+", PLUS, 1),
            BinaryExpression(
                1,
                Number(1, 2),
                Token("*", MULTIPLY, 1),
                Number(1, 4)
            )
        )
    ]

    parser = testing_utils.parser("1+2*4;")
    actual_ast = parser.parse()
    assert actual_ast == expected_ast


builtin_function_names = [
    ("print", BuiltinFunction(1, "print"))
]


@pytest.mark.parametrize("name, ast_object", builtin_function_names)
def test_builtin_functions(name, ast_object):
    parser = testing_utils.parser(f"{name};")
    actual_ast = parser.parse()
    assert actual_ast == [ast_object]
