from tokens.tokenizer import Token
import yaml


def read_yaml_file(path):
    with open(path, "r") as file:
        return yaml.safe_load(file)


def raise_error(line_num: int, description: str) -> None:
    raise Exception(f"Error at line {line_num}: {description}")


class ReturnException(Exception):
    def __init__(self, token: Token) -> None:
        self.token = token
