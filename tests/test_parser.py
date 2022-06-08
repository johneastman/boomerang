import unittest
from tokenizer import *
import _parser


class TestParser(unittest.TestCase):

    def test_precedence_add(self):

        tokens = [
            Token("1", NUMBER, 1),
            Token("+", PLUS, 1),
            Token("1", NUMBER, 1),
            Token(";", SEMICOLON, 1),
            Token("", EOF, 1)
        ]

        expected_ast = [
            _parser.BinaryOperation(
                _parser.Number(Token("1", NUMBER, 1)),
                Token("+", PLUS, 1),
                _parser.Number(Token("1", NUMBER, 1))
            )
        ]

        actual_ast = _parser.Parser(tokens).parse()
        self.assertEqual(expected_ast, actual_ast)

    def test_precedence_multiply(self):
        tokens = [
            Token("1", NUMBER, 1),
            Token("+", PLUS, 1),
            Token("2", NUMBER, 1),
            Token("*", MULTIPLY, 1),
            Token("4", NUMBER, 1),
            Token(";", SEMICOLON, 1),
            Token("", EOF, 1)
        ]

        expected_ast = [
            _parser.BinaryOperation(
                _parser.Number(Token("1", NUMBER, 1)),
                Token("+", PLUS, 1),
                _parser.BinaryOperation(
                    _parser.Number(Token("2", NUMBER, 1)),
                    Token("*", MULTIPLY, 1),
                    _parser.Number(Token("4", NUMBER, 1))
                )
            )
        ]

        actual_ast = _parser.Parser(tokens).parse()
        self.assertEqual(expected_ast, actual_ast)


if __name__ == '__main__':
    unittest.main()
