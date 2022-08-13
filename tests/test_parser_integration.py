import pytest
from tokens.tokens import *
from _parser import _parser
from .testing_utils import TestToken


def test_precedence_add():

    tokens = [
        TestToken("1", INTEGER, 1),
        TestToken("+", PLUS, 1),
        TestToken("1", INTEGER, 1),
        TestToken(";", SEMICOLON, 1),
        TestToken("", EOF, 1)
    ]

    expected_ast = [
        _parser.ExpressionStatement(
            _parser.BinaryOperation(
                _parser.Integer(TestToken("1", INTEGER, 1)),
                TestToken("+", PLUS, 1),
                _parser.Integer(TestToken("1", INTEGER, 1))
            )
        )
    ]

    actual_ast = _parser.Parser(tokens).parse()
    assert actual_ast == expected_ast


def test_precedence_multiply():
    tokens = [
        TestToken("1", INTEGER, 1),
        TestToken("+", PLUS, 1),
        TestToken("2", INTEGER, 1),
        TestToken("*", MULTIPLY, 1),
        TestToken("4", INTEGER, 1),
        TestToken(";", SEMICOLON, 1),
        TestToken("", EOF, 1)
    ]

    expected_ast = [
        _parser.ExpressionStatement(
            _parser.BinaryOperation(
                _parser.Integer(TestToken("1", INTEGER, 1)),
                TestToken("+", PLUS, 1),
                _parser.BinaryOperation(
                    _parser.Integer(TestToken("2", INTEGER, 1)),
                    TestToken("*", MULTIPLY, 1),
                    _parser.Integer(TestToken("4", INTEGER, 1))
                )
            )
        )
    ]

    actual_ast = _parser.Parser(tokens).parse()
    assert actual_ast == expected_ast


precedence_and_or_tests = [
    ("AND", TestToken("&&", AND, 1)),
    ("OR",  TestToken("||", OR, 1))
]


@pytest.mark.parametrize("test_name,operator_token", precedence_and_or_tests)
def test_precedence_and_or(test_name, operator_token):
    tokens = [
        TestToken("1", INTEGER, 1),
        TestToken("==", EQ, 1),
        TestToken("1", INTEGER, 1),
        operator_token,
        TestToken("2", INTEGER, 1),
        TestToken("!=", NE, 1),
        TestToken("3", INTEGER, 1),
        TestToken(";", SEMICOLON, 1),
        TestToken("", EOF, 1)
    ]

    expected_ast = [
        _parser.ExpressionStatement(
            _parser.BinaryOperation(
                _parser.BinaryOperation(
                    _parser.Integer(TestToken("1", INTEGER, 1)),
                    TestToken("==", EQ, 1),
                    _parser.Integer(TestToken("1", INTEGER, 1))
                ),
                operator_token,
                _parser.BinaryOperation(
                    _parser.Integer(TestToken("2", INTEGER, 1)),
                    TestToken("!=", NE, 1),
                    _parser.Integer(TestToken("3", INTEGER, 1)),
                )
            )
        )
    ]

    actual_ast = _parser.Parser(tokens).parse()
    assert actual_ast == expected_ast


def test_dictionary():
    # source: dict["a"];
    tokens = [
        TestToken("dict", IDENTIFIER, 1),
        TestToken("[", OPEN_BRACKET, 1),
        TestToken("a", STRING, 1),
        TestToken("]", CLOSED_BRACKET, 1),
        TestToken(";", SEMICOLON, 1),
        TestToken("", EOF, 1),
    ]

    expected_ast = [
        _parser.ExpressionStatement(
            _parser.Index(
                _parser.Identifier(TestToken("dict", IDENTIFIER, 1)),
                [_parser.String(TestToken("a", STRING, 1))]
            )
        )
    ]

    actual_ast = _parser.Parser(tokens).parse()
    assert actual_ast == expected_ast
