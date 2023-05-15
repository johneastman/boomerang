import yaml
import typing
from enum import Enum

from interpreter.tokens.token import Token


Platform = Enum("Platform", ["WEB", "CMD", "TEST"])


class LanguageRuntimeException(Exception):
    def __init__(self, line_num: int, message: str):
        self.line_num = line_num
        super().__init__(message)


def read_yaml_file(path: str) -> typing.Any:
    with open(path, "r") as file:
        return yaml.safe_load(file)


def language_error(line_num: int, description: str) -> LanguageRuntimeException:
    return LanguageRuntimeException(line_num, f"Error at line {line_num}: {description}")


def unexpected_token_error(line_num: int, expected_token: str, actual_token: Token) -> LanguageRuntimeException:
    return language_error(
        line_num,
        f"expected {expected_token}, got {actual_token.type} ('{actual_token.value}')"
    )


def divide_by_zero_error(line_num: int) -> LanguageRuntimeException:
    return language_error(line_num, "cannot divide by zero")


def raise_unexpected_end_of_file(line_num: int) -> LanguageRuntimeException:
    return language_error(line_num, "unexpected end of file")


def get(dictionary: dict[str, typing.Any], key_path: str) -> typing.Any:
    """Find a value in a recursive dictionary structure (i.e., dictionaries within dictionaries).

    key_path is a list of keys in order from the top level to the bottom level. There should be a period
    between each key. For example, if key_path is "a.b.c", this method will first look in the outer-most
    dictionary for the "a" key. Then, the dictionary associated with "a" will be search for the "b" key,
    and finally the dictionary associated with "b" will be search for the "c" key. The value at "c" is
    returned by this function.
    """
    value = dictionary
    for key in key_path.split("."):
        value = value[key]
    return value
