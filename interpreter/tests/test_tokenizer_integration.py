import pytest
from interpreter.tokens.tokens import *
from interpreter.tokens.tokenizer import Tokenizer, Token


@pytest.mark.parametrize("symbol, type_", [
    (";", SEMICOLON),
    ("<-", POINTER),
    (",", COMMA),
    ("(", OPEN_PAREN),
    (")", CLOSED_PAREN),
    ("+", PLUS),
    ("-", MINUS),
    ("*", MULTIPLY),
    ("/", DIVIDE),
    ("=", ASSIGN),
    ("==", EQ),
    ("!=", NE),
    (">", GT),
    (">=", GE),
    ("<", LT),
    ("<=", LE),
    ("!", BANG),
    ("&", AND),
    ("|", OR),
    (":", COLON),
    ("--", DEC),
    ("++", INC)
])
def test_symbols(symbol, type_):
    """Test symbols

    Symbols that are not stand-alone tokens:
    - PERIOD (indicates floating-point value in numbers)
    - DOUBLE_QUOTE (indicates start and end of strings)
    """
    actual_tokens = get_tokens(symbol)
    assert actual_tokens == [Token(symbol, type_, 1), Token("", EOF, 1)]


@pytest.mark.parametrize("keyword, type_", [
    ("true", BOOLEAN),
    ("false", BOOLEAN),
    ("func", FUNCTION),
    ("when", WHEN),
    ("is", IS),
    ("else", ELSE)
])
def test_keywords(keyword, type_):
    """Test symbols

    Symbols that are not stand-alone tokens:
    - PERIOD (indicates floating-point value in numbers)
    - DOUBLE_QUOTE (indicates start and end of strings)
    """
    actual_tokens = get_tokens(keyword)
    assert actual_tokens == [Token(keyword, type_, 1), Token("", EOF, 1)]


@pytest.mark.parametrize("source,expected_token", [
    ("\"hello, world!\"", Token("hello, world!", STRING, 1)),
    ("1", Token("1", NUMBER, 1)),
    ("15", Token("15", NUMBER, 1)),
    ("153", Token("153", NUMBER, 1)),
    ("1.5", Token("1.5", NUMBER, 1)),
    ("true", Token("true", BOOLEAN, 1)),
    ("false", Token("false", BOOLEAN, 1))
])
def test_data_types(source, expected_token):
    actual_tokens = get_tokens(source)
    assert actual_tokens == [expected_token, Token("", EOF, 1)]


@pytest.mark.parametrize("source, expected_tokens", [
    ("1 + 1;", [
        Token("1", NUMBER, 1),
        Token("+", PLUS, 1),
        Token("1", NUMBER, 1),
        Token(";", SEMICOLON, 1),
        Token("", EOF, 1)
    ]),
    ("a = 1;\nb = 2;", [
        Token("a", IDENTIFIER, 1),
        Token("=", ASSIGN, 1),
        Token("1", NUMBER, 1),
        Token(";", SEMICOLON, 1),
        Token("b", IDENTIFIER, 2),
        Token("=", ASSIGN, 2),
        Token("2", NUMBER, 2),
        Token(";", SEMICOLON, 2),
        Token("", EOF, 2)
    ]),
    ("a = (1, 2, 3, 4);", [
        Token("a", IDENTIFIER, 1),
        Token("=", ASSIGN, 1),
        Token("(", OPEN_PAREN, 1),
        Token("1", NUMBER, 1),
        Token(",", COMMA, 1),
        Token("2", NUMBER, 1),
        Token(",", COMMA, 1),
        Token("3", NUMBER, 1),
        Token(",", COMMA, 1),
        Token("4", NUMBER, 1),
        Token(")", CLOSED_PAREN, 1),
        Token(";", SEMICOLON, 1),
        Token("", EOF, 1)
    ])
])
def test_tokenizer(source, expected_tokens):
    actual_tokens = get_tokens(source)
    assert actual_tokens == expected_tokens


def test_skip_comments():
    source = """
    # this is a comment
    a = 1;
    """
    actual_tokens = get_tokens(source)
    assert actual_tokens == [
        Token("a", IDENTIFIER, 3),
        Token("=", ASSIGN, 3),
        Token("1", NUMBER, 3),
        Token(";", SEMICOLON, 3),
        Token("", EOF, 4)
    ]


def get_tokens(source: str) -> list[Token]:
    return [t for t in Tokenizer(source)]
