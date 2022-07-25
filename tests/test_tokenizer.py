import pytest
import tests.testing_utils as utils
from tokens.tokens import *
from tokens.tokenizer import Token, Tokenizer

data_types_tests = [
    ("\"hello, world!\"", [
        Token("hello, world!", STRING, 1),
        Token("", EOF, 1),
    ]),
    ("true", [
        Token("true", BOOLEAN, 1),
        Token("", EOF, 1),
    ]),
    ("false", [
        Token("false", BOOLEAN, 1),
        Token("", EOF, 1),
    ]),
    ("1", [
        Token("1", INTEGER, 1),
        Token("", EOF, 1),
    ]),
    ("15", [
        Token("15", INTEGER, 1),
        Token("", EOF, 1),
    ]),
    ("153", [
        Token("153", INTEGER, 1),
        Token("", EOF, 1),
    ]),
    ("1.5", [
        Token("1.5", FLOAT, 1),
        Token("", EOF, 1),
    ]),
]


@pytest.mark.parametrize("source,expected_tokens", data_types_tests)
def test_data_types(source, expected_tokens):
    actual_tokens = Tokenizer(source).tokenize()
    utils.assert_tokens_equal(expected_tokens, actual_tokens)


tokenizer_tests = [
    ("1 + 1;", [
        Token("1", INTEGER, 1),
        Token("+", PLUS, 1),
        Token("1", INTEGER, 1),
        Token(";", SEMICOLON, 1),
        Token("", EOF, 1)
    ]),
    ("a = 1;\nb = 2;", [
        Token("a", IDENTIFIER, 1),
        Token("=", ASSIGN, 1),
        Token("1", INTEGER, 1),
        Token(";", SEMICOLON, 1),
        Token("b", IDENTIFIER, 2),
        Token("=", ASSIGN, 2),
        Token("2", INTEGER, 2),
        Token(";", SEMICOLON, 2),
        Token("", EOF, 2),
    ]),
    ("# a = 1;\nb = 2;", [
        Token("b", IDENTIFIER, 2),
        Token("=", ASSIGN, 2),
        Token("2", INTEGER, 2),
        Token(";", SEMICOLON, 2),
        Token("", EOF, 2),
    ]),
    ("\n/*x = 1;\nb = 2; */\nc = 3;", [
        Token("c", IDENTIFIER, 4),
        Token("=", ASSIGN, 4),
        Token("3", INTEGER, 4),
        Token(";", SEMICOLON, 4),
        Token("", EOF, 4),
    ]),
    ("/*func is_eq(a, b) {\n    return a == b;\n};\n*/print(1 / 1);", [
        Token("print", IDENTIFIER, 4),
        Token("(", OPEN_PAREN, 4),
        Token("1", INTEGER, 4),
        Token("/", DIVIDE, 4),
        Token("1", INTEGER, 4),
        Token(")", CLOSED_PAREN, 4),
        Token(";", SEMICOLON, 4),
        Token("", EOF, 4),
    ]),
    ("i += 3; j -= 4;\nk *= 5; l /= 6;", [
        Token("i", IDENTIFIER, 1),
        Token("+=", ASSIGN_ADD, 1),
        Token("3", INTEGER, 1),
        Token(";", SEMICOLON, 1),
        Token("j", IDENTIFIER, 1),
        Token("-=", ASSIGN_SUB, 1),
        Token("4", INTEGER, 1),
        Token(";", SEMICOLON, 1),
        Token("k", IDENTIFIER, 2),
        Token("*=", ASSIGN_MUL, 2),
        Token("5", INTEGER, 2),
        Token(";", SEMICOLON, 2),
        Token("l", IDENTIFIER, 2),
        Token("/=", ASSIGN_DIV, 2),
        Token("6", INTEGER, 2),
        Token(";", SEMICOLON, 2),
        Token("", EOF, 2),
    ])
]


@pytest.mark.parametrize("source, expected_tokens", tokenizer_tests)
def test_tokenizer(source, expected_tokens):
    actual_tokens = Tokenizer(source).tokenize()
    utils.assert_tokens_equal(expected_tokens, actual_tokens)
