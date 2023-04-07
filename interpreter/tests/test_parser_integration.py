from interpreter.tokens.tokens import *
from interpreter.tokens.tokenizer import Token
from .._parser import _parser
from . import testing_utils


def test_precedence_add():

    expected_ast = [
        _parser.create_binary_expression(
            _parser.create_number("1", 1),
            Token("+", PLUS, 1),
            _parser.create_number("1", 1)
        )
    ]

    parser = testing_utils.parser("1+1;")
    actual_ast = parser.parse()
    assert actual_ast == expected_ast


def test_precedence_multiply():
    expected_ast = [
        _parser.create_binary_expression(
            _parser.create_number("1", 1),
            Token("+", PLUS, 1),
            _parser.create_binary_expression(
                _parser.create_number("2", 1),
                Token("*", MULTIPLY, 1),
                _parser.create_number("4", 1)
            )
        )
    ]

    parser = testing_utils.parser("1+2*4;")
    actual_ast = parser.parse()
    assert actual_ast == expected_ast
