import pytest

from interpreter._parser.ast_objects import Node, create_identifier
from interpreter.evaluator.evaluator import Evaluator
from interpreter.evaluator._environment import Environment
from interpreter.utils.utils import LanguageRuntimeException

evaluator = Evaluator([], Environment())


def test_evaluate_expression_invalid_type():
    invalid_type = Node("InvalidType", 1)

    with pytest.raises(Exception) as error:
        evaluator.evaluate_expression(invalid_type)
    assert error.typename == "Exception"
    assert str(error.value) == "Unsupported type: InvalidType"


def test_undefined_variable():
    undefined_variable = create_identifier("undefined", 1)

    with pytest.raises(LanguageRuntimeException) as error:
        evaluator.evaluate_identifier(undefined_variable)
    assert error.typename == "LanguageRuntimeException"
    assert str(error.value) == f"Error at line 1: undefined variable: {undefined_variable.value}"
