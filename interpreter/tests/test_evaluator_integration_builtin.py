import pytest
import interpreter.parser_.ast_objects as o

from interpreter.tests.testing_utils import evaluator_actual_result, assert_expressions_equal


@pytest.mark.parametrize("params, expected_result", [
    (["\"hello, world!\""], o.Output(1, "\"hello, world!\"")),
    (["1"], o.Output(1, "1")),
    (["1", "true", "\"string\""], o.Output(1, "1, true, \"string\"")),
    ([], o.Output(1, "")),
])
def test_print(params, expected_result):
    actual_results = evaluator_actual_result(f"print <- ({params_str(params)});")
    assert_expressions_equal([expected_result], actual_results)


@pytest.mark.parametrize("params, low, high", [
    ([], 0, 1),
    (["5"], 0, 5),
    (["5", "10"], 5, 10),
    (["-5", "5"], -5, 5),
    (["-5", "0"], -5, 0),
    (["-5", "5"], -5, 5),
])
def test_random(params, low, high):
    for _ in range(100):
        ast_results = evaluator_actual_result(f"random <- ({params_str(params)});")
        actual_value = ast_results[0]

        assert type(actual_value) == o.Number
        assert low <= actual_value.value <= high


@pytest.mark.parametrize("params, error_result", [
    (
        ["1", "2", "3"],
        o.Error(
            1,
            "Error at line 1: incorrect number of arguments. Excepts 0, 1, or 2 arguments, but got 3"
        )
    ),
    # With one parameter, range is 0 to end
    (
        ["true"],
        o.Error(
            1,
            "Error at line 1: expected Number for end, got Boolean"
        )
    ),
    (
        ["1", "\"string\""],
        o.Error(
            1,
            "Error at line 1: expected Number for end, got String"
        )
    ),
    (
        ["false", "2"],
        o.Error(
            1,
            "Error at line 1: expected Number for start, got Boolean"
        )
    ),
    (
        ["1.5", "2"],
        o.Error(
            1,
            "Error at line 1: start must be a whole number"
        )
    ),
    (
        ["1", "2.5"],
        o.Error(
            1,
            "Error at line 1: end must be a whole number"
        )
    ),
    (
        ["1", "0"],
        o.Error(
            1,
            "Error at line 1: end (0) must be greater than start (1)"
        )
    ),
])
def test_random_error(params, error_result):
    """Due to the nature of the random function not returning consistent values, error tests had to be
    put in a separate test.
    """
    ast_results = evaluator_actual_result(f"random <- ({params_str(params)});")
    assert ast_results[0] == error_result


@pytest.mark.parametrize("params, length", [
    (
        ["()"],
        o.Number(1, 0)
    ),
    (
        ["(1,)"],
        o.Number(1, 1)
    ),
    (
        ["(1, \"hello, world!\")"],
        o.Number(1, 2)
    ),
    (
        ["(1, true, false)"],
        o.Number(1, 3)
    ),
    (
        ["\"hello, world\""],
        o.Number(1, 12)
    ),
    (
        ["\"hello, world\"", "(1, 2, 3)"],
        o.Error(1, "Error at line 1: expected 1 argument, got 2")
    ),
    (
        ["true"],
        o.Error(1, "Error at line 1: unsupported type Boolean for built-in function len")
    ),
    (
        ["false"],
        o.Error(1, "Error at line 1: unsupported type Boolean for built-in function len")
    ),
    (
        ["1.5"],
        o.Error(1, "Error at line 1: unsupported type Number for built-in function len")
    ),
    (
        ["func a, b: a + b"],
        o.Error(1, "Error at line 1: unsupported type Function for built-in function len")
    ),
])
def test_len(params, length):
    ast_results = evaluator_actual_result(f"len <- ({params_str(params)});")
    assert_expressions_equal([length], ast_results)


@pytest.mark.parametrize("params, expected_result", [
    (
        ["1"],
        o.List(1, [
            o.Number(1, 0)
        ])
    ),
    (
        ["0"],
        o.List(1, [])
    ),
    (
        ["0", "0"],
        o.List(1, [])
    ),
    (
        ["1", "3"],
        o.List(1, [
            o.Number(1, 1),
            o.Number(1, 2),
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
        ])
    ),
    (
        ["3", "1", "-1"],
        o.List(1, [
            o.Number(1, 3),
            o.Number(1, 2),
        ])
    ),
    (
        ["1", "2", ".25"],
        o.List(1, [
            o.Number(1, 1),
            o.Number(1, 1.25),
            o.Number(1, 1.5),
            o.Number(1, 1.75),
        ])
    ),
    (
        ["2", "1", "-.25"],
        o.List(1, [
            o.Number(1, 2),
            o.Number(1, 1.75),
            o.Number(1, 1.5),
            o.Number(1, 1.25),
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
    ast_results = evaluator_actual_result(f"range <- ({params_str(params)});")
    assert_expressions_equal([expected_result], ast_results)


def params_str(params: list[str]) -> str:
    """Take list of parameters and return them as a comma-separated string."""
    return ", ".join(params) + ("," if len(params) == 1 else "")