import argparse
import os

from utils.utils import get_source
from main_utils import evaluate, visualize_ast
from interpreter.evaluator.environment_ import Environment
from utils.utils import Platform, BOOMERANG_PLATFORM


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


if __name__ == "__main__":
    os.environ[BOOMERANG_PLATFORM] = Platform.CMD.name

    parser = argparse.ArgumentParser(description="Boomerang Interpreter")

    parser.add_argument("path", nargs="?", default=None)

    visualize_flags = ("--visualize", "-v")
    parser.add_argument(
        *visualize_flags, help="Create an Abstract Syntax Tree visualization", action="store_true")

    args = parser.parse_args()

    path_var = args.path
    visualize_path = args.visualize

    # If the user provides a path, run the interpreter with the content of that file
    if path_var:
        source = get_source(path_var)

        # Create an AST visualization if the -v flag exists
        if visualize_path:
            pdf_data: bytes = visualize_ast(source)
            with open("graph.pdf", "wb") as file:
                file.write(pdf_data)

        # Otherwise, just evaluate the code
        else:
            _, output = evaluate(source, Environment())

            if len(output) > 0:
                print("\n".join(output))
    else:
        # Run the REPL if no file path is provided
        repl()
