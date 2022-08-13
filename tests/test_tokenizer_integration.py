import pytest
from tokens.tokens import *
from tokens.tokenizer import Tokenizer
from .testing_utils import TestToken

data_types_tests = [
    ("\"hello, world!\"", [
        TestToken("hello, world!", STRING, 1),
        TestToken("", EOF, 1),
    ]),
    ("true", [
        TestToken("true", BOOLEAN, 1),
        TestToken("", EOF, 1),
    ]),
    ("false", [
        TestToken("false", BOOLEAN, 1),
        TestToken("", EOF, 1),
    ]),
    ("1", [
        TestToken("1", INTEGER, 1),
        TestToken("", EOF, 1),
    ]),
    ("15", [
        TestToken("15", INTEGER, 1),
        TestToken("", EOF, 1),
    ]),
    ("153", [
        TestToken("153", INTEGER, 1),
        TestToken("", EOF, 1),
    ]),
    ("1.5", [
        TestToken("1.5", FLOAT, 1),
        TestToken("", EOF, 1),
    ]),
]


@pytest.mark.parametrize("source,expected_tokens", data_types_tests)
def test_data_types(source, expected_tokens):
    actual_tokens = Tokenizer(source).tokenize()
    assert actual_tokens == expected_tokens


tokenizer_tests = [
    ("1 + 1;", [
        TestToken("1", INTEGER, 1),
        TestToken("+", PLUS, 1),
        TestToken("1", INTEGER, 1),
        TestToken(";", SEMICOLON, 1),
        TestToken("", EOF, 1)
    ]),
    ("a = 1;\nb = 2;", [
        TestToken("a", IDENTIFIER, 1),
        TestToken("=", ASSIGN, 1),
        TestToken("1", INTEGER, 1),
        TestToken(";", SEMICOLON, 1),
        TestToken("b", IDENTIFIER, 2),
        TestToken("=", ASSIGN, 2),
        TestToken("2", INTEGER, 2),
        TestToken(";", SEMICOLON, 2),
        TestToken("", EOF, 2),
    ]),
    ("# a = 1;\nb = 2;", [
        TestToken("b", IDENTIFIER, 2),
        TestToken("=", ASSIGN, 2),
        TestToken("2", INTEGER, 2),
        TestToken(";", SEMICOLON, 2),
        TestToken("", EOF, 2),
    ]),
    ("\n/*x = 1;\nb = 2; */\nc = 3;", [
        TestToken("c", IDENTIFIER, 4),
        TestToken("=", ASSIGN, 4),
        TestToken("3", INTEGER, 4),
        TestToken(";", SEMICOLON, 4),
        TestToken("", EOF, 4),
    ]),
    ("/*func is_eq(a, b) {\n    return a == b;\n};\n*/print(1 / 1);", [
        TestToken("print", IDENTIFIER, 4),
        TestToken("(", OPEN_PAREN, 4),
        TestToken("1", INTEGER, 4),
        TestToken("/", DIVIDE, 4),
        TestToken("1", INTEGER, 4),
        TestToken(")", CLOSED_PAREN, 4),
        TestToken(";", SEMICOLON, 4),
        TestToken("", EOF, 4),
    ]),
    ("i += 3; j -= 4;\nk *= 5; l /= 6;", [
        TestToken("i", IDENTIFIER, 1),
        TestToken("+=", ASSIGN_ADD, 1),
        TestToken("3", INTEGER, 1),
        TestToken(";", SEMICOLON, 1),
        TestToken("j", IDENTIFIER, 1),
        TestToken("-=", ASSIGN_SUB, 1),
        TestToken("4", INTEGER, 1),
        TestToken(";", SEMICOLON, 1),
        TestToken("k", IDENTIFIER, 2),
        TestToken("*=", ASSIGN_MUL, 2),
        TestToken("5", INTEGER, 2),
        TestToken(";", SEMICOLON, 2),
        TestToken("l", IDENTIFIER, 2),
        TestToken("/=", ASSIGN_DIV, 2),
        TestToken("6", INTEGER, 2),
        TestToken(";", SEMICOLON, 2),
        TestToken("", EOF, 2),
    ])
]


@pytest.mark.parametrize("source, expected_tokens", tokenizer_tests)
def test_tokenizer(source, expected_tokens):
    actual_tokens = Tokenizer(source).tokenize()
    assert actual_tokens == expected_tokens
