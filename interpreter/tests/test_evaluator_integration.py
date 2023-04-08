import pytest

import interpreter._parser.ast_objects as o
from interpreter.tokens.tokenizer import Tokenizer
from interpreter.tokens.token_queue import TokenQueue
from interpreter._parser._parser import Parser
from interpreter.evaluator.evaluator import Evaluator
from interpreter.evaluator._environment import Environment


evaluator_tests = [
    ("1 + 1", [o.Number(1, 2)]),
    ("1 + 2 * 2", [o.Number(1, 5)]),
    ("(1 + 2) * 2", [o.Number(1, 6)]),
    ("x = (1 + 2) * 2;\nx", [o.Number(1, 6), o.Number(2, 6)]),
    ("x = y = z = 2;\nx;\ny;\nz", [
        o.Number(1, 2),
        o.Number(2, 2),
        o.Number(3, 2),
        o.Number(4, 2)
    ]),
    ("4 / 2", [o.Number(1, 2)]),
    ("7 / 2", [o.Number(1, 3.5)]),
    ("1 + 1 * 2 + 3 / 4", [o.Number(1, 3.75)]),
    ("\"hello world!\"",  [o.String(1, "hello world!")]),
]


@pytest.mark.parametrize("source,expected_results", evaluator_tests)
def test_evaluator(source, expected_results):
    actual_results = actual_result(f"{source};")
    assert expected_results == actual_results


valid_unary_operations_tests = [
    ("-1", [
        o.Number(1, -1)
     ]),
    ("+1", [
        o.Number(1, 1)
    ]),
    ("+-1", [
        o.Number(1, 1)
    ]),
    ("--6", [
        o.Number(1, 6)
    ]),
    ("-5.258", [
        o.Number(1, -5.258)
    ]),
    ("5.258", [
        o.Number(1, 5.258)
    ])
]


@pytest.mark.parametrize("source,expected_results", valid_unary_operations_tests)
def test_valid_unary_operations(source, expected_results):
    actual_results = actual_result(f"{source};")
    assert actual_results == expected_results


def actual_result(source):
    t = Tokenizer(source)
    tokens = TokenQueue(t)

    p = Parser(tokens)
    ast = p.parse()

    e = Evaluator(ast, Environment())
    return e.evaluate()
