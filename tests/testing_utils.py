import pytest

from tokens.tokenizer import Token
from _parser.ast_objects import DictionaryToken, NoReturn


def assert_tokens_equal(expected_tokens: list[Token], actual_tokens: list[Token]):
    assert len(expected_tokens) == len(actual_tokens)

    for expected, actual in zip(expected_tokens, actual_tokens):

        if isinstance(expected, DictionaryToken) and isinstance(actual, DictionaryToken):
            assert_dictionary_tokens_equal(expected, actual)
        elif isinstance(expected, NoReturn) and isinstance(actual, NoReturn):
            assert_token_equal(expected, actual)
        elif isinstance(expected, Token) and isinstance(actual, Token):
            assert_token_equal(expected, actual)
        else:
            pytest.fail(f"expected type: {type(expected)} != actual type: {type(actual)}")


def assert_token_equal(expected: Token, actual: Token) -> None:
    assert expected.value == actual.value
    assert expected.type == actual.type
    assert expected.line_num == actual.line_num


def assert_dictionary_tokens_equal(expected: DictionaryToken, actual: DictionaryToken):
    assert expected.value == actual.value
    assert expected.type == actual.type
    assert expected.line_num == actual.line_num

    for (expected_key, expected_val), (actual_key, actual_val) in zip(expected.data.items(), actual.data.items()):
        assert type(expected_key) == Token
        assert type(actual_key) == Token
        assert_token_equal(expected_key, actual_key)

        if isinstance(expected_val, DictionaryToken) and isinstance(actual_val, DictionaryToken):
            assert_dictionary_tokens_equal(expected_val, actual_val)
        elif isinstance(expected_val, Token) and isinstance(actual_val, Token):
            assert expected_val.value == actual_val.value
            assert expected_val.type == actual_val.type
            assert expected_val.line_num == actual_val.line_num
        else:
            pytest.fail(f"expected type: {type(expected_val)} != actual type: {type(actual_val)}")
