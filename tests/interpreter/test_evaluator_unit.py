import pytest

from interpreter.parser_ import ast_objects as o
from interpreter.evaluator.evaluator import Evaluator
from interpreter.evaluator.environment_ import Environment
from tests.testing_utils import assert_expression_equal
from utils.utils import LanguageRuntimeException
from interpreter.tokens.tokenizer import Token, get_token_type

evaluator = Evaluator([], Environment())

f = o.Function(
    1,
    [],
    o.InfixExpression(
        1,
        o.Number(1, 1),
        Token(1, "+", get_token_type("PLUS")),
        o.Number(1, 1)
    )
)


class InvalidType(o.Expression):
    def __init__(self, line_num: int):
        super().__init__(line_num)


def test_evaluate_expression_invalid_type():
    invalid_type = InvalidType(1)

    with pytest.raises(Exception) as error:
        evaluator.evaluate_expression(invalid_type)
    assert error.typename == "Exception"
    assert str(error.value) == "Unsupported type: InvalidType"


def test_undefined_variable():
    undefined_variable = o.Identifier(1, "undefined")

    with pytest.raises(LanguageRuntimeException) as error:
        evaluator.evaluate_identifier(undefined_variable)
    assert error.typename == "LanguageRuntimeException"
    assert str(error.value) == f"Error at line 1: undefined variable: {undefined_variable.value}"


@pytest.mark.parametrize("call_params, expected_result", [
    (
        [],
        o.Number(1, 2)
    )
])
def test_evaluate_function_call(call_params, expected_result):
    result = evaluator.evaluate_function_call(o.FunctionCall(1, f, o.List(1, call_params)))
    assert_expression_equal(expected_result, result)


def test_evaluate_function_call_errors():
    with pytest.raises(LanguageRuntimeException) as error:
        evaluator.evaluate_function_call(o.FunctionCall(1, f, o.List(1, [o.Number(1, 1)])))

    assert error.typename == "LanguageRuntimeException"
    assert str(error.value) == f"Error at line 1: incorrect number of arguments. Expected 0 but got 1."
