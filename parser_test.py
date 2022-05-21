import unittest
import tokenizer
import _parser


class TestParser(unittest.TestCase):

    def test_let_statements(self):

        source_code = """
        let x = 5;
        let y = 10;
        let foobar = 838383;
        """

        t = tokenizer.Tokenizer(source_code)
        p = _parser.Parser(t)

        program = p.parse_program()
        self.check_for_errors(p.errors)

        self.assertIsNotNone(program)
        self.assertEqual(3, len(program.statements))

        tests = [
            "x",
            "y",
            "foobar"
        ]

        for i, name in enumerate(tests):
            statement = program.statements[i]

            self.assertEqual(_parser.LetStatement, type(statement))
            self.assertEqual("let", statement.token_literal())

            self.assertEqual(name, statement.name.value)
            self.assertEqual(name, statement.name.token_literal())

    def test_return_statements(self):
        source = """
        return 5;
        return 10;
        return 993322;
        """

        t = tokenizer.Tokenizer(source)
        p = _parser.Parser(t)

        program = p.parse_program()
        self.check_for_errors(p.errors)

        for statement in program.statements:
            self.assertEqual(_parser.ReturnStatement, type(statement))
            self.assertEqual("return", statement.token_literal())

    def check_for_errors(self, errors):
        if len(errors) > 0:
            for error in errors:
                print(error)
            self.fail("No errors expected")


if __name__ == "__main__":
    unittest.main()
