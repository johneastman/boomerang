class Environment:
    def __init__(self, parent_env):
        self.variables = {}
        self.functions = {}
        self.parent_env = parent_env

    def set_var(self, key, val):
        self.variables[key] = val

    def get_var(self, key):
        return self.variables.get(key, None)

    def set_func(self, key, val):
        self.functions[key] = val

    def get_func(self, key):
        return self.functions.get(key, None)
