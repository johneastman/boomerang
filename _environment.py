class Environment:
    def __init__(self, parent_env=None):
        self.variables = {}
        self.functions = {}

        # The parent environment is the scope above the current scope. New environments are created for functions, so
        # variables defined within a function can't be accessed anywhere in the code. Additionally, this structure
        # allows for using variables/functions in parent scopes (for example, a variable defined outside a function).
        self.parent_env = parent_env

    def set_var(self, key, val):
        self.variables[key] = val

    def set_vars(self, vars):
        self.variables = {**self.variables, **vars}

    def get_var(self, key):
        return self.variables.get(key, None)

    def set_func(self, key, val):
        self.functions[key] = val

    def get_func(self, key):
        return self.functions.get(key, None)