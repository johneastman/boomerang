from typing import Tuple
import yaml
import os

TOKENS_FILE_PATH = f"{os.path.dirname(__file__)}/tokens.yaml"


def load_tokens():
    with open(TOKENS_FILE_PATH, "r") as file:
        content = yaml.safe_load(file)

    tokens: dict[str, Tuple[str, str]] = {}
    for token in content["tokens"]:
        name = token["name"]
        literal = token["literal"]
        _type = token["type"]

        tokens[name] = (literal, _type)

    return tokens


language_tokens: dict[str, Tuple[str, str]] = load_tokens()


def get_keyword_dict() -> dict[str, str]:
    return {literal: _type for literal, _type in language_tokens.values()}


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
ASSIGN_ADD: str = get_token_type("ASSIGN_ADD")
ASSIGN_SUB: str = get_token_type("ASSIGN_SUB")
ASSIGN_MUL: str = get_token_type("ASSIGN_MUL")
ASSIGN_DIV: str = get_token_type("ASSIGN_DIV")
PLUS: str = get_token_type("PLUS")
MINUS: str = get_token_type("MINUS")
MULTIPLY: str = get_token_type("MULTIPLY")
DIVIDE: str = get_token_type("DIVIDE")
SEMICOLON: str = get_token_type("SEMICOLON")
OPEN_PAREN: str = get_token_type("OPEN_PAREN")
CLOSED_PAREN: str = get_token_type("CLOSED_PAREN")
OPEN_CURLY_BRACKET: str = get_token_type("OPEN_CURLY_BRACKET")
CLOSED_CURLY_BRACKET: str = get_token_type("CLOSED_CURLY_BRACKET")
COMMA: str = get_token_type("COMMA")
COMMENT: str = get_token_type("COMMENT")
BLOCK_COMMENT: str = get_token_type("BLOCK_COMMENT")
DOUBLE_QUOTE: str = get_token_type("DOUBLE_QUOTE")
COLON: str = get_token_type("COLON")
OPEN_BRACKET: str = get_token_type("OPEN_BRACKET")
CLOSED_BRACKET: str = get_token_type("CLOSED_BRACKET")

# Comparison/Boolean Operators
EQ: str = get_token_type("EQ")
NE: str = get_token_type("NE")
GE: str = get_token_type("GE")
LE: str = get_token_type("LE")
GT: str = get_token_type("GT")
LT: str = get_token_type("LT")
BANG: str = get_token_type("BANG")
AND: str = get_token_type("AND")
OR: str = get_token_type("OR")

# Keywords
RETURN: str = get_token_type("RETURN")
FUNCTION: str = get_token_type("FUNCTION")
IF: str = get_token_type("IF")
ELSE: str = get_token_type("ELSE")
WHILE: str = get_token_type("WHILE")
LET: str = get_token_type("LET")

# Misc
EOF: str = get_token_type("EOF")  # End of File
IDENTIFIER: str = get_token_type("IDENTIFIER")

# Data Types
STRING: str = get_token_type("STRING")
INTEGER: str = get_token_type("INTEGER")
BOOLEAN: str = get_token_type("BOOLEAN")
FLOAT: str = get_token_type("FLOAT")
DICTIONARY: str = get_token_type("DICTIONARY")
