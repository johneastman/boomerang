from interpreter.parser_.ast_objects import Expression, When
from interpreter.parser_.parser_ import Parser
from interpreter.tokens.tokenizer import Tokenizer
from interpreter.tokens.token_queue import TokenQueue


def create_when(line_num: int, when_expressions: list[tuple[str, Expression, Expression]]) -> tuple[str, When]:
    conditions_and_expressions = []

    source = "when:"
    for result in when_expressions:
        expr_src, left, right = result
        source += f"\n    {expr_src}"
        conditions_and_expressions.append((left, right))

    return source, When(line_num, conditions_and_expressions)


def parser(source: str) -> Parser:
    tokenizer = Tokenizer(source)
    tokens = TokenQueue(tokenizer)
    return Parser(tokens)
