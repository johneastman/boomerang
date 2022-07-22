from .tokens import *
import string

tokens_dict = get_keyword_dict()


class Token:

    def __init__(self, value: object, _type: str, line_num: int):
        self.value = value
        self.type = _type
        self.line_num = line_num

    def __repr__(self):
        return f"{self.__class__.__name__}(value: {self.value}, type: {self.type}, line_num: {self.line_num})"

    def __eq__(self, other: object):
        if not isinstance(other, Token):
            return False
        return self.value == other.value and self.type == other.type and self.line_num == other.line_num


class Tokenizer:
    def __init__(self, source: str):
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

            elif self.is_digit():
                number = self.read_number()
                token_type = FLOAT if "." in number else INTEGER
                tokens.append(Token(number, token_type, self.line_num))
                continue

            elif self.is_identifier():
                letters = self.read_identifier()

                # Any string that is not a keyword is an identifier (variable, function, etc.)
                token_type = tokens_dict.get(letters, IDENTIFIER)
                tokens.append(Token(letters, token_type, self.line_num))
                continue

            elif self.is_string():
                self.advance()
                string_literal = self.read_string()
                tokens.append(Token(string_literal, STRING, self.line_num))
                self.advance()

            else:
                # Find all tokens starting with the current character. Sort by the length of each token in descending
                # order. This ensures shorter tokens with similar characters to longer tokens are not mistakenly
                # matched (for example, '==' might get confused as two '=' if the smaller tokens are ordered first).
                matching_tokens = sorted(
                    [(l, t, len(l)) for l, t in tokens_dict.items() if l.startswith(self.current)],
                    key=lambda data: data[2], reverse=True
                )

                # If no tokens are found, then assume an invalid character
                if len(matching_tokens) == 0:
                    self.raise_invalid_char(self.current)

                for literal, _type, literal_len in matching_tokens:
                    matching_source = self.source[self.index:self.index + literal_len]
                    if matching_source == literal:

                        # Skip single-line and block comments
                        if _type == COMMENT:
                            self.skip_comment()
                        elif _type == BLOCK_COMMENT:
                            self.skip_block_comment()
                            break
                        else:
                            tokens.append(Token(literal, _type, self.line_num))

                        # Advance past the number of characters in the matching token
                        for _ in range(literal_len):
                            self.advance()
                        break

        tokens.append(Token("", EOF, self.line_num))  # Add end-of-file token
        return tokens

    def raise_invalid_char(self, char: str):
        raise Exception(f"Invalid character: {char}")

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
                # Advance past two characters that close the block comment
                self.advance()
                self.advance()
                break

            if self.current == "\n":
                self.line_num += 1

            self.advance()

    def is_string(self):
        return self.current is not None and self.current == get_token_literal("DOUBLE_QUOTE")

    def is_identifier(self, include_nums: bool = False):
        """Determine if a character is valid for an identifier (a-z, A-Z, 0-9, _)

        :param include_nums: Set if digits are allowed in the valid identifier characters. Identifiers can't start
        with numbers, but can include numbers.
        :return:
        """
        valid_chars = string.ascii_letters + "_"
        if include_nums:
            valid_chars += string.digits

        return self.current is not None and self.current in valid_chars

    def is_digit(self):
        return self.current is not None and (self.current.isdigit() or self.current == ".")

    def read_number(self):
        pos = self.index
        while self.is_digit():
            self.advance()
        return self.source[pos:self.index]

    def read_string(self):
        pos = self.index
        while not self.is_string():
            self.advance()
        return self.source[pos:self.index]

    def read_identifier(self):
        pos = self.index
        while self.is_identifier(include_nums=True):
            self.advance()
        return self.source[pos:self.index]
