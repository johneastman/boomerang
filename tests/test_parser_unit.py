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
