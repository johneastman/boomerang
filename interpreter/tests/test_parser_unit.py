from . import testing_utils
from .._parser.ast_objects import Assignment, Number


def test_set_statement():
    p = testing_utils.parser("variable = 1;")

    actual_assign_ast = p.assign()

    expected_assign_ast = Assignment(
        1,
        "variable",
        Number(1, 1)
    )

    assert actual_assign_ast == expected_assign_ast
