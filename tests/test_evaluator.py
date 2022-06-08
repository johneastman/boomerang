import unittest
from tokenizer import *
from _parser import Parser
from evaluator import Evaluator
from _environment import Environment


class TestEvaluator(unittest.TestCase):

    def test_evaluator(self):
        tests = [
            ("1 + 1;", [
                Token(2, NUMBER, 1)
            ]),
            ("1 + 2 * 2;", [
                Token(5, NUMBER, 1)]),
            ("(1 + 2) * 2;", [
                Token(6, NUMBER, 1)
            ]),
            ("let x = (1 + 2) * 2;x;", [
                Token("null", NULL, 1),
                Token(6, NUMBER, 1)
            ])
        ]
        self.run_tests(tests)

    def test_boolean_operators(self):
        tests = [
            ("1 == 1;", [Token("true", TRUE, 1)]),
            ("1 != 1;", [Token("false", FALSE, 1)]),
            ("1 != 2;", [Token("true", TRUE, 1)]),
            ("1 >= 1;", [Token("true", TRUE, 1)]),
            ("1 >= 2;", [Token("false", FALSE, 1)]),
            ("1 > 1;",  [Token("false", FALSE, 1)]),
            ("2 > 1;",  [Token("true", TRUE, 1)]),
            ("1 <= 1;", [Token("true", TRUE, 1)]),
            ("1 < 2;",  [Token("true", TRUE, 1)]),
            ("2 < 1;",  [Token("false", FALSE, 1)]),
            ("10 == (2 + 4 * 2) == true;",  [Token("true", TRUE, 1)]),
        ]
        self.run_tests(tests)

    def run_tests(self, tests):
        for source, expected_results in tests:
            with self.subTest(source):
                actual_results = self.actual_result(source)
                self.assertEqual(expected_results, actual_results)

    def test_invalid_boolean_operators(self):
        tests = [
            ("1 == true;", "NUMBER", "EQ", "TRUE"),
            ("1 != true;", "NUMBER", "NE", "TRUE"),
            ("1 > true;", "NUMBER", "GT", "TRUE"),
            ("2 >= false;", "NUMBER", "GE", "FALSE"),
            ("2 < false;", "NUMBER", "LT", "FALSE"),
            ("2 <= false;", "NUMBER", "LE", "FALSE"),

            # Check that we can't use boolean operators in less-than, greater-than, greater-than-or-equal, or
            # less-than-or-equal
            ("true <= false;", "TRUE", "LE", "FALSE"),
            ("true < false;", "TRUE", "LT", "FALSE"),
            ("true >= false;", "TRUE", "GE", "FALSE"),
            ("true > false;", "TRUE", "GT", "FALSE"),
        ]

        for source, left_type, operation_type, right_type in tests:
            with self.subTest(source):
                with self.assertRaises(Exception) as error:
                    self.actual_result(source)
                self.assertEqual(
                    f"Cannot perform {operation_type} operation on {left_type} and {right_type}",
                    str(error.exception))

    def test_valid_unary_operators(self):
        tests = [
            ("-1;", [
                Token(-1, NUMBER, 1)
             ]),
            ("+1;", [
                Token(1, NUMBER, 1)
            ]),
            ("!true;", [
                Token("false", FALSE, 1)
            ]),
            ("!false;", [
                Token("true", TRUE, 1)
            ]),
        ]

        for source, expected in tests:
            with self.subTest(source):
                actual = self.actual_result(source)
                self.assertEqual(expected, actual)

    def test_invalid_unary_operators(self):
        tests = [
            ("!1;", "BANG", "NUMBER"),
            ("-true;", "MINUS", "TRUE"),
            ("-false;", "MINUS", "FALSE"),
            ("+true;", "PLUS", "TRUE"),
            ("+false;", "PLUS", "FALSE"),
        ]

        for source, op, _type in tests:
            with self.subTest(source):
                with self.assertRaises(Exception) as error:
                    self.actual_result(source)
                self.assertEqual(
                    f"Cannot perform {op} operation on {_type}",
                    str(error.exception)
                )

    def actual_result(self, source):
        t = Tokenizer(source)
        tokens = t.tokenize()

        p = Parser(tokens)
        ast = p.parse()

        e = Evaluator(ast, Environment())
        return e.evaluate()


if __name__ == "__main__":
    unittest.main()
