# from tokenizer import Tokenizer
# import tokens
#
# PROMPT = ">> "
#
# while True:
#     _input = input(PROMPT)
#
#     if _input.lower() == "exit":
#         break
#     else:
#         t = Tokenizer(_input)
#         tok = t.next_token()
#
#         while tok.type != tokens.EOF:
#             print(f"TYPE: {tok.type}, LITERAL: {tok.literal}")
#             tok = t.next_token()
from tokenizer import Tokenizer
from _parser import Parser
from evaluator import Evaluator


def get_source(filepath):
    with open(filepath, "r") as file:
        return file.read()


source = get_source("language.txt")
t = Tokenizer(source)
tokens = t.tokenize()

p = Parser(tokens)
ast = p.parse()
print(ast)

e = Evaluator(ast)
e.evaluate()
