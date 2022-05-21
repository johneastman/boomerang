import tokens


class Tokenizer:
    def __init__(self, _input):
        self.input = _input
        self.position = 0  # position of current character
        self.read_position = 0  # position of next character
        self.ch = None

        self.read_char()

    def read_char(self):
        self.ch = None if self.read_position >= len(self.input) else self.input[self.read_position]
        self.position = self.read_position
        self.read_position += 1

    def peek_char(self):
        return None if self.read_position >= len(self.input) else self.input[self.read_position]

    def next_token(self):
        self.skip_whitespace()

        if self.ch is None:
            tok = tokens.Token(tokens.EOF, "")
        elif self.ch == "=":
            if self.peek_char() == "=":
                ch = self.ch
                self.read_char()
                tok = tokens.Token(tokens.EQ, ch + self.ch)
            else:
                tok = tokens.Token(tokens.ASSIGN, self.ch)
        elif self.ch == "!":
            if self.peek_char() == "=":
                ch = self.ch
                self.read_char()
                tok = tokens.Token(tokens.NOT_EQ, ch + self.ch)
            else:
                tok = tokens.Token(tokens.BANG, self.ch)
        elif (_type := tokens.single_char_lookup(self.ch)) is not None:
            tok = tokens.Token(_type, self.ch)
        else:
            if self.is_letter():
                literal = self.read_identifier()
                _type = tokens.keyword_lookup(literal)
                return tokens.Token(_type, literal)
            elif self.is_digit():
                literal = self.read_number()
                return tokens.Token(tokens.INT, literal)
            else:
                tok = tokens.Token(tokens.ILLEGAL, self.ch)

        self.read_char()
        return tok

    def read_identifier(self):
        pos = self.position
        while self.ch is not None and self.is_letter():
            self.read_char()
        return self.input[pos:self.position]

    def read_number(self):
        pos = self.position
        while self.ch is not None and self.is_digit():
            self.read_char()
        return self.input[pos:self.position]

    def skip_whitespace(self):
        while self.ch is not None and self.ch.isspace():
            self.read_char()

    def is_letter(self):
        return self.ch is not None and self.ch.isalpha()

    def is_digit(self):
        return self.ch is not None and self.ch.isdigit()
