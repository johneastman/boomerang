from interpreter.tokens.tokenizer import Tokenizer
from interpreter.tokens.token import Token
from interpreter.tokens.tokens import get_token_literal, get_token_type
from utils import utils


class TokenQueue:
    def __init__(self, tokenizer: Tokenizer) -> None:
        self.tokenizer: Tokenizer = tokenizer

        # The peek queue exists because sometimes we want to see what the next token is without actually retrieving it.
        # 'next(self.tokenizer)' will retrieve the next token, but 'peek' will take that result and add it to this
        # queue. Subsequent calls to 'peek' and 'next' will check this queue before calling 'next(self.tokenizer)',
        # ensuring tokens are retrieved in the correct order.
        self.peek_queue: list[Token] = []

        self.current: Token = Token(0, "", "")  # Initializing for mypy

        # NOTE: "self.next" needs to be called AFTER 'self.peek_queue' is instantiated. This method will set a value
        # for "self.current"
        self.next()

    def next(self) -> None:
        if len(self.peek_queue) > 0:
            self.current = self.peek_queue.pop()
        else:
            try:
                self.current = next(self.tokenizer)
            except StopIteration:
                raise utils.raise_unexpected_end_of_file(self.tokenizer.line_num)

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
            raise utils.raise_unexpected_end_of_file(self.tokenizer.line_num)

    def add(self, new_token_label: str) -> None:
        # NOTE: this logic is currently not being used (it was originally used for adding semicolons so the user
        # wouldn't have to add them after block statements). However, I will keep this function defined in case it
        # is needed in the future.
        #
        # To insert a token into the token stream, add the current token to the peek queue, and then update
        # self.current to the new token
        self.peek_queue.append(self.current)

        token_literal = get_token_literal(new_token_label)
        token_type = get_token_type(new_token_label)

        self.current = Token(self.current.line_num, token_literal, token_type)
