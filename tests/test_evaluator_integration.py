import pytest

import _parser.ast_objects as o
from tokens.tokens import *
from tokens.tokenizer import Tokenizer
from _parser._parser import Parser, NoReturn, DictionaryToken
from evaluator.evaluator import Evaluator
from evaluator._environment import Environment
from .testing_utils import TestToken
from utils.utils import LanguageRuntimeException


evaluator_tests = [
    ("1 + 1;", [o.Integer(2, 1)]),
    ("1 + 2 * 2;", [o.Integer(5, 1)]),
    ("(1 + 2) * 2;", [o.Integer(6, 1)]),
    ("set x = (1 + 2) * 2;x;", [o.Integer(6, 1), o.Integer(6, 1)]),
    ("4 / 2;", [o.Float(2.0, 1)]),
    ("7 / 2;", [o.Float(3.5, 1)]),
    ("1 + 1 * 2 + 3 / 4;", [o.Float(3.75, 1)]),
    ("\"hello \" + \"world!\";",  [o.String("hello world!", 1)]),
    ("{\"a\": 1 + 1, \"b\": 3 + (2 * 2 + 1), \"c\": 55};", [
        o.Dictionary(
            {
                o.String("a", 1): o.Integer(2, 1),
                o.String("b", 1): o.Integer(8, 1),
                o.String("c", 1): o.Integer(55, 1),
            }, 1
        )
    ]),
    ("0!;", [o.Integer(1, 1)]),
    ("1!;", [o.Integer(1, 1)]),
    ("2!;", [o.Integer(2, 1)]),
    ("3!;", [o.Integer(6, 1)]),
    ("4!;", [o.Integer(24, 1)]),
    ("5!;", [o.Integer(120, 1)]),
    ("6!;", [o.Integer(720, 1)]),
    ("5! + 5;", [o.Integer(125, 1)]),
    ("3!!;", [o.Integer(720, 1)])
]


@pytest.mark.parametrize("source,expected_results", evaluator_tests)
def test_evaluator(source, expected_results):
    actual_results = actual_result(source)
    assert expected_results == actual_results


valid_boolean_operations_tests = [
    ("1 == 1;", [o.Boolean(True, 1)]),
    ("1 != 1;", [o.Boolean(False, 1)]),
    ("1 != 2;", [o.Boolean(True, 1)]),
    ("1 >= 1;", [o.Boolean(True, 1)]),
    ("1 >= 2;", [o.Boolean(False, 1)]),
    ("1 > 1;",  [o.Boolean(False, 1)]),
    ("2 > 1;",  [o.Boolean(True, 1)]),
    ("1 <= 1;", [o.Boolean(True, 1)]),
    ("1 < 2;",  [o.Boolean(True, 1)]),
    ("2 < 1;",  [o.Boolean(False, 1)]),
    ("10 == (2 + 4 * 2) == true;",  [o.Boolean(True, 1)])
]


@pytest.mark.parametrize("source,expected_results", valid_boolean_operations_tests)
def test_valid_boolean_operations(source, expected_results):
    actual_results = actual_result(source)
    assert expected_results == actual_results


invalid_boolean_operations_tests = [
    ("1 == true;", "Integer", "EQ", "Boolean"),
    ("1 != true;", "Integer", "NE", "Boolean"),
    ("1 > true;", "Integer", "GT", "Boolean"),
    ("2 >= false;", "Integer", "GE", "Boolean"),
    ("2 < false;", "Integer", "LT", "Boolean"),
    ("2 <= false;", "Integer", "LE", "Boolean"),

    # Check that we can't use boolean operators in less-than, greater-than, greater-than-or-equal, or
    # less-than-or-equal
    ("true <= false;", "Boolean", "LE", "Boolean"),
    ("true < false;", "Boolean", "LT", "Boolean"),
    ("true >= false;", "Boolean", "GE", "Boolean"),
    ("true > false;", "Boolean", "GT", "Boolean")
]


@pytest.mark.parametrize("source,left_type,operation_type,right_type", invalid_boolean_operations_tests)
def test_invalid_boolean_operations(source, left_type, operation_type, right_type):
    with pytest.raises(LanguageRuntimeException) as error:
        actual_result(source)
    assert error.typename == "LanguageRuntimeException"
    assert f"Error at line 1: Cannot perform {operation_type} operation on {left_type} and {right_type}" == str(error.value)


valid_unary_operations_tests = [
    ("-1;", [
        o.Integer(-1, 1)
     ]),
    ("+1;", [
        o.Integer(1, 1)
    ]),
    ("-5.258;", [
        o.Float(-5.258, 1)
    ]),
    ("5.258;", [
        o.Float(5.258, 1)
    ]),
    ("!true;", [
        o.Boolean(False, 1)
    ]),
    ("!false;", [
        o.Boolean(True, 1)
    ]),
]


@pytest.mark.parametrize("source,expected_results", valid_unary_operations_tests)
def test_valid_unary_operations(source, expected_results):
    actual_results = actual_result(source)
    assert actual_results == expected_results


invalid_unary_operations_tests = [
    ("!1;", "BANG", "Integer"),
    ("-true;", "MINUS", "Boolean"),
    ("-false;", "MINUS", "Boolean"),
    ("+true;", "PLUS", "Boolean"),
    ("+false;", "PLUS", "Boolean"),
]


@pytest.mark.parametrize("source,op,_type", invalid_unary_operations_tests)
def test_invalid_unary_operations(source, op, _type):
    with pytest.raises(LanguageRuntimeException) as error:
        actual_result(source)
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
        NoReturn(line_num=2),
        o.Boolean(True, 7),
        NoReturn(line_num=8),
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
        NoReturn(line_num=2),
        TestToken(return_val, INTEGER, 5)
    ]
    assert actual_results == expected_results


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
    assert actual_results == expected_results


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
    assert actual_tokens == expected_tokens


def test_dictionary_get():
    source = """
    set d = {"a": 1, "b": 2, "c": 3};
    d["a"];
    d["b"];
    d["c"];
    """

    dict_line_num = 2
    expected_dictionary_token = o.DictionaryToken({
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
    assert actual_values == expected_values


def test_dictionary_get_invalid_key():
    source = """
    set d = {"a": 1, "b": 2, "c": 3};
    d["d"];
    """

    with pytest.raises(LanguageRuntimeException) as error:
        actual_result(source)
    assert error.typename == "LanguageRuntimeException"
    assert str(error.value) == "Error at line 3: No key in dictionary: \"d\""


def actual_result(source):
    t = Tokenizer(source)
    tokens = t.tokenize()

    p = Parser(tokens)
    ast = p.parse()

    e = Evaluator(ast, Environment())
    return e.evaluate()
