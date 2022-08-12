from typing import Optional, Callable, Tuple

from .tokens import *
import string

tokens_dict = get_keyword_dict()


class Token:

    def __init__(self, value: str, _type: str, line_num: int) -> None:
        self.value = value
        self.type = _type
        self.line_num = line_num

    def __str__(self):
        if self.type == STRING:
            return f'"{self.value}"'
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value: {self.value}, type: {self.type}, line_num: {self.line_num})"

    def __eq__(self, other: object) -> bool:
        """Check if token objects are equal

        Note: We do not check the line number to ensure this implementation is compatible with dictionary objects. A
        key may be valid, but not considered matching if the line numbers both key objects do not match.

        For example:
        ```
        dict = {
            Token("a", STRING, 1): Token("1", INTEGER, 1)
        }

        dict[Token("a", STRING, 2)]
        ```
        Even though "a" exists in the dictionary, this code would fail because the line_num for "a" in the
        dictionary is 1 and line_num in the get/index method is 2, which are not equal. Therefore, the code would
        assume this key does not exist (and the line number exists primarily for debugging/error logging).
        """
        if not isinstance(other, Token):
            return False
        return self.value == other.value and self.type == other.type

    def __hash__(self):
        return hash((self.value, self.type))


class Tokenizer:
    def __init__(self, source: str) -> None:
        self.source: str = source
        self.index: int = 0
        self.line_num: int = 1
        self.line_col: int = 1

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []

        while True:
            self.skip_whitespace()

            if self.current is None:
                break

            elif self.is_digit():
                number: str = self.read_number()
                token_type: str = FLOAT if "." in number else INTEGER
                tokens.append(Token(number, token_type, self.line_num))
                continue

            elif self.is_identifier():
                letters: str = self.read_identifier()

                # Any string that is not a keyword is an identifier (variable, function, etc.)
                token_type = tokens_dict.get(letters, IDENTIFIER)
                tokens.append(Token(letters, token_type, self.line_num))
                continue

            elif self.is_string():
                self.advance()
                string_literal: str = self.read_string()
                tokens.append(Token(string_literal, STRING, self.line_num))
                self.advance()

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

                # If no tokens are found, then assume an invalid character
                if len(matching_tokens) == 0:
                    self.raise_invalid_char(self.current)

                for literal, _type, literal_len in matching_tokens:
                    matching_source: str = self.source[self.index:self.index + literal_len]
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

    def raise_invalid_char(self, char: str) -> None:
        raise Exception(f"Invalid character: {char}")

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

    def skip_comment(self) -> None:
        # If a hash symbol is found, skip until the end of the line
        while self.current is not None and self.current != "\n":
            self.advance()
        self.line_num += 1

    def skip_block_comment(self) -> None:
        while True:
            if self.current == "*" and self.next_char == "/":
                # Advance past two characters that close the block comment
                self.advance()
                self.advance()
                break

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
