from tokens.tokenizer import Token
import yaml


class LanguageRuntimeException(Exception):
    pass


class ReturnException(Exception):
    """Raised to handle early returns in function calls.

    For example, without this exception, the below method would always return "false":
    ```
    func is_equal(a, b) {
        if a == b {
            return true;
        }
        return false;
    }
    ```
    """
    def __init__(self, token: Token) -> None:
        """Initializer

        This allows us to retrieve the token returned by the return statement.

        :param token: The evaluated value of the return statement
        """
        self.token = token


def read_yaml_file(path: str):
    with open(path, "r") as file:
        return yaml.safe_load(file)


def raise_error(line_num: int, description: str) -> None:
    raise LanguageRuntimeException(f"Error at line {line_num}: {description}")
