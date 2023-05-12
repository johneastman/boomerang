from typing import Optional

from interpreter.parser_.ast_objects import Expression


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
        # For variables, check the current environment. If it does not exist, check the parent environment.
        # Continue doing this until there are no more parent environments. If the variable does not exist in all
        # scopes, it does not exist anywhere in the code.
        env: Optional[Environment] = self
        while env is not None:
            variable_value = env.variables.get(key, None)
            if variable_value is not None:
                return variable_value
            env = env.parent_env

        return None
