import pytest

from . import testing_utils
from ..parser_.ast_objects import Assignment, Number


def test_set_expression():
    p = testing_utils.parser("variable = 1;")

    actual_assign_ast = p.assign()

    expected_assign_ast = Assignment(
        1,
        "variable",
        Number(1, 1)
    )

    assert actual_assign_ast == expected_assign_ast


string_repr_data = [
    (1.0, "1", True),
    (1.45, "1.45", False)
]


@pytest.mark.parametrize("value, str_repr, is_whole_num", string_repr_data)
def test_number_string(value, str_repr, is_whole_num):
    n = Number(1, value)
    assert str(n) == str_repr
    assert n.is_whole_number() == is_whole_num
