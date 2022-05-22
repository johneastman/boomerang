import unittest
import evaluator
import tokenizer
import _parser


class TestEvaluator(unittest.TestCase):

    def test_evaluator_1(self):
        source = "1 + 1;"
        result = self.actual_result(source)

        self.assertEqual([2], result)

    def test_evaluator_2(self):
        source = "1 + 2 * 2;"
        result = self.actual_result(source)

        self.assertEqual([5], result)

    def test_evaluator_3(self):
        source = "(1 + 2) * 2;"
        result = self.actual_result(source)

        self.assertEqual([6], result)

    def test_evaluator_variable(self):
        source = "let x = (1 + 2) * 2;x;"
        result = self.actual_result(source)

        self.assertEqual([None, 6], result)

    def actual_result(self, source):
        t = tokenizer.Tokenizer(source)
        tokens = t.tokenize()

        p = _parser.Parser(tokens)
        ast = p.parse()

        e = evaluator.Evaluator(ast)
        return e.evaluate()


if __name__ == "__main__":
    unittest.main()
