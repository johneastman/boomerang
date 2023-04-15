class Token:

    def __init__(self, line_num: int, value: str, _type: str) -> None:
        self.line_num = line_num
        self.value = value
        self.type = _type

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value: {self.value}, type: {self.type}, line_num: {self.line_num})"

    def __eq__(self, other: object) -> bool:
        """Check if token objects are equal."""
        if not isinstance(other, Token):
            return False
        return self.value == other.value and self.type == other.type and self.line_num == other.line_num
