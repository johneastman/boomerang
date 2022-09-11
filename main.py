import argparse

# Local packages
import typing

from tokens.tokenizer import Tokenizer
from _parser._parser import Parser, Base
from _parser.ast_objects import NoReturn
from evaluator.evaluator import Evaluator
from evaluator._environment import Environment
# from utils.ast_visualizer import ASTVisualizer
from utils.utils import LanguageRuntimeException


def get_source(filepath: str) -> str:
    with open(filepath, "r") as file:
        return file.read()


def evaluate(source: str, environment: Environment, visualize: bool = False) -> typing.Optional[typing.List[Base]]:
    try:
        t = Tokenizer(source)

        p = Parser(t)
        ast = p.parse()

        # if visualize:
        #     ASTVisualizer(ast).visualize()

        e = Evaluator(ast, environment)
        return e.evaluate()
    except LanguageRuntimeException as e:
        print(str(e))

    return None  # needed to solve mypy error: Missing return statement


def repl(prompt: str = ">>") -> None:
    env = Environment()
    while True:
        _input = input(f"{prompt} ")

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
    parser = argparse.ArgumentParser(description="Boomerang Interpreter")

    path_flags = ("--path", "-p")
    parser.add_argument(*path_flags, help="Path to Boomerang file", type=str, required=False)

    repl_flags = ("--repl", "-r")
    parser.add_argument(*repl_flags, "-r", help="Run Boomerang repl (Read-Evaluate-Print Loop)", action="store_true")

    args = parser.parse_args()
    repl_var = args.repl
    path_var = args.path

    if repl_var and path_var:
        parser.error(f"{path_flags[0]} and {repl_flags[0]} cannot be given together")

    if args.repl:
        repl()
    elif args.path:
        evaluate(get_source(args.path), Environment())
