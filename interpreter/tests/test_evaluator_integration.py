import pytest

import interpreter._parser.ast_objects as o
from interpreter.tokens.tokenizer import Tokenizer
from interpreter.tokens.token_queue import TokenQueue
from interpreter._parser._parser import Parser
from interpreter.evaluator.evaluator import Evaluator
from interpreter.evaluator._environment import Environment


evaluator_tests = [
    ("1 + 1", [o.create_number("2.0", 1)]),
    ("1 + 2 * 2", [o.create_number("5.0", 1)]),
    ("(1 + 2) * 2", [o.create_number("6.0", 1)]),
    ("x = (1 + 2) * 2;\nx", [o.create_number("6.0", 1), o.create_number("6.0", 2)]),
    ("x = y = z = 2;\nx;\ny;\nz", [
        o.create_number("2", 1),
        o.create_number("2", 2),
        o.create_number("2", 3),
        o.create_number("2", 4)
    ]),
    ("4 / 2", [o.create_number("2.0", 1)]),
    ("7 / 2", [o.create_number("3.5", 1)]),
    ("1 + 1 * 2 + 3 / 4", [o.create_number("3.75", 1)])
]


@pytest.mark.parametrize("source,expected_results", evaluator_tests)
def test_evaluator(source, expected_results):
    actual_results = actual_result(f"{source};")
    assert expected_results == actual_results


valid_unary_operations_tests = [
    ("-1", [
        o.create_number("-1.0", 1)
     ]),
    ("+1", [
        o.create_number("1.0", 1)
    ]),
    ("+-1", [
        o.create_number("1.0", 1)
    ]),
    ("--6", [
        o.create_number("6.0", 1)
    ]),
    ("-5.258", [
        o.create_number("-5.258", 1)
    ]),
    ("5.258", [
        o.create_number("5.258", 1)
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
