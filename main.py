import argparse
import typing

from interpreter.parser_.parser_ import Expression, Error, SEND
from interpreter.parser_.ast_objects import BinaryExpression, BuiltinFunction, List, Output
from interpreter.tokens.tokenizer import Tokenizer
from interpreter.tokens.token_queue import TokenQueue
from interpreter.parser_.parser_ import Parser
from interpreter.evaluator.evaluator import Evaluator
from interpreter.evaluator.environment_ import Environment
from interpreter.tokens.tokens import POINTER, get_token_literal, get_token_type
from interpreter.utils.ast_visualizer import ASTVisualizer
from interpreter.utils.utils import LanguageRuntimeException


def get_source(filepath: str) -> str:
    with open(filepath, "r") as file:
        return file.read()


def evaluate(source: str, environment: Environment) -> list[Expression]:
    try:
        t = Tokenizer(source)
        tokens = TokenQueue(t)

        p = Parser(tokens)
        ast = p.parse()

        e = Evaluator(ast, environment)
        return e.evaluate()
    except LanguageRuntimeException as e:
        return [Error(e.line_num, str(e))]


def visualize_ast(source: str) -> bytes:
    t = Tokenizer(source)
    tq = TokenQueue(t)
    p = Parser(tq)
    ast = p.parse()

    ast_v = ASTVisualizer(ast)

    return ast_v.visualize()


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
                for expression in evaluated_expressions:
                    print(str(expression))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Boomerang Interpreter")

    path_flags = ("--path", "-p")
    parser.add_argument(*path_flags, help="Path to Boomerang file", type=str, required=False)

    repl_flags = ("--repl", "-r")
    parser.add_argument(*repl_flags, help="Run Boomerang repl (Read-Evaluate-Print Loop)", action="store_true")

    visualize_flags = ("--visualize", "-v")
    parser.add_argument(*visualize_flags, help="Create an Abstract Syntax Tree visualization", action="store_true")

    args = parser.parse_args()
    repl_var = args.repl
    path_var = args.path
    visualize_path = args.visualize

    if repl_var and path_var:
        parser.error(f"{path_flags[0]} and {repl_flags[0]} cannot be given together")

    if args.repl:
        repl()
    elif args.path:
        source = get_source(args.path)
        results = evaluate(source, Environment())
        for result in results:
            if isinstance(result, Output) or isinstance(result, Error):
                print(result)

        if visualize_path:
            visualize_ast(source)
