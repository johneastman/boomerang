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
    ("++", INC),
    ("%", MOD)
])
def test_symbols(symbol, type_):
    """Test symbols

    Symbols that are not stand-alone tokens:
    - PERIOD (indicates floating-point value in numbers)
    - DOUBLE_QUOTE (indicates start and end of strings)
    """
    actual_tokens = get_tokens(symbol)
    assert actual_tokens == [Token(1, symbol, type_), Token(1, "", EOF)]


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
    assert actual_tokens == [Token(1, keyword, type_), Token(1, "", EOF)]


@pytest.mark.parametrize("source,expected_token", [
    ("\"hello, world!\"", Token(1, "hello, world!", STRING)),
    ("1", Token(1, "1", NUMBER)),
    ("15", Token(1, "15", NUMBER)),
    ("153", Token(1, "153", NUMBER)),
    ("1.5", Token(1, "1.5", NUMBER)),
    ("true", Token(1, "true", BOOLEAN)),
    ("false", Token(1, "false", BOOLEAN))
])
def test_data_types(source, expected_token):
    actual_tokens = get_tokens(source)
    assert actual_tokens == [expected_token, Token(1, "", EOF)]


@pytest.mark.parametrize("source, expected_tokens", [
    ("1 + 1;", [
        Token(1, "1", NUMBER),
        Token(1, "+", PLUS),
        Token(1, "1", NUMBER),
        Token(1, ";", SEMICOLON),
        Token(1, "", EOF)
    ]),
    ("a = 1;\nb = 2;", [
        Token(1, "a", IDENTIFIER),
        Token(1, "=", ASSIGN),
        Token(1, "1", NUMBER),
        Token(1, ";", SEMICOLON),
        Token(2, "b", IDENTIFIER),
        Token(2, "=", ASSIGN),
        Token(2, "2", NUMBER),
        Token(2, ";", SEMICOLON),
        Token(2, "", EOF)
    ]),
    ("a = (1, 2, 3, 4);", [
        Token(1, "a", IDENTIFIER),
        Token(1, "=", ASSIGN),
        Token(1, "(", OPEN_PAREN),
        Token(1, "1", NUMBER),
        Token(1, ",", COMMA),
        Token(1, "2", NUMBER),
        Token(1, ",", COMMA),
        Token(1, "3", NUMBER),
        Token(1, ",", COMMA),
        Token(1, "4", NUMBER),
        Token(1, ")", CLOSED_PAREN),
        Token(1, ";", SEMICOLON),
        Token(1, "", EOF)
    ])
])
def test_tokenizer(source, expected_tokens):
    actual_tokens = get_tokens(source)
    assert actual_tokens == expected_tokens


def test_skip_comments():
    source = """
    # this is a comment
    # THIS IS ANOTHER COMMENT BUT IN ALL CAPS!!!
    # a...third comment!
    a = 1;
    """
    line_num = 5
    actual_tokens = get_tokens(source)
    assert actual_tokens == [
        Token(line_num, "a", IDENTIFIER),
        Token(line_num, "=", ASSIGN),
        Token(line_num, "1", NUMBER),
        Token(line_num, ";", SEMICOLON),
        Token(line_num + 1, "", EOF)
    ]


def get_tokens(source: str) -> list[Token]:
    return [t for t in Tokenizer(source)]
