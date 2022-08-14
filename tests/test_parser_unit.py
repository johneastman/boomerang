import pytest

from _parser._parser import Parser
from _parser.ast_objects import *
from .testing_utils import TestToken


def test_set_statement():
    tokens = [
        TestToken("set", SET, 1),
        TestToken("variable", IDENTIFIER, 1),
        TestToken("=", ASSIGN, 1),
        TestToken("1", INTEGER, 1),
        TestToken(";", SEMICOLON, 1),
    ]

    p = Parser(tokens)
    actual_assign_ast = p.assign()
    expected_assign_ast = SetVariable(
        Identifier(TestToken("variable", IDENTIFIER, 1)),
        Integer(TestToken("1", INTEGER, 1)))
    assert actual_assign_ast == expected_assign_ast


operate_assign_tests = [
    ("+=", ASSIGN_ADD, "+", PLUS),
    ("-=", ASSIGN_SUB, "-", MINUS),
    ("*=", ASSIGN_MUL, "*", MULTIPLY),
    ("/=", ASSIGN_DIV, "/", DIVIDE),
]


@pytest.mark.parametrize("operator_assign_literal, operator_assign_type, operator_literal, operator_type", operate_assign_tests)
def test_set_statement_operate_assign(operator_assign_literal, operator_assign_type, operator_literal, operator_type):
    variable_name = "variable"
    identifier_token = Identifier(TestToken(variable_name, IDENTIFIER, 1))
    tokens = [
        TestToken("set", SET, 1),
        TestToken(variable_name, IDENTIFIER, 1),
        TestToken(operator_assign_literal, operator_assign_type, 1),
        TestToken("1", INTEGER, 1),
        TestToken(";", SEMICOLON, 1),
    ]

    p = Parser(tokens)
    actual_assign_ast = p.assign()
    expected_assign_ast = SetVariable(
        identifier_token,
        BinaryOperation(
            identifier_token,
            TestToken(operator_literal, operator_type, 1),
            Integer(TestToken("1", INTEGER, 1))))

    assert actual_assign_ast == expected_assign_ast
