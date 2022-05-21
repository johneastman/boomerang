"""
Token Types
"""
ILLEGAL = "ILLEGAL"
EOF = "EOF"

IDENT = "IDENT"
INT = "INT"

# Operators
ASSIGN = "ASSIGN"
PLUS = "PLUS"
MINUS = "MINUS"
BANG = "BANG"
ASTERISK = "ASTERISK"
SLASH = "SLASH"
LT = "LESS_THAN"  # less than
GT = "GREATER_THAN"  # greater than
EQ = "EQUAL"
NOT_EQ = "NOT_EQUAL"

COMMA = "COMMA"
SEMICOLON = "SEMICOLON"
LPAREN = "LEFT_PAREN"
RPAREN = "RIGHT_PAREN"
LBRACE = "LEFT_BRACE"
RBRACE = "RIGHT_BRACE"

# Keywords
FUNCTION = "FUNCTION"
LET = "LET"
TRUE = "TRUE"
FALSE = "FALSE"
IF = "IF"
ELSE = "ELSE"
RETURN = "RETURN"

keywords = {
    "fn": FUNCTION,
    "let": LET,
    "true": TRUE,
    "false": FALSE,
    "if": IF,
    "else": ELSE,
    "return": RETURN
}

single_char_tokens = {
    "+": PLUS,
    "-": MINUS,
    "*": ASTERISK,
    "/": SLASH,
    ">": GT,
    "<": LT,
    "=": ASSIGN,
    "!": BANG,
    "(": LPAREN,
    ")": RPAREN,
    "{": LBRACE,
    "}": RBRACE,
    ";": SEMICOLON,
    ",": COMMA
}


def keyword_lookup(keyword):
    return keywords.get(keyword, IDENT)


def single_char_lookup(char):
    return single_char_tokens.get(char, None)


class Token:
    def __init__(self, _type, literal):
        self.type = _type
        self.literal = literal
