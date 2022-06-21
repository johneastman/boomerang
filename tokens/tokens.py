language_tokens = {
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
    "LET": ("let", "LET"),
    "RETURN": ("return", "RETURN"),
    "FUNCTION": ("func", "FUNCTION"),
    "IF": ("if", "IF"),
    "ELSE": ("else", "ELSE"),
    "WHILE": ("while", "WHILE"),
    "TRUE": ("true", "BOOLEAN"),
    "FALSE": ("false", "BOOLEAN"),
    "EOF": ("", "EOF"),
    "NUMBER": ("", "NUMBER"),
    "IDENTIFIER": ("", "IDENTIFIER"),
    "BOOLEAN": ("", "BOOLEAN")
}


def get_keyword_dict():
    return {literal: _type for literal, _type in language_tokens.values()}


def get_token(name):
    token = language_tokens.get(name, None)
    if token is None:
        raise Exception(f"No token for name: {name}")
    return token


def get_token_type(name):
    _, _type = get_token(name)
    return _type


def get_token_literal(name):
    literal, _ = get_token(name)
    return literal


# Symbols
ASSIGN = get_token_type("ASSIGN")
ASSIGN_ADD = get_token_type("ASSIGN_ADD")
ASSIGN_SUB = get_token_type("ASSIGN_SUB")
ASSIGN_MUL = get_token_type("ASSIGN_MUL")
ASSIGN_DIV = get_token_type("ASSIGN_DIV")
PLUS = get_token_type("PLUS")
MINUS = get_token_type("MINUS")
MULTIPLY = get_token_type("MULTIPLY")
DIVIDE = get_token_type("DIVIDE")
SEMICOLON = get_token_type("SEMICOLON")
OPEN_PAREN = get_token_type("OPEN_PAREN")
CLOSED_PAREN = get_token_type("CLOSED_PAREN")
OPEN_CURLY_BRACKET = get_token_type("OPEN_CURLY_BRACKET")
CLOSED_CURLY_BRACKET = get_token_type("CLOSED_CURLY_BRACKET")
COMMA = get_token_type("COMMA")
COMMENT = get_token_type("COMMENT")
BLOCK_COMMENT = get_token_type("BLOCK_COMMENT")

# Comparison/Boolean Operators
EQ = get_token_type("EQ")
NE = get_token_type("NE")
GE = get_token_type("GE")
LE = get_token_type("LE")
GT = get_token_type("GT")
LT = get_token_type("LT")
BANG = get_token_type("BANG")
AND = get_token_type("AND")
OR = get_token_type("OR")

# Keywords
LET = get_token_type("LET")
RETURN = get_token_type("RETURN")
FUNCTION = get_token_type("FUNCTION")
IF = get_token_type("IF")
ELSE = get_token_type("ELSE")
WHILE = get_token_type("WHILE")

# Misc
EOF = get_token_type("EOF")  # End of File
NUMBER = get_token_type("NUMBER")
BOOLEAN = get_token_type("BOOLEAN")
IDENTIFIER = get_token_type("IDENTIFIER")
