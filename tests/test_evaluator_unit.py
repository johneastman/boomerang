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
    (String("hello, world!", 3), String, String("hello, world!", 3)),
    (Float(5.5, 1), Integer, Integer(5, 1)),
    (Integer(10, 1), Float, Float(10.0, 1)),
    (String("1", 1), Integer, Integer(1, 1)),
    (String("3.14159", 1), Float, Float(3.14159, 1)),
    (Float(3.14159, 1), String, String("3.14159", 1)),
    (Integer(1, 1), String, String("1", 1)),
    (Boolean(True, 1), String, String("true", 1)),
    (Boolean(False, 1), String, String("false", 1)),
]


@pytest.mark.parametrize("input_object, _type, expected_object", to_type_tests)
def test_to_type(input_object, _type, expected_object):
    to_string_object = ToType([input_object], input_object.line_num, _type)

    actual_result = evaluator.evaluate_to_type(to_string_object)
    assert actual_result == expected_object


invalid_to_type_tests = [
    (String("true", 1), Boolean),
    (String("false", 1), Boolean),
    (String("\"root\" => [1, 2]", 1), Tree),
    (Boolean(True, 1), Integer),
    (Boolean(False, 1), Integer),
    (Boolean(True, 1), Float),
    (Boolean(False, 1), Float),
    (Boolean(True, 1), Tree),
    (Boolean(False, 1), Tree),
    (
        Tree(Node(Integer(5, 1), children=[
            Node(Float(4.5, 1)),
            Node(String("bools", 1), children=[
                Node(Boolean(True, 1)),
                Node(Boolean(False, 1))
            ]),
            Node(Integer(100, 1))
        ]), 1),
        String
    )
]


@pytest.mark.parametrize("input_object, _type", invalid_to_type_tests)
def test_to_type_invalid_types(input_object, _type):
    to_string_object = ToType([input_object], input_object.line_num, _type)

    with pytest.raises(LanguageRuntimeException) as error:
        evaluator.evaluate_to_type(to_string_object)
    assert error.typename == "LanguageRuntimeException"
    assert str(error.value) == f"Error at line 1: cannot convert {input_object.__class__.__name__} to {_type.__name__}"


invalid_data_tests = [
    (String("a", 1), Integer, "\"a\""),
    (String("a", 1), Float, "\"a\""),
]


@pytest.mark.parametrize("input_object, _type, input_object_repr", invalid_data_tests)
def test_to_type_valid_types_invalid_data(input_object, _type, input_object_repr):
    to_string_object = ToType([input_object], input_object.line_num, _type)

    with pytest.raises(LanguageRuntimeException) as error:
        evaluator.evaluate_to_type(to_string_object)
    assert error.typename == "LanguageRuntimeException"
    assert str(error.value) == f"Error at line 1: cannot convert '{input_object_repr}' of type " \
                               f"{input_object.__class__.__name__} to {_type.__name__}"
