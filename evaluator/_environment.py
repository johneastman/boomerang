from typing import Optional

from _parser.ast_objects import Node


class Environment:
    def __init__(self, parent_env: Optional["Environment"] = None) -> None:
        self.variables: dict[str, Node] = {}

        # The parent environment is the scope above the current scope. New environments are created for functions, so
        # variables defined within a function can't be accessed anywhere in the code. Additionally, this structure
        # allows for using variables/functions in parent scopes (for example, a variable defined outside a function).
        self.parent_env = parent_env

    def set_var(self, key: str, val: Node) -> None:
        self.variables[key] = val

    def set_vars(self, variables: dict[str, Node]) -> None:
        self.variables = {**self.variables, **variables}

    def get_var(self, key: str) -> Optional[Node]:
        return self.variables.get(key, None)
