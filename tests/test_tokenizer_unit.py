import pytest
from tokens.tokenizer import Tokenizer

digit_data = [
    ("0", True),
    ("1", True),
    ("2", True),
    ("3", True),
    ("4", True),
    ("5", True),
    ("6", True),
    ("7", True),
    ("8", True),
    ("9", True),
    ("a", False),
    ("b", False),
    ("c", False),
    ("!", False),
    ("@", False),
    ("#", False),
    ("$", False)
]


@pytest.mark.parametrize("source,is_digit", digit_data)
def test_is_digit(source, is_digit):
    tokenizer = Tokenizer(source)
    assert tokenizer.is_digit() is is_digit


string_char_data = [
    ("\"", True),
    ("'", False),
    ("1", False),
    ("a", False)
]


@pytest.mark.parametrize("source,is_string", string_char_data)
def test_is_string(source, is_string):
    tokenizer = Tokenizer(source)
    assert tokenizer.is_string() is is_string


identifier_char_data = [
    ("a", False, True),
    ("A", False, True),
    ("b", False, True),
    ("B", False, True),
    ("c", False, True),
    ("C", False, True),
    ("d", False, True),
    ("D", False, True),
    ("e", False, True),
    ("E", False, True),
    ("f", False, True),
    ("F", False, True),
    ("g", False, True),
    ("G", False, True),
    ("h", False, True),
    ("H", False, True),
    ("i", False, True),
    ("I", False, True),
    ("j", False, True),
    ("J", False, True),
    ("k", False, True),
    ("K", False, True),
    ("l", False, True),
    ("L", False, True),
    ("m", False, True),
    ("M", False, True),
    ("n", False, True),
    ("N", False, True),
    ("o", False, True),
    ("O", False, True),
    ("p", False, True),
    ("P", False, True),
    ("q", False, True),
    ("Q", False, True),
    ("r", False, True),
    ("R", False, True),
    ("s", False, True),
    ("S", False, True),
    ("t", False, True),
    ("T", False, True),
    ("u", False, True),
    ("U", False, True),
    ("v", False, True),
    ("V", False, True),
    ("w", False, True),
    ("W", False, True),
    ("x", False, True),
    ("X", False, True),
    ("y", False, True),
    ("Y", False, True),
    ("z", False, True),
    ("Z", False, True),
    ("_", False, True),
    ("0", True, True),
    ("1", True, True),
    ("2", True, True),
    ("3", True, True),
    ("4", True, True),
    ("5", True, True),
    ("6", True, True),
    ("7", True, True),
    ("8", True, True),
    ("9", True, True),
    ("0", False, False),
    ("1", False, False),
    ("2", False, False),
    ("3", False, False),
    ("4", False, False),
    ("5", False, False),
    ("6", False, False),
    ("7", False, False),
    ("8", False, False),
    ("9", False, False)
]


@pytest.mark.parametrize("source,include_nums,is_identifier", identifier_char_data)
def test_is_string(source, include_nums, is_identifier):
    tokenizer = Tokenizer(source)
    assert tokenizer.is_identifier(include_nums=include_nums) is is_identifier


number_data = [
    ("1;", "1"),
    ("2;", "2"),
    ("1234567890;", "1234567890"),
    ("14.5;", "14.5"),
    ("3.14159;", "3.14159"),
    ("1234567890.0987654321;", "1234567890.0987654321"),
]


@pytest.mark.parametrize("source,expected_number", number_data)
def test_read_number(source, expected_number):
    tokenizer = Tokenizer(source)
    actual_number = tokenizer.read_number()
    assert expected_number == actual_number


identifier_data = [
    ("variable;", "variable"),
    ("variable1;", "variable1"),
    ("my_number__;", "my_number__"),
    ("_;", "_"),
    ("100;", "100"),
    (";", ""),
]


@pytest.mark.parametrize("source, expected_identifier", identifier_data)
def test_read_identifier(source, expected_identifier):
    tokenizer = Tokenizer(source)
    actual_identifier = tokenizer.read_identifier()
    assert actual_identifier == expected_identifier


def test_advance():
    source = "1 + 1 - (2 * 4);"
    tokenizer = Tokenizer(source)
    for i, char in enumerate(source):
        assert tokenizer.current == char
        assert tokenizer.index == i
        tokenizer.advance()

    assert tokenizer.current is None  # current is a property and acts like a method call
    assert tokenizer.index == len(source)
