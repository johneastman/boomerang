# Symbols
ASSIGN = "ASSIGN"
PLUS = "PLUS"
MINUS = "MINUS"
MULTIPLY = "MULTIPLY"
DIVIDE = "DIVIDE"
SEMICOLON = "SEMICOLON"
OPEN_PAREN = "OPEN_PAREN"
CLOSED_PAREN = "CLOSED_PAREN"
OPEN_CURLY_BRACKET = "OPEN_CURLY_BRACKET"
CLOSED_CURLY_BRACKET = "CLOSED_CURLY_BRACKET"
COMMA = "COMMA"
COMMENT = "COMMENT"

# Keywords
LET = "LET"
RETURN = "RETURN"
FUNCTION = "FUNCTION"

# Misc
EOF = "EOF"  # End of File
NUMBER = "NUMBER"
IDENTIFIER = "IDENTIFIER"


class Token:

    def __init__(self, value, _type):
        self.value = value
        self.type = _type

    def __repr__(self):
        return f"{self.__class__.__name__}(value={self.value}, type={self.type})"


class Tokenizer:
    def __init__(self, source):
        self.source = source
        self.index = 0

    def tokenize(self):
        tokens = []

        while True:
            self.skip_whitespace()

            if self.current is None:
                break
            elif self.current == "#":
                self.skip_comment()
            elif self.current == "+":
                tokens.append(Token(self.current, PLUS))
            elif self.current == "-":
                tokens.append(Token(self.current, MINUS))
            elif self.current == "*":
                tokens.append(Token(self.current, MULTIPLY))
            elif self.current == "/":
                tokens.append(Token(self.current, DIVIDE))
            elif self.current == ";":
                tokens.append(Token(self.current, SEMICOLON))
            elif self.current == "(":
                tokens.append(Token(self.current, OPEN_PAREN))
            elif self.current == ")":
                tokens.append(Token(self.current, CLOSED_PAREN))
            elif self.current == "=":
                tokens.append(Token(self.current, ASSIGN))
            elif self.current == ",":
                tokens.append(Token(self.current, COMMA))
            elif self.current == "{":
                tokens.append(Token(self.current, OPEN_CURLY_BRACKET))
            elif self.current == "}":
                tokens.append(Token(self.current, CLOSED_CURLY_BRACKET))
            elif self.is_digit():
                number = self.read_number()
                tokens.append(Token(number, NUMBER))
                continue
            elif self.is_letter():
                letters = self.read_letters()
                keywords = {
                    "let": LET,
                    "return": RETURN,
                    "func": FUNCTION
                }
                keyword = keywords.get(letters, None)
                token_type = IDENTIFIER if keyword is None else keyword

                tokens.append(Token(letters, token_type))
                continue

            self.advance()

        tokens.append(Token("", EOF))  # Add end-of-file token
        return tokens

    @property
    def current(self):
        return self.source[self.index] if self.index < len(self.source) else None

    def advance(self):
        self.index += 1

    def skip_whitespace(self):
        while self.current is not None and self.current.isspace():
            self.advance()

    def skip_comment(self):
        while self.current is not None and self.current != ";":
            self.advance()

    def is_letter(self):
        return self.current is not None and self.current.isalpha()

    def is_digit(self):
        return self.current is not None and self.current.isdigit()

    def read_number(self):
        pos = self.index
        while self.is_digit():
            self.advance()
        return self.source[pos:self.index]

    def read_letters(self):
        pos = self.index
        while self.is_letter():
            self.advance()
        return self.source[pos:self.index]
