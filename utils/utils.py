import yaml
import typing


class LanguageRuntimeException(Exception):
    pass


def read_yaml_file(path: str) -> typing.Any:
    with open(path, "r") as file:
        return yaml.safe_load(file)


def language_error(line_num: int, description: str) -> LanguageRuntimeException:
    return LanguageRuntimeException(f"Error at line {line_num}: {description}")


def raise_unexpected_end_of_file() -> LanguageRuntimeException:
    return LanguageRuntimeException("Unexpected end of file")


def get(dictionary: dict[str, typing.Any], key_path: str) -> typing.Any:
    value = dictionary
    for key in key_path.split("."):
        value = value[key]
    return value
