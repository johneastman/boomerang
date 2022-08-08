import tokens.tokenizer as tokenizer
import utils
from tokens.tokens import EOF, SEMICOLON, PLUS


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
        if current is None:
            raise Exception(f"from {self.__class__.__name__}.current: token is None")
        return current

    def advance(self, amount=1) -> None:
        self.index += amount

    def parse(self):
        ast = []
        while self.current is not None and self.current.type != EOF:
            result = self._parse()
            ast.append(result)
            self.is_expected_token(SEMICOLON)
            self.advance()
        return ast

    def _parse(self, precedence="statements"):

        if precedence == "factors":
            return self.current

        precedence_data = self.get_precedence(precedence)

        for pd in precedence_data:
            object_name = pd["name"]
            tokens = pd["tokens"]

            failed = self.do_tokens_match(tokens)
            if not failed:
                values = []
                for token in tokens:
                    _type, required = token["type"], token["required"]

                    value = self.current.value
                    if _type in self.precedences:
                        value = self._parse(precedence=_type).value

                    if required:
                        values.append(value)

                    self.advance()

                return {object_name: values}

    def get_precedence(self, precedence="statements"):
        return self.data["program"][precedence]
        # TODO: Error handling when token is not found

    def is_expected_token(self, expected_token_type):
        if self.current.type != expected_token_type:
            utils.raise_error(
                self.current.line_num,
                f"Expected {expected_token_type}, got {self.current.type} ('{self.current.value}')")

    def do_tokens_match(self, expected_tokens):
        actual_tokens = [token for token in self.tokens[self.index:self.index + len(tokens)]]

        for expected_token, actual_token in zip(expected_tokens, actual_tokens):
            expected_type = expected_token["type"]

            # Specifying a literal value helps clear up requirements for tokens (e.g., a PrintStatement object
            # is an Identifier token where the literal value is "print", not just any identifier token
            expected_literal = expected_token.get("literal", None)

            if expected_type in self.precedences:
                precedence_data = self.get_precedence("factors")
                types = [t["type"] for pd in precedence_data for t in pd["tokens"]]
                if actual_token.type not in types:
                    return True
            elif  expected_type != actual_token.type or (expected_literal is not None and expected_literal != actual_token.value):
                return True
        return False


if __name__ == "__main__":
    source = "print(1, x);"
    tkn = tokenizer.Tokenizer(source)
    tokens = tkn.tokenize()
    p = Parser2(tokens, "parser.yaml")
    ast = p.parse()
    print(ast)
