from _parser.ast_objects import *
from . import testing_utils


def test_set_statement():
    p = testing_utils.parser("set variable = 1;")

    actual_assign_ast = p.assign()
    expected_assign_ast = SetVariable(
        Identifier("variable", 1),
        Integer(1, 1))
    assert actual_assign_ast == expected_assign_ast

