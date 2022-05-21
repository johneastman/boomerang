import tokens
import tokenizer
import unittest


class TestTokenizer(unittest.TestCase):

    def test_next_token(self):

        source_code = """
        let five = 5;
        let ten = 10;
        
        let add = fn(x, y) {
          x + y;
        };
        
        let result = add(five, ten);
        !-/*5;
        5 < 10 > 5;
        
        if (5 < 10) {
            return true;
        } else {
            return false;
        }
        """
        tests = [
            (tokens.LET, "let"),
            (tokens.IDENT, "five"),
            (tokens.ASSIGN, "="),
            (tokens.INT, "5"),
            (tokens.SEMICOLON, ";"),
            (tokens.LET, "let"),
            (tokens.IDENT, "ten"),
            (tokens.ASSIGN, "="),
            (tokens.INT, "10"),
            (tokens.SEMICOLON, ";"),
            (tokens.LET, "let"),
            (tokens.IDENT, "add"),
            (tokens.ASSIGN, "="),
            (tokens.FUNCTION, "fn"),
            (tokens.LPAREN, "("),
            (tokens.IDENT, "x"),
            (tokens.COMMA, ","),
            (tokens.IDENT, "y"),
            (tokens.RPAREN, ")"),
            (tokens.LBRACE, "{"),
            (tokens.IDENT, "x"),
            (tokens.PLUS, "+"),
            (tokens.IDENT, "y"),
            (tokens.SEMICOLON, ";"),
            (tokens.RBRACE, "}"),
            (tokens.SEMICOLON, ";"),
            (tokens.LET, "let"),
            (tokens.IDENT, "result"),
            (tokens.ASSIGN, "="),
            (tokens.IDENT, "add"),
            (tokens.LPAREN, "("),
            (tokens.IDENT, "five"),
            (tokens.COMMA, ","),
            (tokens.IDENT, "ten"),
            (tokens.RPAREN, ")"),
            (tokens.SEMICOLON, ";"),
            (tokens.BANG, "!"),
            (tokens.MINUS, "-"),
            (tokens.SLASH, "/"),
            (tokens.ASTERISK, "*"),
            (tokens.INT, "5"),
            (tokens.SEMICOLON, ";"),
            (tokens.INT, "5"),
            (tokens.LT, "<"),
            (tokens.INT, "10"),
            (tokens.GT, ">"),
            (tokens.INT, "5"),
            (tokens.SEMICOLON, ";"),
            (tokens.IF, "if"),
            (tokens.LPAREN, "("),
            (tokens.INT, "5"),
            (tokens.LT, "<"),
            (tokens.INT, "10"),
            (tokens.RPAREN, ")"),
            (tokens.LBRACE, "{"),
            (tokens.RETURN, "return"),
            (tokens.TRUE, "true"),
            (tokens.SEMICOLON, ";"),
            (tokens.RBRACE, "}"),
            (tokens.ELSE, "else"),
            (tokens.LBRACE, "{"),
            (tokens.RETURN, "return"),
            (tokens.FALSE, "false"),
            (tokens.SEMICOLON, ";"),
            (tokens.RBRACE, "}"),
            (tokens.EOF, "")
        ]

        t = tokenizer.Tokenizer(source_code)
        for expected_type, expected_literal in tests:
            tok = t.next_token()
            self.assertEqual(expected_type, tok.type)
            self.assertEqual(expected_literal, tok.literal)

    def test_tokenizer_double_char_tokens(self):
        source_code = """
        ==
        !=
        """

        tests = [
            (tokens.EQ, "=="),
            (tokens.NOT_EQ, "!=")
        ]

        t = tokenizer.Tokenizer(source_code)
        for expected_type, expected_literal in tests:
            tok = t.next_token()
            self.assertEqual(expected_type, tok.type)
            self.assertEqual(expected_literal, tok.literal)


if __name__ == "__main__":
    unittest.main()
