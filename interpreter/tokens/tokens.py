from typing import Tuple
import os

from interpreter.utils import utils

TOKENS_FILE_PATH = os.path.join(os.path.dirname(__file__), "tokens.yaml")


def load_tokens(key_path: str) -> dict[str, Tuple[str, str]]:
    content = utils.read_yaml_file(TOKENS_FILE_PATH)

    token_data = utils.get(content, key_path)

    tokens: dict[str, Tuple[str, str]] = {}
    for token in token_data:
        name = token["name"]
        literal = token["literal"]
        _type = token["type"]

        tokens[name] = (literal, _type)

    return tokens


KEYWORDS = load_tokens("tokens.keywords")
SYMBOLS = load_tokens("tokens.symbols")
DATA_TYPES = load_tokens("tokens.data_types")


language_tokens: dict[str, Tuple[str, str]] = {**KEYWORDS, **SYMBOLS, **DATA_TYPES}


def get_keyword_dict(token_dicts: list[dict[str, Tuple[str, str]]]) -> dict[str, str]:
    combined_tokens: dict[str, Tuple[str, str]] = {}
    for token_dict in token_dicts:
        combined_tokens.update(token_dict)

    return {literal: _type for literal, _type in combined_tokens.values()}


def get_token(name: str) -> Tuple[str, str]:
    token = language_tokens.get(name, None)
    if token is None:
        raise Exception(f"No token for name: {name}")
    return token


def get_token_type(name: str) -> str:
    _, _type = get_token(name)
    return _type


def get_token_literal(name: str) -> str:
    literal, _ = get_token(name)
    return literal


# Symbols
ASSIGN: str = get_token_type("ASSIGN")
PLUS: str = get_token_type("PLUS")
MINUS: str = get_token_type("MINUS")
MULTIPLY: str = get_token_type("MULTIPLY")
DIVIDE: str = get_token_type("DIVIDE")
SEMICOLON: str = get_token_type("SEMICOLON")
COLON: str = get_token_type("COLON")
OPEN_PAREN: str = get_token_type("OPEN_PAREN")
CLOSED_PAREN: str = get_token_type("CLOSED_PAREN")
PERIOD: str = get_token_type("PERIOD")
COMMA: str = get_token_type("COMMA")
POINTER: str = get_token_type("POINTER")
DEC: str = get_token_type("DEC")
INC: str = get_token_type("INC")

# Comparison/Boolean Operators
EQ: str = get_token_type("EQ")  # Equal
NE: str = get_token_type("NE")  # Not Equal
GT: str = get_token_type("GT")  # Greater Than
GE: str = get_token_type("GE")  # Greater Than or Equal
LT: str = get_token_type("LT")  # Less Than
LE: str = get_token_type("LE")  # Less Than or Equal
BANG: str = get_token_type("BANG")
AND: str = get_token_type("AND")
OR: str = get_token_type("OR")
COMMENT: str = get_token_type("COMMENT")

# Keywords
TRUE: str = get_token_type("TRUE")
FALSE: str = get_token_type("FALSE")
FUNCTION: str = get_token_type("FUNCTION")
WHEN: str = get_token_type("WHEN")
IS: str = get_token_type("IS")
ELSE: str = get_token_type("ELSE")

# Misc
EOF: str = get_token_type("EOF")  # End of File
IDENTIFIER: str = get_token_type("IDENTIFIER")

# Data Types
NUMBER: str = get_token_type("NUMBER")
STRING: str = get_token_type("STRING")
BOOLEAN: str = get_token_type("BOOLEAN")
