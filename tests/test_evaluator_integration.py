import pytest

import _parser.ast_objects as o
from tokens.tokenizer import Tokenizer
from tokens.token_queue import TokenQueue
from _parser._parser import Parser
from evaluator.evaluator import Evaluator
from evaluator._environment import Environment
from utils.utils import LanguageRuntimeException


evaluator_tests = [
    ("1 + 1", [o.Integer(2, 1)]),
    ("1 + 2 * 2", [o.Integer(5, 1)]),
    ("(1 + 2) * 2", [o.Integer(6, 1)]),
    ("set x = (1 + 2) * 2;\nx", [o.NoReturn(line_num=1), o.Integer(6, 2)]),
    ("4 / 2", [o.Float(2.0, 1)]),
    ("7 / 2", [o.Float(3.5, 1)]),
    ("1 + 1 * 2 + 3 / 4", [o.Float(3.75, 1)]),
    ("\"hello \" + \"world!\"",  [o.String("hello world!", 1)]),
    ("0!", [o.Integer(1, 1)]),
    ("1!", [o.Integer(1, 1)]),
    ("2!", [o.Integer(2, 1)]),
    ("3!", [o.Integer(6, 1)]),
    ("4!", [o.Integer(24, 1)]),
    ("5!", [o.Integer(120, 1)]),
    ("6!", [o.Integer(720, 1)]),
    ("5! + 5", [o.Integer(125, 1)]),
    ("3!!", [o.Integer(720, 1)])
]


@pytest.mark.parametrize("source,expected_results", evaluator_tests)
def test_evaluator(source, expected_results):
    actual_results = actual_result(f"{source};")
    assert expected_results == actual_results


valid_boolean_operations_tests = [
    ("1 == 1", [o.Boolean(True, 1)]),
    ("1 != 1", [o.Boolean(False, 1)]),
    ("1 != 2", [o.Boolean(True, 1)]),
    ("1 >= 1", [o.Boolean(True, 1)]),
    ("1 >= 2", [o.Boolean(False, 1)]),
    ("1 > 1",  [o.Boolean(False, 1)]),
    ("1 > 2",  [o.Boolean(False, 1)]),
    ("2 > 1",  [o.Boolean(True, 1)]),
    ("1 <= 1", [o.Boolean(True, 1)]),
    ("1 <= 10", [o.Boolean(True, 1)]),
    ("10 <= 1", [o.Boolean(False, 1)]),
    ("1 < 2",  [o.Boolean(True, 1)]),
    ("2 < 1",  [o.Boolean(False, 1)]),
    ("10 == 2 + 4 * 2 == true",  [o.Boolean(True, 1)])
]


@pytest.mark.parametrize("source,expected_results", valid_boolean_operations_tests)
def test_valid_boolean_operations(source, expected_results):
    actual_results = actual_result(f"{source};")
    assert expected_results == actual_results


invalid_boolean_operations_tests = [
    ("1 == true", "Integer", "EQ", "Boolean"),
    ("1 != true", "Integer", "NE", "Boolean"),
    ("1 > true", "Integer", "GT", "Boolean"),
    ("2 >= false", "Integer", "GE", "Boolean"),
    ("2 < false", "Integer", "LT", "Boolean"),
    ("2 <= false", "Integer", "LE", "Boolean"),

    # Check that we can't use boolean operators in less-than, greater-than, greater-than-or-equal, or
    # less-than-or-equal
    ("true <= false", "Boolean", "LE", "Boolean"),
    ("true < false", "Boolean", "LT", "Boolean"),
    ("true >= false", "Boolean", "GE", "Boolean"),
    ("true > false", "Boolean", "GT", "Boolean")
]


@pytest.mark.parametrize("source,left_type,operation_type,right_type", invalid_boolean_operations_tests)
def test_invalid_boolean_operations(source, left_type, operation_type, right_type):
    with pytest.raises(LanguageRuntimeException) as error:
        actual_result(f"{source};")
    assert error.typename == "LanguageRuntimeException"
    assert f"Error at line 1: Cannot perform {operation_type} operation on {left_type} and {right_type}" == str(error.value)


valid_unary_operations_tests = [
    ("-1", [
        o.Integer(-1, 1)
     ]),
    ("+1", [
        o.Integer(1, 1)
    ]),
    ("-5.258", [
        o.Float(-5.258, 1)
    ]),
    ("5.258", [
        o.Float(5.258, 1)
    ]),
    ("!true", [
        o.Boolean(False, 1)
    ]),
    ("!false", [
        o.Boolean(True, 1)
    ]),
]


@pytest.mark.parametrize("source,expected_results", valid_unary_operations_tests)
def test_valid_unary_operations(source, expected_results):
    actual_results = actual_result(f"{source};")
    assert actual_results == expected_results


invalid_unary_operations_tests = [
    ("!1", "BANG", "Integer"),
    ("-true", "MINUS", "Boolean"),
    ("-false", "MINUS", "Boolean"),
    ("+true", "PLUS", "Boolean"),
    ("+false", "PLUS", "Boolean"),
]


@pytest.mark.parametrize("source,op,_type", invalid_unary_operations_tests)
def test_invalid_unary_operations(source, op, _type):
    with pytest.raises(LanguageRuntimeException) as error:
        actual_result(f"{source};")
    assert error.typename == "LanguageRuntimeException"
    assert str(error.value) == f"Error at line 1: Cannot perform {op} operation on {_type}"


def test_function_no_return():
    source = """
    func no_return() {
        set x = 1;
    }
    
    set var = no_return();
    """

    with pytest.raises(LanguageRuntimeException) as error:
        actual_result(source)
    assert error.typename == "LanguageRuntimeException"
    assert f"Error at line 6: cannot evaluate expression that returns no value" == str(error.value)


def test_function_empty_body_no_return():
    source = """
    func no_return() {}
    set var = no_return();
    """

    with pytest.raises(LanguageRuntimeException) as error:
        actual_result(source)
    assert error.typename == "LanguageRuntimeException"
    assert f"Error at line 3: cannot evaluate expression that returns no value" == str(error.value)


def test_function_return():
    source = """
    func is_equal(a, b) {
        if (a == b) {
            return true;
        }
    }
    is_equal(1, 1);  # true
    is_equal(1, 2);  # No return
    """
    expected_results = [
        o.NoReturn(line_num=2),
        o.Boolean(True, 7),
        o.NoReturn(line_num=8),
    ]
    actual_results = actual_result(source)
    assert actual_results == expected_results


function_calls_tests = [
    (1, 1, "2"),
    (1, 2, "3"),
    (12, 5, "17"),
    (2, 3, "5")
]


@pytest.mark.parametrize("first_param,second_param,return_val", function_calls_tests)
def test_function_calls(first_param, second_param, return_val):
    source = f"""
    func add(a, b) {{
        return a + b;
    }}
    add({first_param}, {second_param});
    """

    actual_results = actual_result(source)
    expected_results = [
        o.NoReturn(line_num=2),
        o.Integer(int(return_val), 5)
    ]
    assert actual_results == expected_results


def test_loop():
    """This test verifies that the loop works by checking the final value of "i". If "i" is 10, then the loop ran as
    expected; otherwise, there was an error.
    """
    source = """
    set i = 0;
    while i < 10 {
        set i = i + 1;
    }
    i;
    """
    actual_results = actual_result(source)
    expected_results = [
        o.NoReturn(line_num=2),
        o.NoReturn(),
        o.Integer(10, 6)
    ]
    assert actual_results == expected_results


def actual_result(source):
    t = Tokenizer(source)
    tokens = TokenQueue(t)

    p = Parser(tokens)
    ast = p.parse()

    e = Evaluator(ast, Environment())
    return e.evaluate()
