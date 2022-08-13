import pytest
from evaluator.evaluator import Evaluator
from collections import namedtuple
from utils import LanguageRuntimeException


def test_evaluate_expression_invalid_type():
    evaluator = Evaluator([], None)

    InvalidType = namedtuple("InvalidType", "line_num")
    invalid_type = InvalidType(1)

    with pytest.raises(Exception) as error:
        evaluator.evaluate_expression(invalid_type)
    assert error.typename == "Exception"
    assert str(error.value) == "Unsupported type: InvalidType"
