import pytest

import interpreter.parser_.ast_objects as o
from interpreter.tokens.tokenizer import Tokenizer, Token
from interpreter.tokens.token_queue import TokenQueue
from interpreter.parser_.parser_ import Parser
from interpreter.evaluator.evaluator import Evaluator
from interpreter.evaluator.environment_ import Environment
from interpreter.tokens.tokens import PLUS


@pytest.mark.parametrize("source,expected_results", [
    ("1 + 2 * 2", [o.Number(1, 5)]),
    ("(1 + 2) * 2", [o.Number(1, 6)]),
    ("x = (1 + 2) * 2;\nx", [o.Number(1, 6), o.Number(2, 6)]),
    ("x = y = z = 2;\nx;\ny;\nz", [
        o.Number(1, 2),
        o.Number(2, 2),
        o.Number(3, 2),
        o.Number(4, 2)
    ]),
    ("1 + 1 * 2 + 3 / 4", [o.Number(1, 3.75)]),
    ("\"hello world!\"",  [o.String(1, "hello world!")]),
    ("true", [o.Boolean(1, True)]),
    ("false", [o.Boolean(1, False)]),
    ("()", [o.List(1, [])]),
    ("(1,)", [o.List(1, [o.Number(1, 1)])]),
    ("(1, 2, 3)", [o.List(1, [o.Number(1, 1), o.Number(1, 2), o.Number(1, 3)])]),
])
def test_evaluator(source, expected_results):
    actual_results = actual_result(f"{source};")
    assert expected_results == actual_results


@pytest.mark.parametrize("source, expected_results", [
    # Number
    ("1 + 1", [o.Number(1, 2)]),
    ("4 / 2", [o.Number(1, 2)]),
    ("7 / 2", [o.Number(1, 3.5)]),
    ("1 == 1", [o.Boolean(1, True)]),
    ("1 != 1", [o.Boolean(1, False)]),
    ("0 != 1", [o.Boolean(1, True)]),
    ("1 > 0", [o.Boolean(1, True)]),
    ("1 > 2", [o.Boolean(1, False)]),
    ("1 >= 0", [o.Boolean(1, True)]),
    ("1 >= 2", [o.Boolean(1, False)]),
    ("1 >= 1", [o.Boolean(1, True)]),
    ("1 < 2", [o.Boolean(1, True)]),
    ("1 < 0", [o.Boolean(1, False)]),
    ("1 <= 1", [o.Boolean(1, True)]),
    ("1 <= 2", [o.Boolean(1, True)]),
    ("1 <= 0", [o.Boolean(1, False)]),

    # String
    ("\"hello\" == \"hello\"", [o.Boolean(1, True)]),
    ("\"hello \" + \"world!\"", [o.String(1, "hello world!")]),
    ("\"hello\" - \"world\"", [o.Error(1, "Error at line 1: Invalid types String and String for MINUS")]),
    ("\"hello\" * \"world\"", [o.Error(1, "Error at line 1: Invalid types String and String for MULTIPLY")]),
    ("\"hello\" / \"world\"", [o.Error(1, "Error at line 1: Invalid types String and String for DIVIDE")]),

    # Boolean
    ("true & true", [o.Boolean(1, True)]),
    ("true & false", [o.Boolean(1, False)]),
    ("false & true", [o.Boolean(1, False)]),
    ("false & false", [o.Boolean(1, False)]),
    ("true | true", [o.Boolean(1, True)]),
    ("true | false", [o.Boolean(1, True)]),
    ("false | true", [o.Boolean(1, True)]),
    ("false | false", [o.Boolean(1, False)]),
    ("true == true", [o.Boolean(1, True)]),
    ("true != true", [o.Boolean(1, False)]),
    ("true != false", [o.Boolean(1, True)]),
    ("false == false", [o.Boolean(1, True)]),
    ("false != false", [o.Boolean(1, False)]),
    ("false != true", [o.Boolean(1, True)]),
    ("true > false", [o.Error(1, "Error at line 1: Invalid types Boolean and Boolean for GT")]),
    ("true >= false", [o.Error(1, "Error at line 1: Invalid types Boolean and Boolean for GE")]),
    ("true < false", [o.Error(1, "Error at line 1: Invalid types Boolean and Boolean for LT")]),
    ("true <= false", [o.Error(1, "Error at line 1: Invalid types Boolean and Boolean for LE")]),
    ("true + false", [o.Error(1, "Error at line 1: Invalid types Boolean and Boolean for PLUS")]),
    ("true - false", [o.Error(1, "Error at line 1: Invalid types Boolean and Boolean for MINUS")]),
    ("true * false", [o.Error(1, "Error at line 1: Invalid types Boolean and Boolean for MULTIPLY")]),
    ("true / false", [o.Error(1, "Error at line 1: Invalid types Boolean and Boolean for DIVIDE")]),

    # Mismatched types
    ("1 == \"1\"", [o.Boolean(1, False)]),
    ("1 == true", [o.Boolean(1, False)]),
    ("1 == (1,)", [o.Boolean(1, False)]),
    ("\"1\" == 1", [o.Boolean(1, False)]),
    ("\"true\" == true", [o.Boolean(1, False)]),
    ("\"true\" == (\"true\",)", [o.Boolean(1, False)]),
    ("true == 1", [o.Boolean(1, False)]),
    ("true == \"true\"", [o.Boolean(1, False)]),
    ("true == (\"true\",)", [o.Boolean(1, False)]),
    ("(1,) == 1", [o.Boolean(1, False)]),
    ("(1,) == \"1\"", [o.Boolean(1, False)]),
    ("(1,) == (\"1\",)", [o.Boolean(1, False)]),
])
def test_binary_expressions(source, expected_results):
    actual_results = actual_result(f"{source};")
    assert expected_results == actual_results


@pytest.mark.parametrize("source, expected_results", [
    ("3!", [o.Number(1, 6)]),
    ("6!", [o.Number(1, 720)]),
    ("3!!", [o.Number(1, 720)])
])
def test_suffix_operators(source, expected_results):
    actual_results = actual_result(f"{source};")
    assert expected_results == actual_results


@pytest.mark.parametrize("source,expected_results", [
    ("-1", [
        o.Number(1, -1)
     ]),
    ("+1", [
        o.Number(1, 1)
    ]),
    ("+-1", [
        o.Number(1, 1)
    ]),
    ("--6", [
        o.Number(1, 6)
    ]),
    ("-5.258", [
        o.Number(1, -5.258)
    ]),
    ("+5.258", [
        o.Number(1, 5.258)
    ]),
    ("!true", [
        o.Boolean(1, False)
    ]),
    ("!false", [
        o.Boolean(1, True)
    ]),
    ("!!true", [
        o.Boolean(1, True)
    ]),
    ("!!false", [
        o.Boolean(1, False)
    ]),
])
def test_valid_unary_operations(source, expected_results):
    actual_results = actual_result(f"{source};")
    assert actual_results == expected_results


@pytest.mark.parametrize("source, output_str", [
    ("\"hello, world!\"", "\"hello, world!\""),
    ("1", "1")
])
def test_print(source, output_str):
    results = actual_result(f"print <- ({source},);")
    assert results == [o.Output(1, output_str)]


def test_functions():
    src = """
    add = func a, b: a + b;
    add <- (1, 2);
    """

    expected_results = [
        o.Function(
            2,
            [o.Identifier(2, "a"), o.Identifier(2, "b")],
            o.BinaryExpression(
                2,
                o.Identifier(2, "a"),
                Token("+", PLUS, 2),
                o.Identifier(2, "b")
            )
        ),
        o.Number(3, 3.0)
    ]

    results = actual_result(src)
    assert results == expected_results


def test_when_if_implementation():
    src = """
    a = 1;
    when:
        a == 1: "1"
        a == 2: "2"
        a == 3: "3"
        a == 4: "4"
        else: "0";
    a = 2;
    when:
        a == 1: "1"
        a == 2: "2"
        a == 3: "3"
        a == 4: "4"
        else: "0";
    a = 3;
    when:
        a == 1: "1"
        a == 2: "2"
        a == 3: "3"
        a == 4: "4"
        else: "0";
    a = 4;
    when:
        a == 1: "1"
        a == 2: "2"
        a == 3: "3"
        a == 4: "4"
        else: "0";
    a = 5;
    when:
        a == 1: "1"
        a == 2: "2"
        a == 3: "3"
        a == 4: "4"
        else: "0";
    """
    results = actual_result(src)
    expected_results = [
        o.Number(2, 1),
        o.String(3, "1"),
        o.Number(9, 2),
        o.String(10, "2"),
        o.Number(16, 3),
        o.String(17, "3"),
        o.Number(23, 4),
        o.String(24, "4"),
        o.Number(30, 5),
        o.String(31, "0"),
    ]
    assert results == expected_results


def test_when_switch_implementation():
    src = """
    a = 1;
    when a:
        is 1: "1"
        is 2: "2"
        is 3: "3"
        is 4: "4"
        else: "0";
    a = 2;
    when a:
        is 1: "1"
        is 2: "2"
        is 3: "3"
        is 4: "4"
        else: "0";
    a = 3;
    when a:
        is 1: "1"
        is 2: "2"
        is 3: "3"
        is 4: "4"
        else: "0";
    a = 4;
    when a:
        is 1: "1"
        is 2: "2"
        is 3: "3"
        is 4: "4"
        else: "0";
    a = 5;
    when a:
        is 1: "1"
        is 2: "2"
        is 3: "3"
        is 4: "4"
        else: "0";
    """
    results = actual_result(src)
    expected_results = [
        o.Number(2, 1),
        o.String(3, "1"),
        o.Number(9, 2),
        o.String(10, "2"),
        o.Number(16, 3),
        o.String(17, "3"),
        o.Number(23, 4),
        o.String(24, "4"),
        o.Number(30, 5),
        o.String(31, "0"),
    ]
    assert results == expected_results


def actual_result(source):
    t = Tokenizer(source)
    tokens = TokenQueue(t)

    p = Parser(tokens)
    ast = p.parse()

    e = Evaluator(ast, Environment())
    return e.evaluate()
