import unittest
from tokens.tokens import *
from tokens.tokenizer import Token
from _parser import _parser


class TestParser(unittest.TestCase):

    def test_precedence_add(self):

        tokens = [
            Token("1", INTEGER, 1),
            Token("+", PLUS, 1),
            Token("1", INTEGER, 1),
            Token(";", SEMICOLON, 1),
            Token("", EOF, 1)
        ]

        expected_ast = [
            _parser.BinaryOperation(
                _parser.Number(Token("1", INTEGER, 1)),
                Token("+", PLUS, 1),
                _parser.Number(Token("1", INTEGER, 1))
            )
        ]

        actual_ast = _parser.Parser(tokens).parse()
        self.assertEqual(expected_ast, actual_ast)

    def test_precedence_multiply(self):
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
            _parser.BinaryOperation(
                _parser.Number(Token("1", INTEGER, 1)),
                Token("+", PLUS, 1),
                _parser.BinaryOperation(
                    _parser.Number(Token("2", INTEGER, 1)),
                    Token("*", MULTIPLY, 1),
                    _parser.Number(Token("4", INTEGER, 1))
                )
            )
        ]

        actual_ast = _parser.Parser(tokens).parse()
        self.assertEqual(expected_ast, actual_ast)

    def test_precedence_and_or(self):
        tests = [
            ("AND", Token("&&", AND, 1)),
            ("OR",  Token("||", OR, 1))
        ]

        for test_name, operator_token in tests:
            with self.subTest(test_name):
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
                    _parser.BinaryOperation(
                        _parser.BinaryOperation(
                            _parser.Number(Token("1", INTEGER, 1)),
                            Token("==", EQ, 1),
                            _parser.Number(Token("1", INTEGER, 1))
                        ),
                        operator_token,
                        _parser.BinaryOperation(
                            _parser.Number(Token("2", INTEGER, 1)),
                            Token("!=", NE, 1),
                            _parser.Number(Token("3", INTEGER, 1)),
                        )
                    )
                ]

                actual_ast = _parser.Parser(tokens).parse()
                self.assertEqual(expected_ast, actual_ast)


if __name__ == '__main__':
    unittest.main()
