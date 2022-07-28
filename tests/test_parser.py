import pytest
from tokens.tokens import *
from tokens.tokenizer import Token
from _parser import _parser


def test_precedence_add():

    tokens = [
        Token("1", INTEGER, 1),
        Token("+", PLUS, 1),
        Token("1", INTEGER, 1),
        Token(";", SEMICOLON, 1),
        Token("", EOF, 1)
    ]

    expected_ast = [
        _parser.ExpressionStatement(
            _parser.BinaryOperation(
                _parser.Integer(Token("1", INTEGER, 1)),
                Token("+", PLUS, 1),
                _parser.Integer(Token("1", INTEGER, 1))
            )
        )
    ]

    actual_ast = _parser.Parser(tokens).parse()
    assert expected_ast == actual_ast


def test_precedence_multiply():
    tokens = [
        Token("1", INTEGER, 1),
        Token("+", PLUS, 1),
        Token("2", INTEGER, 1),
        Token("*", MULTIPLY, 1),
        Token("4", INTEGER, 1),
        Token(";", SEMICOLON, 1),
        Token("", EOF, 1)
    ]

    expected_ast = [
        _parser.ExpressionStatement(
            _parser.BinaryOperation(
                _parser.Integer(Token("1", INTEGER, 1)),
                Token("+", PLUS, 1),
                _parser.BinaryOperation(
                    _parser.Integer(Token("2", INTEGER, 1)),
                    Token("*", MULTIPLY, 1),
                    _parser.Integer(Token("4", INTEGER, 1))
                )
            )
        )
    ]

    actual_ast = _parser.Parser(tokens).parse()
    assert expected_ast == actual_ast


precedence_and_or_tests = [
    ("AND", Token("&&", AND, 1)),
    ("OR",  Token("||", OR, 1))
]


@pytest.mark.parametrize("test_name,operator_token", precedence_and_or_tests)
def test_precedence_and_or(test_name, operator_token):
    tokens = [
        Token("1", INTEGER, 1),
        Token("==", EQ, 1),
        Token("1", INTEGER, 1),
        operator_token,
        Token("2", INTEGER, 1),
        Token("!=", NE, 1),
        Token("3", INTEGER, 1),
        Token(";", SEMICOLON, 1),
        Token("", EOF, 1)
    ]

    expected_ast = [
        _parser.ExpressionStatement(
            _parser.BinaryOperation(
                _parser.BinaryOperation(
                    _parser.Integer(Token("1", INTEGER, 1)),
                    Token("==", EQ, 1),
                    _parser.Integer(Token("1", INTEGER, 1))
                ),
                operator_token,
                _parser.BinaryOperation(
                    _parser.Integer(Token("2", INTEGER, 1)),
                    Token("!=", NE, 1),
                    _parser.Integer(Token("3", INTEGER, 1)),
                )
            )
        )
    ]

    actual_ast = _parser.Parser(tokens).parse()
    assert expected_ast == actual_ast


def test_dictionary():
    # source: dict["a"];
    tokens = [
        Token("dict", IDENTIFIER, 1),
        Token("[", OPEN_BRACKET, 1),
        Token("a", STRING, 1),
        Token("]", CLOSED_BRACKET, 1),
        Token(";", SEMICOLON, 1),
        Token("", EOF, 1),
    ]

    expected_ast = [
        _parser.ExpressionStatement(
            _parser.Index(
                _parser.Identifier(Token("dict", IDENTIFIER, 1)),
                _parser.String(Token("a", STRING, 1))
            )
        )
    ]

    actual_ast = _parser.Parser(tokens).parse()
    assert expected_ast == actual_ast
