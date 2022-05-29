import unittest
from tokenizer import *


class TestTokenizer(unittest.TestCase):

    def test_tokenizer(self):

        tests = [
            ("1 + 1;", [
                Token("1", NUMBER, 1),
                Token("+", PLUS, 1),
                Token("1", NUMBER, 1),
                Token(";", SEMICOLON, 1),
                Token("", EOF, 1)
            ]),
            ("let a = 1;\nlet b = 2;", [
                Token("let", LET, 1),
                Token("a", IDENTIFIER, 1),
                Token("=", ASSIGN, 1),
                Token("1", NUMBER, 1),
                Token(";", SEMICOLON, 1),
                Token("let", LET, 2),
                Token("b", IDENTIFIER, 2),
                Token("=", ASSIGN, 2),
                Token("2", NUMBER, 2),
                Token(";", SEMICOLON, 2),
                Token("", EOF, 2),
            ])
        ]

        for source, expected_tokens in tests:
            t = Tokenizer(source)
            actual_tokens = t.tokenize()
            self.assert_tokens_equal(expected_tokens, actual_tokens)

    def assert_tokens_equal(self, expected_tokens, actual_tokens):
        self.assertEqual(len(expected_tokens), len(actual_tokens))
        for expected, actual in zip(expected_tokens, actual_tokens):
            self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
