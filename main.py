from tokenizer import Tokenizer
import tokens

PROMPT = ">> "

while True:
    _input = input(PROMPT)

    if _input.lower() == "exit":
        break
    else:
        t = Tokenizer(_input)
        tok = t.next_token()

        while tok.type != tokens.EOF:
            print(f"TYPE: {tok.type}, LITERAL: {tok.literal}")
            tok = t.next_token()
