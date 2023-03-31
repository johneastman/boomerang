import pytest

from _parser.ast_objects import *
from tokens.tokenizer import Token
from . import testing_utils


def test_set_statement():
    p = testing_utils.parser("set variable = 1;")

    actual_assign_ast = p.assign()
    expected_assign_ast = SetVariable(
        Identifier("variable", 1),
        Integer(1, 1))
    assert actual_assign_ast == expected_assign_ast


def test_loop():
    p = testing_utils.parser("while i < 10 {\n set i = i + 1; }")
    actual_loop_ast = p.loop()
    expected_loop_ast = Loop(
        BinaryOperation(Identifier("i", 1), Token("<", LT, 1), Integer(10, 1)),
        [
            SetVariable(Identifier("i", 2),
                        BinaryOperation(Identifier("i", 2), Token("+", PLUS, 2), Integer(1, 2)))
        ]
    )

    assert actual_loop_ast == expected_loop_ast
