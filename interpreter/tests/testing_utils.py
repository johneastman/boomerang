from interpreter.parser_.ast_objects import Expression, When, Boolean
from interpreter.parser_.parser_ import Parser
from interpreter.tokens.tokenizer import Tokenizer
from interpreter.tokens.token_queue import TokenQueue


def create_when(line_num: int, switch_expression: Expression, case_expressions: list[tuple[str, Expression, Expression]]) -> tuple[str, When]:
    conditions_and_expressions = []

    source = "when"
    if not isinstance(switch_expression, Boolean):
        source += f" {str(switch_expression)}"
    source += ":"

    for result in case_expressions:
        expr_src, left, right = result
        source += f"\n    {expr_src}"
        conditions_and_expressions.append((left, right))

    return source, When(line_num, switch_expression, conditions_and_expressions)


def parser(source: str) -> Parser:
    tokenizer = Tokenizer(source)
    tokens = TokenQueue(tokenizer)
    return Parser(tokens)
