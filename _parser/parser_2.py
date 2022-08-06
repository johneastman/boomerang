import tokens.tokenizer as t
import utils


class Parser2:
    def __init__(self, tokens, file_path):
        self.tokens = tokens
        self.index = 0

        self.data = utils.read_yaml_file(file_path)

        # precedences are non-token types (factors, expressions, statements, etc.). These are the keys under "program"
        # in the yaml file
        self.precedences = list(self.data["program"].keys())

    @property
    def current(self):
        current = self.tokens[self.index] if self.index < len(self.tokens) else None
        # if current is None:
        #     raise Exception(f"from {self.__class__.__name__}.current: token is None")
        return current

    def advance(self) -> None:
        self.index += 1

    def parse(self, ast={}, precedence="statements"):

        if precedence == "factors":
            return self.current

        precedence_data = self.get_precedence(precedence)

        for pd in precedence_data:
            object_name = pd["name"]
            tokens = pd["tokens"]

            failed = False
            for expected_token_type, actual_token_type in zip(
                    [t["type"] for t in tokens],
                    [t.type for t in self.tokens[self.index:self.index + len(tokens)]]
            ):
                if expected_token_type in self.precedences:
                    precedence_data = self.get_precedence("factors")
                    types = [t["type"] for pd in precedence_data for t in pd["tokens"]]
                    if actual_token_type not in types:
                        failed = True
                        break
                elif expected_token_type != actual_token_type:
                    failed = True
                    break

            if not failed:
                values = []
                for token in tokens:
                    _type, required = token["type"], token["required"]

                    value = self.parse(ast=ast, precedence=_type) if _type in self.precedences else self.current
                    if required:
                        values.append(value)

                    self.advance()

                ast[object_name] = values
                return ast

        return ast

    def get_precedence(self, precedence="statements"):
        return self.data["program"][precedence]

    def find_precedence(self, precedence_data):
        for pd in precedence_data:
            _type = pd["tokens"][0]["type"]
            if _type == self.current.type:
                return pd["name"], pd["tokens"]

        # TODO: Error handling when token is not found

    def is_expected_token(self, expected_token_type):
        if self.current.type != expected_token_type:
            utils.raise_error(
                self.current.line_num,
                f"Expected {expected_token_type}, got {self.current.type} ('{self.current.value}')")


if __name__ == "__main__":
    source = "1 + 2 + 3;"
    tokenizer = t.Tokenizer(source)
    tokens = tokenizer.tokenize()
    p = Parser2(tokens, "parser.yaml")
    ast = p.parse()
    print(ast)
