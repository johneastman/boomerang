from tokens.tokenizer import Tokenizer
from _parser._parser import Parser
from _parser.ast_objects import NoReturn
from evaluator.evaluator import Evaluator
from evaluator._environment import Environment
from ast_visualizer import ASTVisualizer
from utils import LanguageRuntimeException

PROMPT = ">> "


def get_source(filepath: str):
    with open(filepath, "r") as file:
        return file.read()


def evaluate(source: str, environment: Environment, visualize: bool = False):
    try:
        t = Tokenizer(source)
        tokens = t.tokenize()

        p = Parser(tokens)
        ast = p.parse()

        if visualize:
            ASTVisualizer(ast).visualize()

        e = Evaluator(ast, environment)
        return e.evaluate()
    except LanguageRuntimeException as e:
        print(str(e))


def repl():
    env = Environment()
    while True:
        _input = input(PROMPT)

        if _input.lower() == "exit":
            break
        else:
            evaluated_expressions = evaluate(_input, env)
            # if 'evaluated_expressions' is None, an error likely occurred
            if evaluated_expressions is not None:
                for token in evaluated_expressions:
                    if isinstance(token, NoReturn):
                        # If the statement/expression returns nothing (e.g., if-else, variable assignment, etc.), do not
                        # print anything.
                        continue
                    print(token.value)


if __name__ == "__main__":
    evaluate(get_source("main.ang"), Environment())
