import pytest

import interpreter.parser_.ast_objects as o
from interpreter.tests.testing_utils import assert_expressions_equal
from interpreter.tokens.tokenizer import Tokenizer, Token
from interpreter.tokens.token_queue import TokenQueue
from interpreter.parser_.parser_ import Parser
from interpreter.evaluator.evaluator import Evaluator
from interpreter.evaluator.environment_ import Environment
from interpreter.tokens.tokens import PLUS, LE, SEND, MINUS


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
    assert_expressions_equal(expected_results, actual_results)


@pytest.mark.parametrize("source, expected_results", [
    # Number
    ("1 + 1", [o.Number(1, 2)]),
    ("4 / 2", [o.Number(1, 2)]),
    ("7 / 2", [o.Number(1, 3.5)]),
    ("7 % 0", [o.Error(1, "Error at line 1: cannot divide by zero")]),
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
    ("10 % 0", [o.Error(1, "Error at line 1: cannot divide by zero")]),
    ("10 % 1", [o.Number(1, 0)]),
    ("10 % 2", [o.Number(1, 0)]),
    ("10 % 3", [o.Number(1, 1)]),
    ("10 % 4", [o.Number(1, 2)]),
    ("10 % 5", [o.Number(1, 0)]),
    ("10 % 6", [o.Number(1, 4)]),
    ("10 % 7", [o.Number(1, 3)]),
    ("10 % 8", [o.Number(1, 2)]),
    ("10 % 9", [o.Number(1, 1)]),
    ("10 % 10", [o.Number(1, 0)]),

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
    ("(1,) == (\"1\",)", [o.Boolean(1, False)])
])
def test_binary_expressions(source, expected_results):
    actual_results = actual_result(f"{source};")
    assert_expressions_equal(expected_results, actual_results)


@pytest.mark.parametrize("source, expected_results", [
    # Factorial
    ("(-4)!", [o.Number(1, 120)]),
    ("(-3)!", [o.Number(1, 24)]),
    ("(-2)!", [o.Number(1, 6)]),
    ("(-1)!", [o.Number(1, 2)]),
    ("0!", [o.Number(1, 1)]),
    ("1!", [o.Number(1, 1)]),
    ("2!", [o.Number(1, 2)]),
    ("3!", [o.Number(1, 6)]),
    ("4!", [o.Number(1, 24)]),
    ("5!", [o.Number(1, 120)]),
    ("6!", [o.Number(1, 720)]),
    ("3!!", [o.Number(1, 720)]),

    # Decrement
    ("(-1)--", [o.Number(1, -2)]),
    ("0--", [o.Number(1, -1)]),
    ("1--", [o.Number(1, 0)]),
    ("2--", [o.Number(1, 1)]),
    ("3--", [o.Number(1, 2)]),
    ("3----", [o.Number(1, 1)]),

    # Increment
    ("(-1)++", [o.Number(1, 0)]),
    ("0++", [o.Number(1, 1)]),
    ("1++", [o.Number(1, 2)]),
    ("2++", [o.Number(1, 3)]),
    ("3++", [o.Number(1, 4)]),
    ("3++++", [o.Number(1, 5)]),

    # Combination Increment and Decrement
    ("16--++", [o.Number(1, 16)]),
    ("13++--", [o.Number(1, 13)]),
])
def test_suffix_operators(source, expected_results):
    actual_results = actual_result(f"{source};")
    assert_expressions_equal(expected_results, actual_results)


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
    ("-(-6)", [
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
    ("-(1, 2, 3)", [
        o.List(1, [o.Number(1, 3), o.Number(1, 2), o.Number(1, 1)])
    ])
])
def test_valid_unary_operations(source, expected_results):
    actual_results = actual_result(f"{source};")
    assert_expressions_equal(expected_results, actual_results)


@pytest.mark.parametrize("source, output_str", [
    ("\"hello, world!\"", "\"hello, world!\""),
    ("1", "1")
])
def test_print(source, output_str):
    actual_results = actual_result(f"print <- ({source},);")
    assert_expressions_equal([o.Output(1, output_str)], actual_results)


@pytest.mark.parametrize("low, high, params", [
    (0, 1, ""),
    (0, 5, "5,"),
    (5, 10, "5, 10"),
    (-5, 5, "-5, 5"),
    (-5, 0, "-5, 0"),
    (-5, 5, "-5, 5"),
])
def test_random(low, high, params):
    for _ in range(100):
        ast_results = actual_result(f"random <- ({params});")
        actual_value = ast_results[0]

        assert type(actual_value) == o.Number
        assert low <= actual_value.value <= high


@pytest.mark.parametrize("source, expected_results", [
    (
        """
        add = func a, b: a + b;
        add <- (1, 2);
        """,
        [
            o.Function(
                2,
                [o.Identifier(2, "a"), o.Identifier(2, "b")],
                o.BinaryExpression(
                    2,
                    o.Identifier(2, "a"),
                    Token(2, "+", PLUS),
                    o.Identifier(2, "b")
                )
            ),
            o.Number(3, 3.0)
        ]
    ),
    (
        # Recursive function call
        """
        decrement = func n:
            when:
                n <= 0: n
                else: decrement <- (n - 1,);
    
        decrement <- (3,);
        """,
        [
            o.Function(
                2,
                [o.Identifier(2, "n")],
                o.When(
                    3,
                    o.Boolean(3, True),
                    [
                        (
                            o.BinaryExpression(
                                4,
                                o.Identifier(4, "n"),
                                Token(4, "<=", LE),
                                o.Number(4, 0)
                            ),
                            o.Identifier(4, "n")
                        ),
                        (
                            o.Boolean(5, True),
                            o.BinaryExpression(
                                5,
                                o.Identifier(5, "decrement"),
                                Token(5, "<-", SEND),
                                o.List(
                                    5,
                                    [
                                        o.BinaryExpression(
                                            5,
                                            o.Identifier(5, "n"),
                                            Token(5, "-", MINUS),
                                            o.Number(5, 1)
                                        )
                                    ]
                                )
                            )
                        ),
                    ],
                )
            ),
            o.Number(7, 0)
        ]
    )
])
def test_functions(source, expected_results):
    actual_results = actual_result(source)
    assert_expressions_equal(expected_results, actual_results)


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
    actual_results = actual_result(src)
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
    assert_expressions_equal(expected_results, actual_results)


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
    actual_results = actual_result(src)
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
    assert_expressions_equal(expected_results, actual_results)


def actual_result(source):
    t = Tokenizer(source)
    tokens = TokenQueue(t)

    p = Parser(tokens)
    ast = p.parse()

    e = Evaluator(ast, Environment())
    return e.evaluate()
