from typing import Tuple

language_tokens: dict[str, Tuple[str, str]] = {
    "LET": ("let", "LET"),
    "ASSIGN": ("=", "ASSIGN"),
    "ASSIGN_ADD": ("+=", "ASSIGN_ADD"),
    "ASSIGN_SUB": ("-=", "ASSIGN_SUB"),
    "ASSIGN_MUL": ("*=", "ASSIGN_MUL"),
    "ASSIGN_DIV": ("/=", "ASSIGN_DIV"),
    "PLUS": ("+", "PLUS"),
    "MINUS": ("-", "MINUS"),
    "MULTIPLY": ("*", "MULTIPLY"),
    "DIVIDE": ("/", "DIVIDE"),
    "SEMICOLON": (";", "SEMICOLON"),
    "OPEN_PAREN": ("(", "OPEN_PAREN"),
    "CLOSED_PAREN": (")", "CLOSED_PAREN"),
    "OPEN_CURLY_BRACKET": ("{", "OPEN_CURLY_BRACKET"),
    "CLOSED_CURLY_BRACKET": ("}", "CLOSED_CURLY_BRACKET"),
    "COMMA": (",", "COMMA"),
    "COMMENT": ("#", "COMMENT"),
    "BLOCK_COMMENT": ("/*", "BLOCK_COMMENT"),
    "EQ": ("==", "EQ"),
    "NE": ("!=", "NE"),
    "GE": (">=", "GE"),
    "LE": ("<=", "LE"),
    "GT": (">", "GT"),
    "LT": ("<", "LT"),
    "BANG": ("!", "BANG"),
    "AND": ("&&", "AND"),
    "OR": ("||", "OR"),
    "RETURN": ("return", "RETURN"),
    "FUNCTION": ("func", "FUNCTION"),
    "IF": ("if", "IF"),
    "ELSE": ("else", "ELSE"),
    "WHILE": ("while", "WHILE"),
    "TRUE": ("true", "BOOLEAN"),
    "FALSE": ("false", "BOOLEAN"),
    "DOUBLE_QUOTE": ("\"", "DOUBLE_QUOTE"),
    "EOF": ("", "EOF"),
    "INTEGER": ("", "INTEGER"),
    "IDENTIFIER": ("", "IDENTIFIER"),
    "BOOLEAN": ("", "BOOLEAN"),
    "STRING": ("", "STRING"),
    "FLOAT": ("", "FLOAT"),
    "DICTIONARY": ("", "DICTIONARY"),
    "COLON": (":", "COLON"),
    "OPEN_BRACKET": ("[", "OPEN_BRACKET"),
    "CLOSED_BRACKET": ("]", "CLOSED_BRACKET"),
}


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
