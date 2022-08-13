import pytest

import _parser.ast_objects
from tokens.tokens import *
from tokens.tokenizer import Tokenizer
from _parser._parser import Parser, NoReturn, DictionaryToken
from evaluator.evaluator import Evaluator
from evaluator._environment import Environment
import tests.testing_utils as utils
from .testing_utils import TestToken
from utils import LanguageRuntimeException


evaluator_tests = [
    ("1 + 1;", [TestToken("2", INTEGER, 1)]),
    ("1 + 2 * 2;", [TestToken("5", INTEGER, 1)]),
    ("(1 + 2) * 2;", [TestToken("6", INTEGER, 1)]),
    ("set x = (1 + 2) * 2;x;", [TestToken("6", INTEGER, 1), TestToken("6", INTEGER, 1)]),
    ("4 / 2;", [TestToken("2.0", FLOAT, 1)]),
    ("7 / 2;", [TestToken("3.5", FLOAT, 1)]),
    ("1 + 1 * 2 + 3 / 4;", [TestToken("3.75", FLOAT, 1)]),
    ("\"hello \" + \"world!\";",  [TestToken("hello world!", STRING, 1)]),
    ("{\"a\": 1 + 1, \"b\": 3 + (2 * 2 + 1), \"c\": 55};", [
        _parser.ast_objects.DictionaryToken(
            {
                TestToken("a", STRING, 1): TestToken("2", INTEGER, 1),
                TestToken("b", STRING, 1): TestToken("8", INTEGER, 1),
                TestToken("c", STRING, 1): TestToken("55", INTEGER, 1),
            }, 1
        )
    ]),
    ("0!;", [TestToken("1", INTEGER, 1)]),
    ("1!;", [TestToken("1", INTEGER, 1)]),
    ("2!;", [TestToken("2", INTEGER, 1)]),
    ("3!;", [TestToken("6", INTEGER, 1)]),
    ("4!;", [TestToken("24", INTEGER, 1)]),
    ("5!;", [TestToken("120", INTEGER, 1)]),
    ("6!;", [TestToken("720", INTEGER, 1)]),
    ("5! + 5;", [TestToken("125", INTEGER, 1)]),
    ("3!!;", [TestToken("720", INTEGER, 1)])
]


@pytest.mark.parametrize("source,expected_results", evaluator_tests)
def test_evaluator(source, expected_results):
    actual_results = actual_result(source)
    assert expected_results == actual_results


valid_boolean_operations_tests = [
    ("1 == 1;", [TestToken("true", BOOLEAN, 1)]),
    ("1 != 1;", [TestToken("false", BOOLEAN, 1)]),
    ("1 != 2;", [TestToken("true", BOOLEAN, 1)]),
    ("1 >= 1;", [TestToken("true", BOOLEAN, 1)]),
    ("1 >= 2;", [TestToken("false", BOOLEAN, 1)]),
    ("1 > 1;",  [TestToken("false", BOOLEAN, 1)]),
    ("2 > 1;",  [TestToken("true", BOOLEAN, 1)]),
    ("1 <= 1;", [TestToken("true", BOOLEAN, 1)]),
    ("1 < 2;",  [TestToken("true", BOOLEAN, 1)]),
    ("2 < 1;",  [TestToken("false", BOOLEAN, 1)]),
    ("10 == (2 + 4 * 2) == true;",  [TestToken("true", BOOLEAN, 1)])
]


@pytest.mark.parametrize("source,expected_results", valid_boolean_operations_tests)
def test_valid_boolean_operations(source, expected_results):
    actual_results = actual_result(source)
    assert expected_results == actual_results


invalid_boolean_operations_tests = [
    ("1 == true;", "INTEGER", "EQ", "BOOLEAN"),
    ("1 != true;", "INTEGER", "NE", "BOOLEAN"),
    ("1 > true;", "INTEGER", "GT", "BOOLEAN"),
    ("2 >= false;", "INTEGER", "GE", "BOOLEAN"),
    ("2 < false;", "INTEGER", "LT", "BOOLEAN"),
    ("2 <= false;", "INTEGER", "LE", "BOOLEAN"),

    # Check that we can't use boolean operators in less-than, greater-than, greater-than-or-equal, or
    # less-than-or-equal
    ("true <= false;", "BOOLEAN", "LE", "BOOLEAN"),
    ("true < false;", "BOOLEAN", "LT", "BOOLEAN"),
    ("true >= false;", "BOOLEAN", "GE", "BOOLEAN"),
    ("true > false;", "BOOLEAN", "GT", "BOOLEAN")
]


@pytest.mark.parametrize("source,left_type,operation_type,right_type", invalid_boolean_operations_tests)
def test_invalid_boolean_operations(source, left_type, operation_type, right_type):
    with pytest.raises(LanguageRuntimeException) as error:
        actual_result(source)
    assert error.typename == "LanguageRuntimeException"
    assert f"Error at line 1: Cannot perform {operation_type} operation on {left_type} and {right_type}" == str(error.value)


valid_unary_operations_tests = [
    ("-1;", [
        TestToken("-1", INTEGER, 1)
     ]),
    ("+1;", [
        TestToken("1", INTEGER, 1)
    ]),
    ("!true;", [
        TestToken("false", BOOLEAN, 1)
    ]),
    ("!false;", [
        TestToken("true", BOOLEAN, 1)
    ]),
]


@pytest.mark.parametrize("source,expected_results", valid_unary_operations_tests)
def test_valid_unary_operations(source, expected_results):
    actual_results = actual_result(source)
    assert expected_results == actual_results


invalid_unary_operations_tests = [
    ("!1;", "BANG", "INTEGER"),
    ("-true;", "MINUS", "BOOLEAN"),
    ("-false;", "MINUS", "BOOLEAN"),
    ("+true;", "PLUS", "BOOLEAN"),
    ("+false;", "PLUS", "BOOLEAN"),
]


@pytest.mark.parametrize("source,op,_type", invalid_unary_operations_tests)
def test_invalid_unary_operations(source, op, _type):
    with pytest.raises(LanguageRuntimeException) as error:
        actual_result(source)
    assert error.typename == "LanguageRuntimeException"
    assert f"Error at line 1: Cannot perform {op} operation on {_type}" == str(error.value)


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
        NoReturn(line_num=2),
        TestToken("true", BOOLEAN, 7),
        NoReturn(line_num=8),
    ]
    actual_results = actual_result(source)
    assert expected_results == actual_results


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
        NoReturn(line_num=2),
        TestToken(return_val, INTEGER, 5)
    ]
    assert expected_results == actual_results


assignment_tests = [
    ("set a = 2; set a += 2; a;", [
        TestToken("2", INTEGER, 1),
        TestToken("4", INTEGER, 1),
        TestToken("4", INTEGER, 1)
    ]),
    ("set a = 2; set a -= 2; a;", [
        TestToken("2", INTEGER, 1),
        TestToken("0", INTEGER, 1),
        TestToken("0", INTEGER, 1)
    ]),
    ("set a = 2; set a *= 2; a;", [
        TestToken("2", INTEGER, 1),
        TestToken("4", INTEGER, 1),
        TestToken("4", INTEGER, 1)
    ]),
    ("set a = 2; set a /= 2; a;", [
        TestToken("2", INTEGER, 1),
        TestToken("1.0", FLOAT, 1),
        TestToken("1.0", FLOAT, 1)
    ]),
    ("set d = {\"a\": 2}; set d[\"a\"] += 2; d[\"a\"];", [
        DictionaryToken({TestToken("a", STRING, 1): TestToken("2", INTEGER, 1)}, 1),
        NoReturn(line_num=1),
        TestToken("4", INTEGER, 1)
    ]),
    ("set d = {\"a\": 2}; set d[\"a\"] -= 2; d[\"a\"];", [
        DictionaryToken({TestToken("a", STRING, 1): TestToken("2", INTEGER, 1)}, 1),
        NoReturn(line_num=1),
        TestToken("0", INTEGER, 1)
    ]),
    ("set d = {\"a\": 2}; set d[\"a\"] *= 2; d[\"a\"];", [
        DictionaryToken({TestToken("a", STRING, 1): TestToken("2", INTEGER, 1)}, 1),
        NoReturn(line_num=1),
        TestToken("4", INTEGER, 1)
    ]),
    ("set d = {\"a\": 2}; set d[\"a\"] /= 2; d[\"a\"];", [
        DictionaryToken({TestToken("a", STRING, 1): TestToken("2", INTEGER, 1)}, 1),
        NoReturn(line_num=1),
        TestToken("1.0", FLOAT, 1)
    ]),
    ("set d = {\"a\": 2}; set d[\"a\"] = 5; d[\"a\"];", [
        DictionaryToken({TestToken("a", STRING, 1): TestToken("2", INTEGER, 1)}, 1),
        NoReturn(line_num=1),
        TestToken("5", INTEGER, 1)
    ]),
    ("set d = {\"a\": {1: 1, 2: 2}}; set d[\"a\"][1] += 20; d[\"a\"][1];", [
        DictionaryToken({
            TestToken("a", STRING, 1): DictionaryToken({
                TestToken("1", INTEGER, 1): TestToken("1", INTEGER, 1),
                TestToken("2", INTEGER, 1): TestToken("2", INTEGER, 1)}, 1)
        }, 1),
        NoReturn(line_num=1),
        TestToken("21", INTEGER, 1)
    ])
]


@pytest.mark.parametrize("source,expected_results", assignment_tests)
def test_assignment(source, expected_results):
    actual_results = actual_result(source)
    assert expected_results == actual_results


def test_embedded_dictionary_set():
    source = """
    set dict = {
        "a": {
            "b": {
                "c": 1,
                "d": 2
            }
        }
    };
    set dict["a"]["b"]["e"] = 3;
    dict;
    """
    actual_tokens = actual_result(source)
    expected_tokens = [
        DictionaryToken({
            TestToken("a", STRING, 3): DictionaryToken({
                TestToken("b", STRING, 4): DictionaryToken({
                    TestToken("c", STRING, 5): TestToken("1", INTEGER, 5),
                    TestToken("d", STRING, 6): TestToken("2", INTEGER, 6),
                }, 4)
            }, 3)
        }, 2),
        NoReturn(2),
        DictionaryToken({
            TestToken("a", STRING, 3): DictionaryToken({
                TestToken("b", STRING, 4): DictionaryToken({
                    TestToken("c", STRING, 5): TestToken("1", INTEGER, 5),
                    TestToken("d", STRING, 6): TestToken("2", INTEGER, 6),
                    TestToken("e", STRING, 10): TestToken("3", INTEGER, 10),
                }, 4)
            }, 3)
        }, 2),
    ]
    assert expected_tokens == actual_tokens


def test_dictionary_get():
    source = """
    set d = {"a": 1, "b": 2, "c": 3};
    d["a"];
    d["b"];
    d["c"];
    """

    dict_line_num = 2
    expected_dictionary_token = _parser.ast_objects.DictionaryToken({
        TestToken("a", STRING, dict_line_num): TestToken("1", INTEGER, dict_line_num),
        TestToken("b", STRING, dict_line_num): TestToken("2", INTEGER, dict_line_num),
        TestToken("c", STRING, dict_line_num): TestToken("3", INTEGER, dict_line_num),
    }, dict_line_num)

    expected_values = [
        expected_dictionary_token,
        TestToken("1", INTEGER, 3),
        TestToken("2", INTEGER, 4),
        TestToken("3", INTEGER, 5),
    ]
    actual_values = actual_result(source)
    assert expected_values == actual_values


def test_dictionary_get_invalid_key():
    source = """
    set d = {"a": 1, "b": 2, "c": 3};
    d["d"];
    """

    with pytest.raises(LanguageRuntimeException) as error:
        actual_result(source)
    assert error.typename == "LanguageRuntimeException"
    assert "Error at line 3: No key in dictionary: \"d\"" == str(error.value)


def actual_result(source):
    t = Tokenizer(source)
    tokens = t.tokenize()

    p = Parser(tokens)
    ast = p.parse()

    e = Evaluator(ast, Environment())
    return e.evaluate()
