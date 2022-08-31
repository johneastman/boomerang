import yaml
import typing
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _parser.ast_objects import Base


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
    def __init__(self, base_object: "Base") -> None:
        """Initializer

        NOTE: Can't define "token: Token" due to import error

        This allows us to retrieve the token returned by the return statement.

        :param token: The evaluated value of the return statement
        """
        self.base_object = base_object


def read_yaml_file(path: str) -> typing.Any:
    with open(path, "r") as file:
        return yaml.safe_load(file)


def raise_error(line_num: int, description: str) -> typing.NoReturn:
    raise LanguageRuntimeException(f"Error at line {line_num}: {description}")


def get(dictionary: dict[str, typing.Any], key_path: str) -> typing.Any:
    value = dictionary
    for key in key_path.split("."):
        value = value[key]
    return value
