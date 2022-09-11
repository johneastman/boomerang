from _parser._parser import Parser
from tokens.tokenizer import Tokenizer
from tokens.token_queue import TokenQueue


def parser(source: str) -> Parser:
    tokenizer = Tokenizer(source)
    tokens = TokenQueue(tokenizer)
    return Parser(tokens)
