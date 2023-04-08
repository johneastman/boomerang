import pytest

from interpreter.tokens.tokens import *
from interpreter.tokens.tokenizer import Token
from .._parser import _parser
from . import testing_utils


boolean_values = [
    ("true", _parser.Boolean(1, True)),
    ("false", _parser.Boolean(1, False))
]


@pytest.mark.parametrize("source, expected_value", boolean_values)
def test_boolean(source, expected_value):
    expected_ast = [
        expected_value
    ]

    parser = testing_utils.parser(f"{source};")
    actual_ast = parser.parse()
    assert actual_ast == expected_ast


def test_precedence_add():
    expected_ast = [
        _parser.BinaryExpression(
            1,
            _parser.Number(1, 1),
            Token("+", PLUS, 1),
            _parser.Number(1, 1)
        )
    ]

    parser = testing_utils.parser("1+1;")
    actual_ast = parser.parse()
    assert actual_ast == expected_ast


def test_precedence_multiply():
    expected_ast = [
        _parser.BinaryExpression(
            1,
            _parser.Number(1, 1),
            Token("+", PLUS, 1),
            _parser.BinaryExpression(
                1,
                _parser.Number(1, 2),
                Token("*", MULTIPLY, 1),
                _parser.Number(1, 4)
            )
        )
    ]

    parser = testing_utils.parser("1+2*4;")
    actual_ast = parser.parse()
    assert actual_ast == expected_ast


list_values = [
    ("()", []),
    ("(1,)", [_parser.Number(1, 1)]),
    ("(1, 2)", [_parser.Number(1, 1), _parser.Number(1, 2)]),
    ("(1, 2, 3)", [_parser.Number(1, 1), _parser.Number(1, 2), _parser.Number(1, 3)])
]


@pytest.mark.parametrize("source, expected_list_values", list_values)
def test_list(source, expected_list_values):
    expected_ast = [
        _parser.List(
            1,
            expected_list_values
        )
    ]

    parser = testing_utils.parser(f"{source};")
    actual_ast = parser.parse()
    assert actual_ast == expected_ast
