from tokenizer import Tokenizer
from _parser import Parser
from evaluator import Evaluator
from my_ast import MyAST

PROMPT = ">> "


def get_source(filepath):
    with open(filepath, "r") as file:
        return file.read()


def repl():
    while True:
        _input = input(PROMPT)

        if _input.lower() == "exit":
            break
        else:
            try:
                t = Tokenizer(_input)
                tokens = t.tokenize()

                p = Parser(tokens)
                ast = p.parse()

                e = Evaluator(ast)
                result = e.evaluate()
                print(result)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    source = get_source("language.txt")
    t = Tokenizer(source)
    tokens = t.tokenize()

    p = Parser(tokens)
    ast = p.parse()

    e = Evaluator(ast)
    results = e.evaluate()
    print(results)

    # ast_obj = MyAST(ast)
    # ast_obj.visualize()
