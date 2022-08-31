from typing import Optional
from _parser.ast_objects import Base, AssignFunction


class Environment:
    def __init__(self, parent_env: Optional["Environment"] = None) -> None:
        self.variables: dict[str, Base] = {}
        self.functions: dict[str, AssignFunction] = {}

        # The parent environment is the scope above the current scope. New environments are created for functions, so
        # variables defined within a function can't be accessed anywhere in the code. Additionally, this structure
        # allows for using variables/functions in parent scopes (for example, a variable defined outside a function).
        self.parent_env = parent_env

    def set_var(self, key: str, val: Base) -> None:
        self.variables[key] = val

    def set_vars(self, vars: dict[str, Base]) -> None:
        self.variables = {**self.variables, **vars}

    def get_var(self, key: str) -> Optional[Base]:
        return self.variables.get(key, None)

    def set_func(self, key: str, val: AssignFunction) -> None:
        self.functions[key] = val

    def get_func(self, key: str) -> Optional[AssignFunction]:
        return self.functions.get(key, None)
