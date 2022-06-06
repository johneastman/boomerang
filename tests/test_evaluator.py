import unittest
import evaluator
import tokenizer
import _parser
import _environment


class TestEvaluator(unittest.TestCase):

    def test_evaluator(self):

        tests = [
            ("1 + 1;", [2]),
            ("1 + 2 * 2;", [5]),
            ("(1 + 2) * 2;", [6]),
            ("let x = (1 + 2) * 2;x;", ["null", 6])
        ]

        for source, expected_results in tests:
            actual_results = self.actual_result(source)
            self.assertEqual(expected_results, actual_results)

    def test_boolean_operators(self):
        tests = [
            ("1 == 1;", ["true"]),
            ("1 != 1;", ["false"]),
            ("1 != 2;", ["true"]),
            ("1 >= 1;", ["true"]),
            ("1 >= 2;", ["false"]),
            ("1 > 1;",  ["false"]),
            ("2 > 1;",  ["true"]),
            ("1 <= 1;", ["true"]),
            ("1 < 2;",  ["true"]),
            ("2 < 1;",  ["false"]),
            ("10 == (2 + 4 * 2) == true;",  ["true"]),
        ]

        for source, expected_results in tests:
            actual_results = self.actual_result(source)
            self.assertEqual(expected_results, actual_results)

    def actual_result(self, source):
        t = tokenizer.Tokenizer(source)
        tokens = t.tokenize()

        p = _parser.Parser(tokens)
        ast = p.parse()

        e = evaluator.Evaluator(ast, _environment.Environment())
        return e.evaluate()


if __name__ == "__main__":
    unittest.main()
