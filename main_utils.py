from interpreter.evaluator.environment_ import Environment
from interpreter.evaluator.evaluator import Evaluator
from interpreter.parser_.ast_objects import Error, Expression
from interpreter.parser_.parser_ import Parser
from interpreter.tokens.token_queue import TokenQueue
from interpreter.tokens.tokenizer import Tokenizer
from utils.ast_visualizer import ASTVisualizer
from utils.utils import LanguageRuntimeException


def evaluate(source: str, environment: Environment) -> tuple[list[Expression], list[str]]:
    """Execute code in a file.

    Unlike REPL, this execution style does not use the results of each individual expression.
    """
    try:
        t = Tokenizer(source)
        tokens = TokenQueue(t)

        p = Parser(tokens)
        ast = p.parse()
        return Evaluator(ast, environment).evaluate()

    except LanguageRuntimeException as e:
        # This catch is needed for the parser and tokenizer. Evaluator.evaluate handles these errors on its own.
        error_object = Error(e.line_num, str(e))
        return [str(error_object)], []


def visualize_ast(source: str) -> bytes:
    t = Tokenizer(source)
    tq = TokenQueue(t)
    p = Parser(tq)
    ast = p.parse()
    return ASTVisualizer(ast).visualize()
