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
