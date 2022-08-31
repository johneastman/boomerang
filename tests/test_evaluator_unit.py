import pytest
from collections import namedtuple

from evaluator.evaluator import Evaluator
from evaluator._environment import Environment
from utils.utils import LanguageRuntimeException
from _parser.ast_objects import *


evaluator = Evaluator([], Environment())


def test_evaluate_expression_invalid_type():
    InvalidType = namedtuple("InvalidType", "line_num")
    invalid_type = InvalidType(1)

    with pytest.raises(Exception) as error:
        evaluator.evaluate_expression(invalid_type)
    assert error.typename == "Exception"
    assert str(error.value) == "Unsupported type: InvalidType"


def test_undefined_variable():
    undefined_variable = Identifier("undefined", 1)

    with pytest.raises(LanguageRuntimeException) as error:
        evaluator.evaluate_identifier(undefined_variable)
    assert error.typename == "LanguageRuntimeException"
    assert str(error.value) == f"Error at line 1: undefined variable: {undefined_variable.value}"


to_type_tests = [
    # (String, Integer(1, 1), String("1", 1)),
    # (String, Integer(100, 5), String("100", 5)),
    # (String, Float(3.14159, 15), String("3.14159", 15)),
    # (String, String("hello, world!", 3), String("hello, world!", 3)),
    # (String, Boolean(True, 5), String("true", 5)),
    # (String, Boolean(False, 10), String("false", 10)),
    # (String, Tree(Node(Integer(5, 1), children=[
    #     Node(Float(4.5, 1)),
    #     Node(String("bools", 1), children=[
    #         Node(Boolean(True, 1)),
    #         Node(Boolean(False, 1))
    #     ]),
    #     Node(Integer(100, 1))
    # ]), 1), String("5 => [4.5, \"bools\" => [true, false], 100]", 1)),
    (Integer, Float(5.5, 1), Integer(5, 1))
]


@pytest.mark.parametrize("_type, input_object, expected_object", to_type_tests)
def test_to_type(_type, input_object, expected_object):
    to_string_object = ToType([input_object], input_object.line_num, _type)

    actual_result = evaluator.evaluate_to_type(to_string_object)
    assert actual_result == expected_object


invalid_to_type_tests = [
    (Integer, String("a", 1), "String"),
    (Integer, Boolean(True, 1), "Boolean"),
    (Integer, Boolean(False, 1), "Boolean"),
]


@pytest.mark.parametrize("_type, input_object, object_name", invalid_to_type_tests)
def test_to_type_invalid_types(_type, input_object, object_name):
    to_string_object = ToType([input_object], input_object.line_num, _type)

    with pytest.raises(LanguageRuntimeException) as error:
        evaluator.evaluate_to_type(to_string_object)
    assert error.typename == "LanguageRuntimeException"
    assert str(error.value) == f"Error at line 1: cannot convert {object_name} to Integer"
