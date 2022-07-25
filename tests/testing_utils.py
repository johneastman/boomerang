from tokens.tokenizer import Token


def assert_tokens_equal(expected_tokens: list[Token], actual_tokens: list[Token]):
    assert len(expected_tokens) == len(actual_tokens)

    for expected, actual in zip(expected_tokens, actual_tokens):
        assert expected.value == actual.value
        assert expected.type == actual.type
        assert expected.line_num == actual.line_num