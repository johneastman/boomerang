import pytest
import interpreter.parser_.ast_objects as o

from interpreter.tests.testing_utils import evaluator_actual_result, assert_expressions_equal


@pytest.mark.parametrize("source, output_str", [
    ("\"hello, world!\"", "\"hello, world!\""),
    ("1", "1")
])
def test_print(source, output_str):
    actual_results = evaluator_actual_result(f"print <- ({source},);")
    assert_expressions_equal([o.Output(1, output_str)], actual_results)


@pytest.mark.parametrize("low, high, params", [
    (0, 1, ""),
    (0, 5, "5,"),
    (5, 10, "5, 10"),
    (-5, 5, "-5, 5"),
    (-5, 0, "-5, 0"),
    (-5, 5, "-5, 5"),
])
def test_random(low, high, params):
    for _ in range(100):
        ast_results = evaluator_actual_result(f"random <- ({params});")
        actual_value = ast_results[0]

        assert type(actual_value) == o.Number
        assert low <= actual_value.value <= high


@pytest.mark.parametrize("list_, length", [
    ("()", 0),
    ("(1,)", 1),
    ("(1, \"hello, world!\")", 2),
    ("(1, true, false)", 3),
    ("\"hello, world\"", 12)
])
def test_len(list_, length):
    ast_results = evaluator_actual_result(f"len <- ({list_},);")
    assert_expressions_equal([o.Number(1, length)], ast_results)


@pytest.mark.parametrize("params, expected_result", [
    (
        ["1"],
        o.List(1, [
            o.Number(1, 0),
            o.Number(1, 1)
        ])
    ),
    (
        ["0"],
        o.List(1, [
            o.Number(1, 0)
        ])
    ),
    (
        ["0", "0"],
        o.List(1, [
            o.Number(1, 0)
        ])
    ),
    (
        ["1", "3"],
        o.List(1, [
            o.Number(1, 1),
            o.Number(1, 2),
            o.Number(1, 3)
        ])
    ),
    (
        ["0", "10", "2"],
        o.List(1, [
            o.Number(1, 0),
            o.Number(1, 2),
            o.Number(1, 4),
            o.Number(1, 6),
            o.Number(1, 8),
            o.Number(1, 10)
        ])
    ),
    (
        ["3", "1", "-1"],
        o.List(1, [
            o.Number(1, 3),
            o.Number(1, 2),
            o.Number(1, 1)
        ])
    ),
    (
        ["1", "2", ".25"],
        o.List(1, [
            o.Number(1, 1),
            o.Number(1, 1.25),
            o.Number(1, 1.5),
            o.Number(1, 1.75),
            o.Number(1, 2)
        ])
    ),
    (
        ["2", "1", "-.25"],
        o.List(1, [
            o.Number(1, 2),
            o.Number(1, 1.75),
            o.Number(1, 1.5),
            o.Number(1, 1.25),
            o.Number(1, 1),
        ])
    ),

    # Errors
    (
        [],
        o.Error(1, "Error at line 1: incorrect number of arguments. Excepts 1, 2, or 3 arguments, but got 0")
    ),
    (
        ["1", "2", "3", "4"],
        o.Error(1, "Error at line 1: incorrect number of arguments. Excepts 1, 2, or 3 arguments, but got 4")
    ),
    (
        ["0", "0", "0"],
        o.Error(1, "Error at line 1: step cannot be 0")
    ),
    (
        ["\"string\"", "2"],
        o.Error(1, "Error at line 1: expected Number for start, got String")
    ),
    (
        ["1", "\"string\""],
        o.Error(1, "Error at line 1: expected Number for end, got String")
    ),
    (
        ["1", "2", "\"string\""],
        o.Error(1, "Error at line 1: expected Number for step, got String")
    ),
    (
        ["1", "2", "-1"],
        o.Error(1, "Error at line 1: step value must be positive if start value is less than end value")
    ),
    (
        ["2", "1", "1"],
        o.Error(1, "Error at line 1: step value must be negative if start value is greater than end value")
    ),
])
def test_range(params, expected_result):
    params_str = ", ".join(params) + ("," if len(params) == 1 else "")

    ast_results = evaluator_actual_result(f"range <- ({params_str});")
    assert_expressions_equal([expected_result], ast_results)
