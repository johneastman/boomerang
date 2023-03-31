import pytest
from tokens.tokens import *
from tokens.tokenizer import Token
from _parser import _parser
from . import testing_utils


def test_precedence_add():

    expected_ast = [
        _parser.ExpressionStatement(
            _parser.BinaryOperation(
                _parser.Integer(1, 1),
                Token("+", PLUS, 1),
                _parser.Integer(1, 1)
            )
        )
    ]

    parser = testing_utils.parser("1+1;")
    actual_ast = parser.parse()
    assert actual_ast == expected_ast


def test_precedence_multiply():
    expected_ast = [
        _parser.ExpressionStatement(
            _parser.BinaryOperation(
                _parser.Integer(1, 1),
                Token("+", PLUS, 1),
                _parser.BinaryOperation(
                    _parser.Integer(2, 1),
                    Token("*", MULTIPLY, 1),
                    _parser.Integer(4, 1)
                )
            )
        )
    ]

    parser = testing_utils.parser("1+2*4;")
    actual_ast = parser.parse()
    assert actual_ast == expected_ast


precedence_and_or_tests = [
    ("AND", Token("&&", AND, 1)),
    ("OR",  Token("||", OR, 1))
]


@pytest.mark.parametrize("test_name,operator_token", precedence_and_or_tests)
def test_precedence_and_or(test_name, operator_token):

    parser = testing_utils.parser(f"1 == 1 {operator_token.value} 2 != 3;")

    expected_ast = [
        _parser.ExpressionStatement(
            _parser.BinaryOperation(
                _parser.BinaryOperation(
                    _parser.Integer(1, 1),
                    Token("==", EQ, 1),
                    _parser.Integer(1, 1)
                ),
                operator_token,
                _parser.BinaryOperation(
                    _parser.Integer(2, 1),
                    Token("!=", NE, 1),
                    _parser.Integer(3, 1)
                ),
            )
        )
    ]

    actual_ast = parser.parse()
    assert actual_ast == expected_ast
