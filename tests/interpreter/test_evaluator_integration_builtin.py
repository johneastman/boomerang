import pytest
import interpreter.parser_.ast_objects as o

from tests.testing_utils import evaluator_actual_result, assert_expressions_equal


@pytest.mark.parametrize("params, expected_result, expected_output_results", [
    (
        ["\"hello, world!\""],
        o.List(1, [o.String(1, "hello, world!")]),
        ["\"hello, world!\""]
    ),
    (
        ["1"],
        o.List(1, [o.Number(1, 1)]),
        ["1"]
    ),
    (
        ["1", "true", "\"string\""],
        o.List(1, [o.Number(1, 1), o.Boolean(1, True), o.String(1, "string")]),
        ["1, true, \"string\""]
    ),
    (
        [],
        o.List(1, []),
        []
    ),
])
def test_print(params, expected_result, expected_output_results):
    actual_results, output_results = evaluator_actual_result(f"print <- ({params_str(params)});")
    assert output_results == expected_output_results
    assert_expressions_equal([expected_result], actual_results)


@pytest.mark.parametrize("params, is_randint, low, high", [
    # randint
    (["5"], True, 0, 5),
    (["5", "10"], True, 5, 10),
    (["-5", "5"], True, -5, 5),
    (["-5", "0"], True, -5, 0),
    (["-5", "5"], True, -5, 5),

    # randfloat
    ([], False, 0, 1),
    (["5"], False, 0, 5),
    (["5", "10"], False, 5, 10),
    (["-5", "5"], False, -5, 5),
    (["-5", "0"], False, -5, 0),
    (["-5", "5"], False, -5, 5),
    (["0.1", "0.2"], False, 0.1, 0.2),
    (["-0.5", "0.5"], False, -0.5, 0.5),
])
def test_random(params, is_randint, low, high):
    func_name = "randint" if is_randint else "randfloat"
    for _ in range(100):
        ast_results, _ = evaluator_actual_result(f"{func_name} <- ({params_str(params)});")
        actual_value = ast_results[0]

        assert type(actual_value) == o.Number
        assert low <= actual_value.value <= high


@pytest.mark.parametrize("params, error_result", [
    (
        [],
        o.Error(
            1,
            "Error at line 1: incorrect number of arguments. Excepts 1 or 2 arguments, but got 0"
        )
    ),
    (
        ["1", "2", "3"],
        o.Error(
            1,
            "Error at line 1: incorrect number of arguments. Excepts 1 or 2 arguments, but got 3"
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
def test_randint_error(params, error_result):
    """randint only accepts whole (integer) numbers.
    """
    ast_results, _ = evaluator_actual_result(f"randint <- ({params_str(params)});")
    assert ast_results[0] == error_result


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
        ["1", "0"],
        o.Error(
            1,
            "Error at line 1: end (0) must be greater than start (1)"
        )
    ),
])
def test_randfloat_error(params, error_result):
    """randfloat does not have whole-number errors because the function returns a random decimal (float) point value
    between two numbers, both of which can be decimal (floating-point) numbers.
    """
    ast_results, _ = evaluator_actual_result(f"randfloat <- ({params_str(params)});")
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
    ast_results, _ = evaluator_actual_result(f"len <- ({params_str(params)});")
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
    ast_results, _ = evaluator_actual_result(f"range <- ({params_str(params)});")
    assert_expressions_equal([expected_result], ast_results)


@pytest.mark.parametrize("params, expected_result", [
    (
        ["3.14159", "0"],
        o.Number(1, 3)
    ),
    (
        ["3.14159", "1"],
        o.Number(1, 3.1)
    ),
    (
        ["3.14159", "2"],
        o.Number(1, 3.14)
    ),
    (
        ["3.14159", "3"],
        o.Number(1, 3.142)
    ),
    (
        ["3.14159", "4"],
        o.Number(1, 3.1416)
    ),
    (
        ["3.14159", "5"],
        o.Number(1, 3.14159)
    ),
    (
        ["3.14159", "6"],
        o.Number(1, 3.14159)
    ),
    (
        ["3.14159", "7"],
        o.Number(1, 3.14159)
    ),

    # Errors
    (
        [],
        o.Error(1, "Error at line 1: incorrect number of arguments. Excepts 2 arguments, but got 0")
    ),
    (
        ["3.14159"],
        o.Error(1, "Error at line 1: incorrect number of arguments. Excepts 2 arguments, but got 1")
    ),
    (
        ["3.14159", "2", "3"],
        o.Error(1, "Error at line 1: incorrect number of arguments. Excepts 2 arguments, but got 3")
    ),
    (
        ["\"hello\"", "2"],
        o.Error(1, "Error at line 1: expected Number for number, got String")
    ),
    (
        ["3.14159", "true"],
        o.Error(1, "Error at line 1: expected Number for round_to, got Boolean")
    ),
    (
        ["3.14159", "1.5"],
        o.Error(1, "Error at line 1: round_to must be a whole number")
    ),
    (
        ["3.14159", "-1"],
        o.Error(1, "Error at line 1: round_to must be greater than or equal to 0")
    ),
])
def test_round(params, expected_result):
    ast_results, _ = evaluator_actual_result(f"round <- ({params_str(params)});")
    assert_expressions_equal([expected_result], ast_results)


def params_str(params: list[str]) -> str:
    """Take list of parameters and return them as a comma-separated string."""
    return ", ".join(params) + ("," if len(params) == 1 else "")
