class Token:

    def __init__(self, line_num: int, value: str, _type: str) -> None:
        self.line_num = line_num
        self.value = value
        self.type = _type

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(line_num={self.line_num}, value={repr(self.value)}, type={self.type})"

    def __eq__(self, other: object) -> bool:
        """Check if token objects are equal.

        NOTE: this method is implemented for testing purposes only
        """
        if not isinstance(other, Token):
            return False
        return self.value == other.value and self.type == other.type and self.line_num == other.line_num
