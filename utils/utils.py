import yaml
import typing


class LanguageRuntimeException(Exception):
    def __init__(self, line_num: int, message: str):
        self.line_num = line_num
        super().__init__(message)


def read_yaml_file(path: str) -> typing.Any:
    with open(path, "r") as file:
        return yaml.safe_load(file)


def language_error(line_num: int, description: str) -> LanguageRuntimeException:
    return LanguageRuntimeException(line_num, f"Error at line {line_num}: {description}")


def raise_unexpected_end_of_file(line_num: int) -> LanguageRuntimeException:
    return language_error(line_num, "Unexpected end of file")


def get(dictionary: dict[str, typing.Any], key_path: str) -> typing.Any:
    value = dictionary
    for key in key_path.split("."):
        value = value[key]
    return value
