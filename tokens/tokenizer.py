from typing import Optional, Callable, Tuple
import string

from .tokens import *

tokens_dict = get_keyword_dict([KEYWORDS, SYMBOLS])


class Token:

    def __init__(self, value: str, _type: str, line_num: int) -> None:
        self.value = value
        self.type = _type
        self.line_num = line_num

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value: {self.value}, type: {self.type}, line_num: {self.line_num})"

    def __eq__(self, other: object) -> bool:
        """Check if token objects are equal."""
        if not isinstance(other, Token):
            return False
        return self.value == other.value and self.type == other.type and self.line_num == other.line_num


class Tokenizer:
    def __init__(self, source: str) -> None:
        self.source: str = source
        self.index: int = 0
        self.line_num: int = 1
        self.line_col: int = 1

        # If self.current is None, the tokenizer should return an EOF token. When that happens, this variable will be
        # set to true, and the next time .next_token is called, a StopIteration exception is raised.
        self.is_end_of_stream: bool = False

    def __iter__(self) -> "Tokenizer":
        return self

    def __next__(self) -> Token:
        if self.is_end_of_stream:
            raise StopIteration

        if self.current is None:
            self.is_end_of_stream = True

        return self.next_token()

    def next_token(self) -> Token:
        self.skip_whitespace()

        if self.current is None:
            return Token("", EOF, self.line_num)

        elif self.is_digit():
            number: str = self.read_number()
            token_type: str = FLOAT if "." in number else INTEGER
            return Token(number, token_type, self.line_num)

        elif self.is_identifier():
            letters: str = self.read_identifier()

            # Any string that is not a keyword is an identifier (variable, function, etc.)
            token_type = tokens_dict.get(letters, IDENTIFIER)
            return Token(letters, token_type, self.line_num)

        else:
            # Find all tokens starting with the current character. Sort by the length of each token in descending
            # order. This ensures shorter tokens with similar characters to longer tokens are not mistakenly
            # matched (for example, '==' might get confused as two '=' if the smaller tokens are ordered first).
            #
            # l = literal
            # t = type
            key_sort: Callable[[Tuple[str, str, int]], int] = lambda data: data[2]
            matching_tokens: list[Tuple[str, str, int]] = sorted(
                [(l, t, len(l)) for l, t in tokens_dict.items() if l.startswith(self.current)],
                key=key_sort, reverse=True
            )

            for literal, _type, literal_len in matching_tokens:
                matching_source: str = self.source[self.index:self.index + literal_len]
                if matching_source == literal:
                    # Advance past the number of characters in the matching literal string
                    for _ in range(literal_len):
                        self.advance()
                    return Token(literal, _type, self.line_num)

            # If no tokens are found, then assume an invalid character
            raise utils.language_error(self.line_num, f"invalid character {repr(self.current)}")

    @property
    def current(self) -> Optional[str]:
        return self.source[self.index] if self.index < len(self.source) else None

    @property
    def next_char(self) -> Optional[str]:
        next_char_index: int = self.index + 1
        return self.source[next_char_index] if next_char_index < len(self.source) else None

    def advance(self) -> None:
        self.index += 1

    def skip_whitespace(self) -> None:
        while self.current is not None and self.current.isspace():
            if self.current == "\n":
                self.line_num += 1

            self.advance()

    def is_string(self) -> bool:
        return self.current is not None and self.current == get_token_literal("DOUBLE_QUOTE")

    def is_identifier(self, include_nums: bool = False) -> bool:
        """Determine if a character is valid for an identifier (a-z, A-Z, 0-9, _)

        :param include_nums: Set if digits are allowed in the valid identifier characters. Identifiers can't start
        with numbers, but can include numbers.
        :return:
        """
        valid_chars: str = string.ascii_letters + "_"
        if include_nums:
            valid_chars += string.digits

        return self.current is not None and self.current in valid_chars

    def is_digit(self) -> bool:
        return self.current is not None and (self.current.isdigit() or self.current == get_token_literal(PERIOD))

    def read_number(self) -> str:
        pos: int = self.index
        while self.is_digit():
            self.advance()
        return self.source[pos:self.index]

    def read_string(self) -> str:
        pos: int = self.index
        while not self.is_string():
            self.advance()
        return self.source[pos:self.index]

    def read_identifier(self) -> str:
        pos: int = self.index
        while self.is_identifier(include_nums=True):
            self.advance()
        return self.source[pos:self.index]
