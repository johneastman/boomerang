from tokenizer import Tokenizer
from _parser import Parser
from evaluator import Evaluator
from _environment import Environment
from ast_visualizer import ASTVisualizer

PROMPT = ">> "


def get_source(filepath):
    with open(filepath, "r") as file:
        return file.read()


def evaluate(source, environment, visualize=False):

    t = Tokenizer(source)
    tokens = t.tokenize()

    p = Parser(tokens)
    ast = p.parse()

    if visualize:
        ASTVisualizer(ast).visualize()

    e = Evaluator(ast, environment)
    return e.evaluate()


def repl():
    env = Environment()
    while True:
        _input = input(PROMPT)

        if _input.lower() == "exit":
            break
        else:
            try:
                result = evaluate(_input, env)
                print(result)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    # source = get_source("language.txt")
    # evaluate(source, Environment())
    t = Tokenizer("1 ==1 || 2 != 3;")
    ast = Parser(t.tokenize()).parse()
    print(ast)
