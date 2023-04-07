from _parser.ast_objects import *
from . import testing_utils


def test_set_statement():
    p = testing_utils.parser("set variable = 1;")

    actual_assign_ast = p.assign()

    expected_assign_ast = create_assignment_statement(
        "variable",
        1,
        create_integer(1, 1)
    )

    assert actual_assign_ast == expected_assign_ast
