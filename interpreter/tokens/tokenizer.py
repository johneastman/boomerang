from typing import Optional, Callable
import string

import utils.utils as utils
from .token import Token
from .tokens import *

tokens_dict = get_keyword_dict([KEYWORDS, SYMBOLS])


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

        return self.next_token()

    def next_token(self) -> Token:
        self.skip_whitespace()
        self.skip_comments()

        if self.current is None:
            self.is_end_of_stream = True
            return Token(self.line_num, "", EOF)

        elif self.is_digit():
            number: str = self.read_number()
            return Token(self.line_num, number, NUMBER)

        elif self.is_identifier():
            letters: str = self.read_identifier()

            # Any string that is not a keyword is an identifier (variable, function, etc.)
            token_type = tokens_dict.get(letters, IDENTIFIER)
            return Token(self.line_num, letters, token_type)

        elif self.is_string():
            self.advance()  # skip starting quote
            string_literal: str = self.read_string()
            self.advance()  # skip ending quote
            return Token(self.line_num, string_literal, STRING)

        return self.get_symbol_token()

    def get_symbol_token(self) -> Token:
        """Find all tokens starting with the current character. Sort by the length of each token in descending
        order. This ensures shorter tokens with similar characters to longer tokens are not mistakenly
        matched (for example, '==' might get confused as two '=' if the smaller tokens are ordered first).

        l = literal
        t = type
        """
        key_sort: Callable[[tuple[str, str, int]], int] = lambda data: data[2]
        matching_tokens: list[tuple[str, str, int]] = sorted(
            # error: Argument 1 to "startswith" of "str" has incompatible type "Optional[str]"; expected
            # "Union[str, Tuple[str, ...]]"
            #
            # Reason for ignoring: The None check in "self.next_token" ensures "self.current" will
            # never be None in this method.
            [(l, t, len(l)) for l, t in tokens_dict.items() if l.startswith(self.current)],  # type: ignore
            key=key_sort, reverse=True
        )

        for literal, _type, literal_len in matching_tokens:
            matching_source: str = self.source[self.index:self.index + literal_len]
            if matching_source == literal:
                # Advance past the number of characters in the matching literal string
                for _ in range(literal_len):
                    self.advance()
                return Token(self.line_num, literal, _type)

        # If no tokens are found, then assume an invalid character
        raise utils.language_error(self.line_num, f"invalid character {repr(self.current)}")

    @property
    def current(self) -> Optional[str]:
        return self.source[self.index] if self.index < len(self.source) else None

    @property
    def peek(self) -> Optional[str]:
        next_char_index: int = self.index + 1
        return self.source[next_char_index] if next_char_index < len(self.source) else None

    def advance(self) -> None:
        self.index += 1

    def skip_whitespace(self) -> None:
        while self.current is not None and self.current.isspace():
            if self.current == "\n":
                self.line_num += 1
            self.advance()

    def skip_comments(self) -> None:
        while self.current == get_token_literal("COMMENT"):
            # If a hash symbol is found, skip until the end of the line
            while self.current is not None and self.current != "\n":
                self.advance()
            self.advance()  # skip end-line char

            self.line_num += 1

            self.skip_whitespace()  # for any whitespace that may be after the comments

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
