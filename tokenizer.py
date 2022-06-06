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
NULL = "null"
IF = "if"
ELSE = "else"

# Misc
EOF = "EOF"  # End of File
NUMBER = "NUMBER"
IDENTIFIER = "IDENTIFIER"

token_literal_map = {
    "+": PLUS,
    "-": MINUS,
    "/": DIVIDE,
    "*": MULTIPLY,
    "=": ASSIGN,
    "!": BANG,
    ">": GREATER,
    "<": LESS,
    ";": SEMICOLON,
    "(": OPEN_PAREN,
    ")": CLOSED_PAREN,
    "{": OPEN_CURLY_BRACKET,
    "}": CLOSED_CURLY_BRACKET,
    "#": COMMENT,
    ",": COMMA
}

KEYWORDS = {
    "let": LET,
    "return": RETURN,
    "func": FUNCTION,
    "true": TRUE,
    "false": FALSE,
    "null": NULL,
    "if": IF,
    "else": ELSE
}


class Token:

    def __init__(self, value, _type, line_num):
        self.value = value
        self.type = _type
        self.line_num = line_num

    def __repr__(self):
        return f"{self.__class__.__name__}(value: {self.value}, type: {self.type}, line_num: {self.line_num})"

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return self.value == other.value and self.type == other.type and self.line_num == other.line_num


class Tokenizer:
    def __init__(self, source):
        self.source = source
        self.index = 0
        self.line_num = 1
        self.line_col = 1

    def tokenize(self):
        tokens = []

        while True:
            self.skip_whitespace()

            if self.current is None:
                break
            elif self.current == "#":
                self.skip_comment()
            elif self.current == "+":
                tokens.append(Token(self.current, PLUS, self.line_num))
            elif self.current == "-":
                tokens.append(Token(self.current, MINUS, self.line_num))
            elif self.current == "*":
                tokens.append(Token(self.current, MULTIPLY, self.line_num))
            elif self.current == "/":
                if self.next_char == "*":
                    self.skip_block_comment()
                else:
                    tokens.append(Token(self.current, DIVIDE, self.line_num))
                continue
            elif self.current == ";":
                tokens.append(Token(self.current, SEMICOLON, self.line_num))
            elif self.current == "(":
                tokens.append(Token(self.current, OPEN_PAREN, self.line_num))
            elif self.current == ")":
                tokens.append(Token(self.current, CLOSED_PAREN, self.line_num))
            elif self.current == "=":
                if self.next_char == "=":
                    token = self.create_two_char_token(EQ)
                    tokens.append(token)
                else:
                    tokens.append(Token(self.current, ASSIGN, self.line_num))
            elif self.current == "!":
                if self.next_char == "=":
                    token = self.create_two_char_token(NOT_EQ)
                    tokens.append(token)
                else:
                    tokens.append(Token(self.current, BANG, self.line_num))
            elif self.current == ",":
                tokens.append(Token(self.current, COMMA, self.line_num))
            elif self.current == "{":
                tokens.append(Token(self.current, OPEN_CURLY_BRACKET, self.line_num))
            elif self.current == "}":
                tokens.append(Token(self.current, CLOSED_CURLY_BRACKET, self.line_num))
            elif self.current == ">":
                if self.next_char == "=":
                    token = self.create_two_char_token(GREATER_EQUAL)
                    tokens.append(token)
                else:
                    tokens.append(Token(self.current, GREATER, self.line_num))
            elif self.current == "<":
                if self.next_char == "=":
                    token = self.create_two_char_token(LESS_EQ)
                    tokens.append(token)
                else:
                    tokens.append(Token(self.current, LESS, self.line_num))
            elif self.is_digit():
                number = self.read_number()
                tokens.append(Token(number, NUMBER, self.line_num))
                continue
            elif self.is_identifier():
                letters = self.read_identifier()
                keyword = KEYWORDS.get(letters, None)
                token_type = IDENTIFIER if keyword is None else keyword

                tokens.append(Token(letters, token_type, self.line_num))
                continue

            self.advance()

        tokens.append(Token("", EOF, self.line_num))  # Add end-of-file token
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
            if self.current == "\n":
                self.line_num += 1

            self.advance()

    def skip_comment(self):
        # If a hash symbol is found, skip until the end of the line
        while self.current is not None and self.current != "\n":
            self.advance()
        self.line_num += 1

    def skip_block_comment(self):
        while True:
            if self.current == "*" and self.next_char == "/":
                break

            if self.current == "\n":
                self.line_num += 1

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
        return Token(prev_char + self.current, token_type, self.line_num)
