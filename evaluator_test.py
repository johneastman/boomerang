import unittest
import evaluator
import tokenizer
import _parser


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

    def actual_result(self, source):
        t = tokenizer.Tokenizer(source)
        tokens = t.tokenize()

        p = _parser.Parser(tokens)
        ast = p.parse()

        e = evaluator.Evaluator(ast)
        return e.evaluate()


if __name__ == "__main__":
    unittest.main()
