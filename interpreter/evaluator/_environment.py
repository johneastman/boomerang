from typing import Optional

from interpreter._parser.ast_objects import Expression


class Environment:
    def __init__(self, parent_env: Optional["Environment"] = None) -> None:
        self.variables: dict[str, Expression] = {}

        # The parent environment is the scope above the current scope. New environments are created for functions, so
        # variables defined within a function can't be accessed anywhere in the code. Additionally, this structure
        # allows for using variables/functions in parent scopes (for example, a variable defined outside a function).
        self.parent_env = parent_env

    def set_var(self, key: str, val: Expression) -> None:
        self.variables[key] = val

    def set_vars(self, variables: dict[str, Expression]) -> None:
        self.variables = {**self.variables, **variables}

    def get_var(self, key: str) -> Optional[Expression]:
        return self.variables.get(key, None)
