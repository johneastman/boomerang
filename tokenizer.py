import string

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

# Comparison/Boolean Operators
EQ = "EQ"
NOT_EQ = "NOT_EQ"
GREATER_EQUAL = "GREATER_EQUAL"
LESS_EQ = "LESS_EQ"
GREATER = "GREATER"
LESS = "LESS"
BANG = "BANG"

# Keywords
LET = "LET"
RETURN = "RETURN"
FUNCTION = "FUNCTION"
TRUE = "TRUE"
FALSE = "FALSE"

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
                if self.next_char == "*":
                    self.skip_block_comment()
                else:
                    tokens.append(Token(self.current, DIVIDE))
            elif self.current == ";":
                tokens.append(Token(self.current, SEMICOLON))
            elif self.current == "(":
                tokens.append(Token(self.current, OPEN_PAREN))
            elif self.current == ")":
                tokens.append(Token(self.current, CLOSED_PAREN))
            elif self.current == "=":
                if self.next_char == "=":
                    token = self.create_two_char_token(EQ)
                    tokens.append(token)
                else:
                    tokens.append(Token(self.current, ASSIGN))
            elif self.current == "!":
                if self.next_char == "=":
                    token = self.create_two_char_token(NOT_EQ)
                    tokens.append(token)
                else:
                    tokens.append(Token(self.current, BANG))
            elif self.current == ",":
                tokens.append(Token(self.current, COMMA))
            elif self.current == "{":
                tokens.append(Token(self.current, OPEN_CURLY_BRACKET))
            elif self.current == "}":
                tokens.append(Token(self.current, CLOSED_CURLY_BRACKET))
            elif self.current == ">":
                if self.next_char == "=":
                    token = self.create_two_char_token(GREATER_EQUAL)
                    tokens.append(token)
                else:
                    tokens.append(Token(self.current, GREATER))
            elif self.current == "<":
                if self.next_char == "=":
                    token = self.create_two_char_token(LESS_EQ)
                    tokens.append(token)
                else:
                    tokens.append(Token(self.current, LESS))
            elif self.is_digit():
                number = self.read_number()
                tokens.append(Token(number, NUMBER))
                continue
            elif self.is_identifier():
                letters = self.read_identifier()
                keywords = {
                    "let": LET,
                    "return": RETURN,
                    "func": FUNCTION,
                    "true": TRUE,
                    "false": FALSE
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

    @property
    def next_char(self):
        next_char_index = self.index + 1
        return self.source[next_char_index] if next_char_index < len(self.source) else None

    def advance(self):
        self.index += 1

    def skip_whitespace(self):
        while self.current is not None and self.current.isspace():
            self.advance()

    def skip_comment(self):
        # If a hash symbol is found, skip until the end of the line
        while self.current is not None and self.current != "\n":
            self.advance()

    def skip_block_comment(self):
        while self.current != "*" or self.next_char != "/":
            self.advance()

        self.advance()
        self.advance()

    def is_identifier(self, include_nums=False):
        """Determine if a character is valid for an identifier (a-z, A-Z, 0-9, _)

        :param include_nums: Set if digits are allowed in the valid identifier characters. Identifiers can't start
        with numbers, but can include numbers.
        :return:
        :rtype:
        """
        valid_chars = string.ascii_letters + "_"
        if include_nums:
            valid_chars += string.digits

        return self.current is not None and self.current in valid_chars

    def is_digit(self):
        return self.current is not None and self.current.isdigit()

    def read_number(self):
        pos = self.index
        while self.is_digit():
            self.advance()
        return self.source[pos:self.index]

    def read_identifier(self):
        pos = self.index
        while self.is_identifier(include_nums=True):
            self.advance()
        return self.source[pos:self.index]

    def create_two_char_token(self, token_type):
        prev_char = self.current
        self.advance()
        return Token(prev_char + self.current, token_type)


