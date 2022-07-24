import pytest
from tokens.tokens import *
from tokens.tokenizer import Token, Tokenizer
from _parser._parser import Parser, NoReturn
from evaluator.evaluator import Evaluator
from evaluator._environment import Environment


evaluator_tests = [
    ("1 + 1;", [Token("2", INTEGER, 1)]),
    ("1 + 2 * 2;", [Token("5", INTEGER, 1)]),
    ("(1 + 2) * 2;", [Token("6", INTEGER, 1)]),
    ("x = (1 + 2) * 2;x;", [Token("6", INTEGER, 1), Token("6", INTEGER, 1)]),
    ("4 / 2;", [Token("2.0", FLOAT, 1)]),
    ("7 / 2;", [Token("3.5", FLOAT, 1)]),
    ("1 + 1 * 2 + 3 / 4;", [Token("3.75", FLOAT, 1)]),
    ("\"hello \" + \"world!\";",  [Token("hello world!", STRING, 1)]),
    ("{\"a\": 1 + 1, \"b\": 3 + (2 * 2 + 1), \"c\": 55};", [Token('{"a": 2, "b": 8, "c": 55}', DICTIONARY, 1)]),
]


@pytest.mark.parametrize("source,expected_results", evaluator_tests)
def test_evaluator(source, expected_results):
    actual_results = actual_result(source)
    assert_tokens_equal(expected_results, actual_results)


valid_boolean_operations_tests = [
    ("1 == 1;", [Token("true", BOOLEAN, 1)]),
    ("1 != 1;", [Token("false", BOOLEAN, 1)]),
    ("1 != 2;", [Token("true", BOOLEAN, 1)]),
    ("1 >= 1;", [Token("true", BOOLEAN, 1)]),
    ("1 >= 2;", [Token("false", BOOLEAN, 1)]),
    ("1 > 1;",  [Token("false", BOOLEAN, 1)]),
    ("2 > 1;",  [Token("true", BOOLEAN, 1)]),
    ("1 <= 1;", [Token("true", BOOLEAN, 1)]),
    ("1 < 2;",  [Token("true", BOOLEAN, 1)]),
    ("2 < 1;",  [Token("false", BOOLEAN, 1)]),
    ("10 == (2 + 4 * 2) == true;",  [Token("true", BOOLEAN, 1)])
]


@pytest.mark.parametrize("source,expected_results", valid_boolean_operations_tests)
def test_valid_boolean_operations(source, expected_results):
    actual_results = actual_result(source)
    assert_tokens_equal(expected_results, actual_results)


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
    with pytest.raises(Exception) as error:
        actual_result(source)
    assert f"Cannot perform {operation_type} operation on {left_type} and {right_type}" == str(error.value)


valid_unary_operations_tests = [
    ("-1;", [
        Token("-1", INTEGER, 1)
     ]),
    ("+1;", [
        Token("1", INTEGER, 1)
    ]),
    ("!true;", [
        Token("false", BOOLEAN, 1)
    ]),
    ("!false;", [
        Token("true", BOOLEAN, 1)
    ]),
]


@pytest.mark.parametrize("source,expected_results", valid_unary_operations_tests)
def test_valid_unary_operations(source, expected_results):
    actual_results = actual_result(source)
    assert_tokens_equal(expected_results, actual_results)


invalid_unary_operations_tests = [
    ("!1;", "BANG", "INTEGER"),
    ("-true;", "MINUS", "BOOLEAN"),
    ("-false;", "MINUS", "BOOLEAN"),
    ("+true;", "PLUS", "BOOLEAN"),
    ("+false;", "PLUS", "BOOLEAN"),
]


@pytest.mark.parametrize("source,op,_type", invalid_unary_operations_tests)
def test_invalid_unary_operations(source, op, _type):
    with pytest.raises(Exception) as error:
        actual_result(source)
    assert f"Cannot perform {op} operation on {_type}" == str(error.value)


def test_function_no_return():
    source = """
    func no_return() {
        x = 1;
    }
    
    var = no_return();
    """

    with pytest.raises(Exception) as error:
        actual_result(source)
    assert f"Error at line 6: cannot evaluate expression that returns no value" == str(error.value)


def test_function_empty_body_no_return():
    source = """
    func no_return() {}
    var = no_return();
    """

    with pytest.raises(Exception) as error:
        actual_result(source)
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
        Token("true", BOOLEAN, 7),
        NoReturn(line_num=8),
    ]
    actual_results = actual_result(source)
    assert_tokens_equal(expected_results, actual_results)


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
        Token(return_val, INTEGER, 5)
    ]
    assert_tokens_equal(expected_results, actual_results)


assignment_tests = [
    ("a = 2; a += 2; a;", [
        Token("2", INTEGER, 1),
        Token("4", INTEGER, 1),
        Token("4", INTEGER, 1)
    ]),
    ("a = 2; a -= 2; a;", [
        Token("2", INTEGER, 1),
        Token("0", INTEGER, 1),
        Token("0", INTEGER, 1)
    ]),
    ("a = 2; a *= 2; a;", [
        Token("2", INTEGER, 1),
        Token("4", INTEGER, 1),
        Token("4", INTEGER, 1)
    ]),
    ("a = 2; a /= 2; a;", [
        Token("2", INTEGER, 1),
        Token("1.0", FLOAT, 1),
        Token("1.0", FLOAT, 1)
    ]),
    ("d = {\"a\": 2}; d[\"a\"] += 2; d[\"a\"];", [
        Token('{"a": 2}', DICTIONARY, 1),
        NoReturn(line_num=1),
        Token("4", INTEGER, 1)
    ]),
    ("d = {\"a\": 2}; d[\"a\"] -= 2; d[\"a\"];", [
        Token('{"a": 2}', DICTIONARY, 1),
        NoReturn(line_num=1),
        Token("0", INTEGER, 1)
    ]),
    ("d = {\"a\": 2}; d[\"a\"] *= 2; d[\"a\"];", [
        Token('{"a": 2}', DICTIONARY, 1),
        NoReturn(line_num=1),
        Token("4", INTEGER, 1)
    ]),
    ("d = {\"a\": 2}; d[\"a\"] /= 2; d[\"a\"];", [
        Token('{"a": 2}', DICTIONARY, 1),
        NoReturn(line_num=1),
        Token("1.0", FLOAT, 1)
    ]),
    ("d = {\"a\": 2}; d[\"a\"] = 5; d[\"a\"];", [
        Token('{"a": 2}', DICTIONARY, 1),
        NoReturn(line_num=1),
        Token("5", INTEGER, 1)
    ])
]


@pytest.mark.parametrize("source,expected_results", assignment_tests)
def test_assignment(source, expected_results):
    actual_results = actual_result(source)
    assert_tokens_equal(expected_results, actual_results)


def test_dictionary_get():
    source = """
    d = {"a": 1, "b": 2, "c": 3};
    d["a"];
    d["b"];
    d["c"];
    """

    expected_values = [
        Token("{\"a\": 1, \"b\": 2, \"c\": 3}", DICTIONARY, 2),
        Token("1", INTEGER, 3),
        Token("2", INTEGER, 4),
        Token("3", INTEGER, 5),
    ]
    actual_values = actual_result(source)
    assert expected_values == actual_values


def test_dictionary_get_invalid_key():
    source = """
    d = {"a": 1, "b": 2, "c": 3};
    d["d"];
    """

    with pytest.raises(Exception) as error:
        actual_result(source)
    assert "Error at line 3: No key in dictionary: d" == str(error.value)


def assert_tokens_equal(expected_results, actual_results):
    assert len(expected_results) == len(actual_results)

    for expected, actual in zip(expected_results, actual_results):
        assert expected.value == actual.value
        assert expected.type == actual.type
        assert expected.line_num == actual.line_num


def actual_result(source):
    t = Tokenizer(source)
    tokens = t.tokenize()

    p = Parser(tokens)
    ast = p.parse()

    e = Evaluator(ast, Environment())
    return e.evaluate()
