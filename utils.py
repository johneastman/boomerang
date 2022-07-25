from tokens.tokenizer import Token


def raise_error(line_num: int, description: str) -> None:
    raise Exception(f"Error at line {line_num}: {description}")


class ReturnException(Exception):
    def __init__(self, token: Token) -> None:
        self.token = token
