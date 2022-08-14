from tokens.tokenizer import Token


class TestToken(Token):
    """Test Token object

    Same as Token object, but equals method checks line_num, which allows for more easily testing that Token objects
    are actually equal
    """
    def __eq__(self, other):
        if not isinstance(other, TestToken) and not isinstance(other, Token):
            return False
        return self.value == other.value and self.type == other.type and self.line_num == other.line_num

    def __hash__(self):
        return super().__hash__()
