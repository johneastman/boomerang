import argparse

from interpreter.parser_.parser_ import Error
from interpreter.tokens.tokenizer import Tokenizer
from interpreter.tokens.token_queue import TokenQueue
from interpreter.parser_.parser_ import Parser
from interpreter.evaluator.evaluator import Evaluator
from interpreter.evaluator.environment_ import Environment
from interpreter.utils.ast_visualizer import ASTVisualizer
from interpreter.utils.utils import LanguageRuntimeException


def get_source(filepath: str) -> str:
    with open(filepath, "r") as f:
        return f.read()


def evaluate(source: str, environment: Environment) -> list[str]:
    """Execute code in a file.

    Unlike REPL, this execution style does not use the results of each individual expression.
    """
    try:
        t = Tokenizer(source)
        tokens = TokenQueue(t)

        p = Parser(tokens)
        ast = p.parse()
        return Evaluator(ast, environment).evaluate()[1]

    except LanguageRuntimeException as e:
        # This catch is needed for the parser and tokenizer. Evaluator.evaluate handles these errors on its own.
        error_object = Error(e.line_num, str(e))
        return [str(error_object)]


def repl(prompt: str = ">>") -> None:
    """Execute code in REPL/command line.

    Uses both output (e.g., print) and individual expression values.
    """
    env = Environment()
    while True:
        _input = input(f"{prompt} ")

        if _input.lower() == "exit":
            break
        else:
            evaluated_expressions, output = evaluate(_input, env)

            # Display output, if any exists
            if len(output) > 0:
                print("\n".join(output))

            # Display evaluated results
            for expression in evaluated_expressions:
                print(str(expression))


def visualize_ast(source: str) -> bytes:
    t = Tokenizer(source)
    tq = TokenQueue(t)
    p = Parser(tq)
    ast = p.parse()
    return ASTVisualizer(ast).visualize()


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

    if repl_var:
        repl()
    elif path_var:
        source = get_source(path_var)
        output = evaluate(source, Environment())

        if len(output) > 0:
            print("\n".join(output))

        if visualize_path:
            pdf_data: bytes = visualize_ast(source)
            with open("graph.pdf", "wb") as file:
                file.write(pdf_data)
