import pytest

import _parser.ast_objects as o
from tokens.tokenizer import Tokenizer
from tokens.token_queue import TokenQueue
from _parser._parser import Parser
from evaluator.evaluator import Evaluator
from evaluator._environment import Environment
from utils.utils import LanguageRuntimeException


evaluator_tests = [
    ("1 + 1", [o.Integer(2, 1)]),
    ("1 + 2 * 2", [o.Integer(5, 1)]),
    ("(1 + 2) * 2", [o.Integer(6, 1)]),
    ("let x = (1 + 2) * 2;\nx", [o.NoReturn(line_num=1), o.Integer(6, 2)]),
    ("4 / 2", [o.Float(2.0, 1)]),
    ("7 / 2", [o.Float(3.5, 1)]),
    ("1 + 1 * 2 + 3 / 4", [o.Float(3.75, 1)])
]


@pytest.mark.parametrize("source,expected_results", evaluator_tests)
def test_evaluator(source, expected_results):
    actual_results = actual_result(f"{source};")
    assert expected_results == actual_results


valid_unary_operations_tests = [
    ("-1", [
        o.Integer(-1, 1)
     ]),
    ("+1", [
        o.Integer(1, 1)
    ]),
    ("-5.258", [
        o.Float(-5.258, 1)
    ]),
    ("5.258", [
        o.Float(5.258, 1)
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
