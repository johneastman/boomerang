from tokens.tokenizer import Token


def raise_error(line_num, description):
    raise Exception(f"Error at line {line_num}: {description}")


class ReturnException(Exception):
    def __init__(self, token: Token):
        self.token = token
