import pytest

from tests.testing_utils import assert_tokens_equal, get_tokens
from interpreter.tokens import tokens as t
from interpreter.tokens.tokenizer import Token


@pytest.mark.parametrize("symbol, type_", [
    (";", t.SEMICOLON),
    ("<-", t.SEND),
    (",", t.COMMA),
    ("(", t.OPEN_PAREN),
    (")", t.CLOSED_PAREN),
    ("+", t.PLUS),
    ("-", t.MINUS),
    ("*", t.MULTIPLY),
    ("/", t.DIVIDE),
    ("=", t.ASSIGN),
    ("==", t.EQ),
    ("!=", t.NE),
    (">", t.GT),
    (">=", t.GE),
    ("<", t.LT),
    ("<=", t.LE),
    ("!", t.BANG),
    (":", t.COLON),
    ("--", t.DEC),
    ("++", t.INC),
    ("%", t.MOD),
    ("@", t.INDEX),
    ("**", t.PACK)
])
def test_symbols(symbol, type_):
    """Test symbols

    Symbols that are not stand-alone tokens:
    - PERIOD (indicates floating-point value in numbers)
    - DOUBLE_QUOTE (indicates start and end of strings)
    """
    actual_tokens = get_tokens(symbol)
    assert_tokens_equal([Token(1, symbol, type_), Token(1, "", t.EOF)], actual_tokens)


@pytest.mark.parametrize("keyword, type_", [
    ("true", t.BOOLEAN),
    ("false", t.BOOLEAN),
    ("func", t.FUNCTION),
    ("when", t.WHEN),
    ("is", t.IS),
    ("else", t.ELSE),
    ("for", t.FOR),
    ("in", t.IN),
    ("and", t.AND),
    ("or", t.OR),
    ("xor", t.XOR),
    ("if", t.IF)
])
def test_keywords(keyword, type_):
    """Test symbols

    Symbols that are not stand-alone tokens:
    - PERIOD (indicates floating-point value in numbers)
    - DOUBLE_QUOTE (indicates start and end of strings)
    """
    actual_tokens = get_tokens(keyword)
    assert_tokens_equal([Token(1, keyword, type_), Token(1, "", t.EOF)], actual_tokens)


@pytest.mark.parametrize("source,expected_token", [
    ("\"hello, world!\"", Token(1, "hello, world!", t.STRING)),
    ("1", Token(1, "1", t.NUMBER)),
    ("15", Token(1, "15", t.NUMBER)),
    ("153", Token(1, "153", t.NUMBER)),
    ("1.5", Token(1, "1.5", t.NUMBER)),
    ("true", Token(1, "true", t.BOOLEAN)),
    ("false", Token(1, "false", t.BOOLEAN))
])
def test_data_types(source, expected_token):
    actual_tokens = get_tokens(source)
    assert_tokens_equal([expected_token, Token(1, "", t.EOF)], actual_tokens)


@pytest.mark.parametrize("source, expected_tokens", [
    ("1 + 1;", [
        Token(1, "1", t.NUMBER),
        Token(1, "+", t.PLUS),
        Token(1, "1", t.NUMBER),
        Token(1, ";", t.SEMICOLON),
        Token(1, "", t.EOF)
    ]),
    ("a = 1;\nb = 2;", [
        Token(1, "a", t.IDENTIFIER),
        Token(1, "=", t.ASSIGN),
        Token(1, "1", t.NUMBER),
        Token(1, ";", t.SEMICOLON),
        Token(2, "b", t.IDENTIFIER),
        Token(2, "=", t.ASSIGN),
        Token(2, "2", t.NUMBER),
        Token(2, ";", t.SEMICOLON),
        Token(2, "", t.EOF)
    ]),
    ("a = (1, 2, 3, 4);", [
        Token(1, "a", t.IDENTIFIER),
        Token(1, "=", t.ASSIGN),
        Token(1, "(", t.OPEN_PAREN),
        Token(1, "1", t.NUMBER),
        Token(1, ",", t.COMMA),
        Token(1, "2", t.NUMBER),
        Token(1, ",", t.COMMA),
        Token(1, "3", t.NUMBER),
        Token(1, ",", t.COMMA),
        Token(1, "4", t.NUMBER),
        Token(1, ")", t.CLOSED_PAREN),
        Token(1, ";", t.SEMICOLON),
        Token(1, "", t.EOF)
    ])
])
def test_tokenizer(source, expected_tokens):
    actual_tokens = get_tokens(source)
    assert_tokens_equal(expected_tokens, actual_tokens)


def test_skip_comments():
    source = """
    # this is a comment
    # THIS IS ANOTHER COMMENT BUT IN ALL CAPS!!!
    # a...third comment!
    a = 1;
    """
    line_num = 5
    actual_tokens = get_tokens(source)
    expected_tokens = [
        Token(line_num, "a", t.IDENTIFIER),
        Token(line_num, "=", t.ASSIGN),
        Token(line_num, "1", t.NUMBER),
        Token(line_num, ";", t.SEMICOLON),
        Token(line_num + 1, "", t.EOF)
    ]
    assert_tokens_equal(expected_tokens, actual_tokens)
