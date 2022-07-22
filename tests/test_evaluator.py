import unittest
from tokens.tokens import *
from tokens.tokenizer import Token, Tokenizer
from _parser._parser import Parser, NoReturn
from evaluator.evaluator import Evaluator
from evaluator._environment import Environment


class TestEvaluator(unittest.TestCase):

    def test_evaluator(self):
        tests = [
            ("1 + 1;", [Token(2, INTEGER, 1)]),
            ("1 + 2 * 2;", [Token(5, INTEGER, 1)]),
            ("(1 + 2) * 2;", [Token(6, INTEGER, 1)]),
            ("x = (1 + 2) * 2;x;", [Token(6, INTEGER, 1), Token(6, INTEGER, 1)]),
            ("4 / 2;", [Token(2.0, FLOAT, 1)]),
            ("7 / 2;", [Token(3.5, FLOAT, 1)]),
            ("1 + 1 * 2 + 3 / 4;", [Token(3.75, FLOAT, 1)]),
            ("\"hello \" + \"world!\";",  [Token("hello world!", STRING, 1)]),
            ("{\"a\": 1 + 1, \"b\": 3 + (2 * 2 + 1), \"c\": 55};", [Token({"a": 2, "b": 8, "c": 55}, DICTIONARY, 1)]),
        ]
        self.run_tests(tests)

    def test_boolean_operators(self):
        tests = [
            ("1 == 1;", [Token("true", BOOLEAN, 1)]),
            ("1 != 1;", [Token("false", BOOLEAN, 1)]),
            ("1 != 2;", [Token("true", BOOLEAN, 1)]),
            ("1 >= 1;", [Token("true", BOOLEAN, 1)]),
            ("1 >= 2;", [Token("false", BOOLEAN, 1)]),
            ("1 > 1;",  [Token("false", BOOLEAN, 1)]),
            ("2 > 1;",  [Token("true", BOOLEAN, 1)]),
            ("1 <= 1;", [Token("true", BOOLEAN, 1)]),
            ("1 < 2;",  [Token("true", BOOLEAN, 1)]),
            ("2 < 1;",  [Token("false", BOOLEAN, 1)]),
            ("10 == (2 + 4 * 2) == true;",  [Token("true", BOOLEAN, 1)])
        ]
        self.run_tests(tests)

    def test_invalid_boolean_operators(self):
        tests = [
            ("1 == true;", "INTEGER", "EQ", "BOOLEAN"),
            ("1 != true;", "INTEGER", "NE", "BOOLEAN"),
            ("1 > true;", "INTEGER", "GT", "BOOLEAN"),
            ("2 >= false;", "INTEGER", "GE", "BOOLEAN"),
            ("2 < false;", "INTEGER", "LT", "BOOLEAN"),
            ("2 <= false;", "INTEGER", "LE", "BOOLEAN"),

            # Check that we can't use boolean operators in less-than, greater-than, greater-than-or-equal, or
            # less-than-or-equal
            ("true <= false;", "BOOLEAN", "LE", "BOOLEAN"),
            ("true < false;", "BOOLEAN", "LT", "BOOLEAN"),
            ("true >= false;", "BOOLEAN", "GE", "BOOLEAN"),
            ("true > false;", "BOOLEAN", "GT", "BOOLEAN"),
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
                Token(-1, INTEGER, 1)
             ]),
            ("+1;", [
                Token(1, INTEGER, 1)
            ]),
            ("!true;", [
                Token("false", BOOLEAN, 1)
            ]),
            ("!false;", [
                Token("true", BOOLEAN, 1)
            ]),
        ]
        self.run_tests(tests)

    def test_invalid_unary_operators(self):
        tests = [
            ("!1;", "BANG", "INTEGER"),
            ("-true;", "MINUS", "BOOLEAN"),
            ("-false;", "MINUS", "BOOLEAN"),
            ("+true;", "PLUS", "BOOLEAN"),
            ("+false;", "PLUS", "BOOLEAN"),
        ]

        for source, op, _type in tests:
            with self.subTest(source):
                with self.assertRaises(Exception) as error:
                    self.actual_result(source)
                self.assertEqual(
                    f"Cannot perform {op} operation on {_type}",
                    str(error.exception)
                )

    def test_function_no_return(self):
        source = """
        func no_return() {
            x = 1;
        }
        
        var = no_return();
        """

        with self.assertRaises(Exception) as error:
            self.actual_result(source)
        self.assertEqual(
            f"Error at line 6: cannot evaluate expression that returns no value",
            str(error.exception)
        )

    def test_function_empty_body_no_return(self):
        source = """
        func no_return() {}
        var = no_return();
        """

        with self.assertRaises(Exception) as error:
            self.actual_result(source)
        self.assertEqual(
            f"Error at line 3: cannot evaluate expression that returns no value",
            str(error.exception)
        )

    def test_function_return(self):
        source = """
        func is_equal(a, b) {
            if (a == b) {
                return true;
            }
        }
        is_equal(1, 1);  # true
        is_equal(1, 2);  # No return
        """
        expected_results = [
            NoReturn(line_num=2),
            Token("true", BOOLEAN, 7),
            NoReturn(line_num=8),
        ]
        actual_results = self.actual_result(source)
        self.assert_tokens_equal(expected_results, actual_results)

    def test_function_calls(self):
        tests = [
            (1, 1, 2),
            (1, 2, 3),
            (12, 5, 17),
            (2, 3, 5)
        ]

        for first, second, result in tests:
            source = f"""
            func add(a, b) {{
                return a + b;
            }}
            add({first}, {second});
            """
            with self.subTest(f"add({first}, {second}) == {result}"):
                actual_results = self.actual_result(source)
                expected_results = [
                    NoReturn(line_num=2),
                    Token(result, INTEGER, 5)
                ]
                self.assert_tokens_equal(expected_results, actual_results)

    def test_assignment(self):
        tests = [
            ("a = 2; a += 2; a;", [
                Token("2", INTEGER, 1),
                Token(4, INTEGER, 1),
                Token(4, INTEGER, 1)
            ]),
            ("a = 2; a -= 2; a;", [
                Token("2", INTEGER, 1),
                Token(0, INTEGER, 1),
                Token(0, INTEGER, 1)
            ]),
            ("a = 2; a *= 2; a;", [
                Token("2", INTEGER, 1),
                Token(4, INTEGER, 1),
                Token(4, INTEGER, 1)
            ]),
            ("a = 2; a /= 2; a;", [
                Token("2", INTEGER, 1),
                Token(1.0, FLOAT, 1),
                Token(1.0, FLOAT, 1)
            ]),
            ("d = {\"a\": 2}; d[\"a\"] += 2; d[\"a\"];", [
                Token({"a": 2}, DICTIONARY, 1),
                NoReturn(line_num=1),
                Token(4, INTEGER, 1)
            ]),
            ("d = {\"a\": 2}; d[\"a\"] -= 2; d[\"a\"];", [
                Token({"a": 2}, DICTIONARY, 1),
                NoReturn(line_num=1),
                Token(0, INTEGER, 1)
            ]),
            ("d = {\"a\": 2}; d[\"a\"] *= 2; d[\"a\"];", [
                Token({"a": 2}, DICTIONARY, 1),
                NoReturn(line_num=1),
                Token(4, INTEGER, 1)
            ]),
            ("d = {\"a\": 2}; d[\"a\"] /= 2; d[\"a\"];", [
                Token({"a": 2}, DICTIONARY, 1),
                NoReturn(line_num=1),
                Token(1.0, FLOAT, 1)
            ]),
            ("d = {\"a\": 2}; d[\"a\"] = 5; d[\"a\"];", [
                Token({"a": 2}, DICTIONARY, 1),
                NoReturn(line_num=1),
                Token(5, INTEGER, 1)
            ])
        ]
        self.run_tests(tests)

    def test_dictionary_get(self):
        source = """
        d = {"a": 1, "b": 2, "c": 3};
        d["a"];
        d["b"];
        d["c"];
        """

        expected_values = [
            Token({"a": 1, "b": 2, "c": 3}, DICTIONARY, 2),
            Token(1, INTEGER, 3),
            Token(2, INTEGER, 4),
            Token(3, INTEGER, 5),
        ]
        actual_values = self.actual_result(source)
        self.assertEqual(expected_values, actual_values)

    def test_dictionary_get_invalid_key(self):
        source = """
        d = {"a": 1, "b": 2, "c": 3};
        d["d"];
        """

        with self.assertRaises(Exception) as error:
            self.actual_result(source)

        self.assertEqual(
            "Error at line 3: No key in dictionary: d",
            str(error.exception)
        )

    def run_tests(self, tests):
        for source, expected_results in tests:
            with self.subTest(source):
                actual_results = self.actual_result(source)
                self.assert_tokens_equal(expected_results, actual_results)

    def assert_tokens_equal(self, expected_results, actual_results):
        self.assertEqual(len(expected_results), len(actual_results))

        for expected, actual in zip(expected_results, actual_results):
            self.assertEqual(expected.value, actual.value)
            self.assertEqual(expected.type, actual.type)
            self.assertEqual(expected.line_num, actual.line_num)

    def actual_result(self, source):
        t = Tokenizer(source)
        tokens = t.tokenize()

        p = Parser(tokens)
        ast = p.parse()

        e = Evaluator(ast, Environment())
        return e.evaluate()


if __name__ == "__main__":
    unittest.main()
