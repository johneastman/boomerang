from tokens.tokenizer import Tokenizer, Token
from tokens.tokens import get_token_literal, get_token_type
from utils import utils


class TokenQueue:
    def __init__(self, tokenizer: Tokenizer) -> None:
        self.tokenizer = tokenizer

        # The peek queue exists because sometimes we want to see what the next token is without actually retrieving it.
        # 'next(self.tokenizer)' will retrieve the next token, but 'peek' will take that result and add it to this
        # queue. Subsequent calls to 'peek' and 'next' will check this queue before calling 'next(self.tokenizer)',
        # ensuring tokens are retrieved in the correct order.
        self.peek_queue: list[Token] = []

        # NOTE: 'self._next' needs to be called AFTER 'self.peek_queue' is instantiated.
        self.current = self._next()

    def next(self) -> None:
        self.current = self._next()

    def _next(self) -> Token:
        if len(self.peek_queue) > 0:
            return self.peek_queue.pop()
        else:
            try:
                return next(self.tokenizer)
            except StopIteration:
                utils.raise_unexpected_end_of_file()

    def peek(self) -> Token:
        if len(self.peek_queue) > 0:
            # Because we just want to see what the next token is without consuming it, return the last value in the
            # queue without calling .pop()
            return self.peek_queue[-1]

        try:
            token = next(self.tokenizer)
            self.peek_queue.append(token)
            return token
        except StopIteration:
            utils.raise_unexpected_end_of_file()

    def add(self, new_token_label: str) -> None:
        # To insert a token into the token stream, add the current token to the peek queue, and then update
        # self.current to the new token
        self.peek_queue.append(self.current)

        semicolon_literal = get_token_literal(new_token_label)
        semicolon_type = get_token_type(new_token_label)

        self.current = Token(semicolon_literal, semicolon_type, self.current.line_num)
