import pytest

import interpreter.parser_.ast_objects as o
from interpreter.parser_.builtin_ast_objects import Print
from utils.utils import LanguageRuntimeException
from tests.testing_utils import assert_expression_equal
from interpreter.tokens import tokens as t
from interpreter.tokens.token import Token

test_binary_expression = o.InfixExpression(1, o.Identifier(1, "a"), Token(1, "+", t.PLUS), o.Identifier(1, "b"))

test_function = o.Function(
    1,
    [o.Identifier(1, "a"), o.Identifier(1, "b")],
    test_binary_expression
)


@pytest.mark.parametrize("ast_object, repr_str", [
    (
        o.Number(1, 1),
        "Number(line_num=1, value=1)"
    ),
    (
        o.Boolean(1, True),
        "Boolean(line_num=1, value=True)"
    ),
    (
        o.String(1, "hello, world!"),
        "String(line_num=1, value='hello, world!')"
    ),
    (
        o.List(1, [o.Number(1, 1), o.Number(1, 2)]),
        "List(line_num=1, values=[Number(line_num=1, value=1), Number(line_num=1, value=2)])"
    ),
    (
        o.Identifier(1, "name"),
        "Identifier(line_num=1, value='name')"
    ),
    (
        o.Error(1, "error message"),
        "Error(line_num=1, message='error message')"
    ),
    (
        test_function,
        "Function(line_num=1, parameters=[Identifier(line_num=1, value='a'), Identifier(line_num=1, value='b')], body=InfixExpression(line_num=1, left=Identifier(line_num=1, value='a'), operator=Token(line_num=1, value='+', type=PLUS), right=Identifier(line_num=1, value='b')))"
    ),
    (
        o.FunctionCall(1, test_function, o.List(1, [o.Number(1, 1), o.Number(1, 2)])),
        "FunctionCall(line_num=1, function=Function(line_num=1, parameters=[Identifier(line_num=1, value='a'), Identifier(line_num=1, value='b')], body=InfixExpression(line_num=1, left=Identifier(line_num=1, value='a'), operator=Token(line_num=1, value='+', type=PLUS), right=Identifier(line_num=1, value='b'))), call_params=List(line_num=1, values=[Number(line_num=1, value=1), Number(line_num=1, value=2)]))"
    ),
    (
        o.When(1, o.Boolean(1, True), [(o.Boolean(1, False), o.String(1, "yes")), (o.Boolean(1, True), o.String(1, "no"))]),
        "When(line_num=1, expression=Boolean(line_num=1, value=True), case_expressions=[(Boolean(line_num=1, value=False), String(line_num=1, value='yes')), (Boolean(line_num=1, value=True), String(line_num=1, value='no'))])"
    ),
    (
        o.ForLoop(
            1,
            "i",
            o.List(1, [o.Number(1, 1), o.Number(1, 2), o.Number(1, 3)]),
            o.Boolean(1, True),
            o.InfixExpression(1, o.Identifier(1, "i"), Token(1, "+", t.PLUS), o.Number(1, 1))
        ),
        "ForLoop(line_num=1, element_identifier='i', values=List(line_num=1, values=[Number(line_num=1, value=1), Number(line_num=1, value=2), Number(line_num=1, value=3)]), conditional_expr=Boolean(line_num=1, value=True), expression=InfixExpression(line_num=1, left=Identifier(line_num=1, value='i'), operator=Token(line_num=1, value='+', type=PLUS), right=Number(line_num=1, value=1)))"
    ),
    (
        Print(1),
        "Print(line_num=1)"
    ),
    (
        o.PrefixExpression(1, Token(1, "-", t.MINUS), o.Number(1, 1)),
        "PrefixExpression(line_num=1, operator=Token(line_num=1, value='-', type=MINUS), expression=Number(line_num=1, value=1))"
    ),
    (
        test_binary_expression,
        "InfixExpression(line_num=1, left=Identifier(line_num=1, value='a'), operator=Token(line_num=1, value='+', type=PLUS), right=Identifier(line_num=1, value='b'))"
    ),
    (
        o.PostfixExpression(1, Token(1, "++", t.INC), o.Number(1, 5)),
        "PostfixExpression(line_num=1, operator=Token(line_num=1, value='++', type=INC), expression=Number(line_num=1, value=5))"
    ),
    (
        o.Assignment(1, "variable", o.String(1, "hello")),
        "Assignment(line_num=1, name='variable', value=String(line_num=1, value='hello'))"
    )
])
def test_repr(ast_object, repr_str):
    assert repr(ast_object) == repr_str


@pytest.mark.parametrize("value, str_repr, is_whole_num", [
    (1.0, "1", True),
    (1.45, "1.45", False)
])
def test_number_string(value, str_repr, is_whole_num):
    n = o.Number(1, value)
    assert str(n) == str_repr
    assert n.is_whole_number() == is_whole_num


@pytest.mark.parametrize("left, right, expected_result", [
    (
        o.List(1, [o.Number(1, 1), o.Number(1, 2)]),
        o.List(1, [o.Number(1, 3), o.Number(1, 4)]),
        o.List(1, [o.Number(1, 1), o.Number(1, 2), o.Number(1, 3), o.Number(1, 4)])
    ),
    (
        o.List(1, []),
        o.List(1, [o.Number(1, 3), o.Number(1, 4)]),
        o.List(1, [o.Number(1, 3), o.Number(1, 4)])
    ),
    (
        o.List(1, [o.Number(1, 1), o.Number(1, 2)]),
        o.List(1, []),
        o.List(1, [o.Number(1, 1), o.Number(1, 2)])
    ),
])
def test_add(left, right, expected_result):
    actual_result = left.add(right)
    assert_expression_equal(expected_result, actual_result)


@pytest.mark.parametrize("left, right, expected_result", [
    # Lists
    (
        o.List(1, [o.Number(1, 1), o.Number(1, 2), o.Number(1, 3), o.Number(1, 4), o.Number(1, 5)]),
        o.List(1, [o.Number(1, 1), o.Number(1, 3), o.Number(1, 5)]),
        o.List(1, [o.Number(1, 2), o.Number(1, 4)])
    ),
    (
        o.List(1, [o.Number(1, 1), o.Number(1, 2), o.Number(1, 3), o.Number(1, 4), o.Number(1, 5)]),
        o.List(1, []),
        o.List(1, [o.Number(1, 1), o.Number(1, 2), o.Number(1, 3), o.Number(1, 4), o.Number(1, 5)])
    ),
    (
        o.List(1, []),
        o.List(1, [o.Number(1, 1)]),
        o.List(1, [])
    ),
    (
        o.List(1, [o.Number(1, 1), o.Number(1, 1), o.Number(1, 3), o.Number(1, 4), o.Number(1, 4)]),
        o.List(1, [o.Number(1, 1), o.Number(1, 4)]),
        o.List(1, [o.Number(1, 3)])
    )
])
def test_sub(left, right, expected_result):
    actual_result = left.sub(right)
    assert_expression_equal(expected_result, actual_result)


@pytest.mark.parametrize("left, right, expected_result", [
    (
        o.List(1, [o.Number(1, 1)]),
        o.Number(1, 2),
        o.List(1, [o.Number(1, 1), o.Number(1, 2)])
    ),
    (
        o.List(1, [o.Number(1, 1)]),
        o.List(1, [o.String(1, "hello"), o.String(1, "world")]),
        o.List(1, [o.Number(1, 1), o.List(1, [o.String(1, "hello"), o.String(1, "world")])])
    ),
    (
        o.Function(
            1,
            [o.Identifier(1, "a"), o.Identifier(1, "b")],
            o.InfixExpression(
                1,
                o.Identifier(1, "a"),
                Token(1, "+", t.PLUS),
                o.Identifier(1, "b")
            )
        ),
        o.List(1, [o.Number(1, 1), o.Number(1, 2)]),
        o.FunctionCall(
            1,
            o.Function(
                1,
                [o.Identifier(1, "a"), o.Identifier(1, "b")],
                o.InfixExpression(
                    1,
                    o.Identifier(1, "a"),
                    Token(1, "+", t.PLUS),
                    o.Identifier(1, "b")
                )
            ),
            o.List(1, [o.Number(1, 1), o.Number(1, 2)])
        )
    )
])
def test_ptr(left, right, expected_result):
    actual_result = left.ptr(right)
    assert_expression_equal(expected_result, actual_result)


@pytest.mark.parametrize("left, right, expected_equal_result, expected_not_equal_result", [
    # Numbers
    (
        o.Number(1, 1),
        o.Number(2, 1),
        True,
        False
    ),
    (
        o.Number(1, 2),
        o.Number(2, 1),
        False,
        True
    ),

    # Booleans
    (
        o.Boolean(1, True),
        o.Boolean(2, True),
        True,
        False
    ),
    (
        o.Boolean(1, True),
        o.Boolean(2, False),
        False,
        True
    ),

    # Strings
    (
        o.String(1, "hello, world"),
        o.String(2, "hello, world"),
        True,
        False
    ),
    (
        o.String(1, "hello, world"),
        o.String(2, "Hello, World"),
        False,
        True
    ),

    # Lists
    (
        o.List(1, []),
        o.List(2, []),
        True,
        False
    ),
    (
        o.List(1, [o.Number(1, 1)]),
        o.List(2, [o.Number(2, 1)]),  # Line numbers don't need to match for equality
        True,
        False
    ),
    (
        o.List(1, [o.Number(1, 1)]),
        o.List(2, [o.Number(2, 2)]),
        False,
        True
    ),

    # Functions
    (
        o.Function(
            1,
            [o.Identifier(1, "a"), o.Identifier(1, "b")],
            o.InfixExpression(1, o.Identifier(1, "a"), Token(1, "+", t.PLUS), o.Identifier(1, "b"))
        ),
        o.Function(
            2,
            [o.Identifier(2, "a"), o.Identifier(2, "b")],
            o.InfixExpression(2, o.Identifier(2, "a"), Token(2, "+", t.PLUS), o.Identifier(2, "b"))
        ),
        True,
        False
    ),
    (
        o.Function(
            1,
            [o.Identifier(1, "b"), o.Identifier(1, "a")],
            o.InfixExpression(1, o.Identifier(1, "a"), Token(1, "+", t.PLUS), o.Identifier(1, "b"))
        ),
        o.Function(
            2,
            [o.Identifier(2, "a"), o.Identifier(2, "b")],
            o.InfixExpression(2, o.Identifier(2, "a"), Token(2, "+", t.PLUS), o.Identifier(2, "b"))
        ),
        False,
        True
    ),
])
def test_equal_not_equal(left, right, expected_equal_result, expected_not_equal_result):
    """Test that object are equal and not equal without consideration for the line number.
    """
    assert_expression_equal(o.Boolean(1, expected_equal_result), left.eq(right))
    assert_expression_equal(o.Boolean(1, expected_not_equal_result), left.ne(right))


@pytest.mark.parametrize("left, right, expected_result", [
    (o.Number(1, 1), o.List(1, [o.Number(1, 1), o.Number(1, 2)]), o.Boolean(1, True)),
    (o.Number(1, 3), o.List(1, [o.Number(1, 1), o.Number(1, 2)]), o.Boolean(1, False)),
    (o.Boolean(1, True), o.List(1, [o.Number(1, 1), o.Number(1, 2)]), o.Boolean(1, False)),
    (o.String(1, "hello, world!"), o.List(1, [o.Number(1, 1), o.Number(1, 2)]), o.Boolean(1, False)),
])
def test_in_valid(left, right, expected_result):
    actual_result = left.contains(right)
    assert_expression_equal(expected_result, actual_result)


@pytest.mark.parametrize("left, right, expected_error_message", [
    (o.Number(1, 1), o.Number(1, 1), "Error at line 1: invalid types Number and Number for IN"),
    (o.Number(1, 1), o.Boolean(1, True), "Error at line 1: invalid types Number and Boolean for IN"),
    (o.Number(1, 1), o.String(1, "hello, world!"), "Error at line 1: invalid types Number and String for IN"),
])
def test_in_error(left, right, expected_error_message):
    with pytest.raises(LanguageRuntimeException) as e:
        left.contains(right)
    assert str(e.value) == expected_error_message


@pytest.mark.parametrize("index, expected_result", [
    (o.Number(1, -3), o.Number(1, 1)),
    (o.Number(1, -2), o.Number(1, 2)),
    (o.Number(1, -1), o.Number(1, 3)),
    (o.Number(1, 0),  o.Number(1, 1)),
    (o.Number(1, 1),  o.Number(1, 2)),
    (o.Number(1, 2),  o.Number(1, 3))
])
def test_at(index, expected_result):
    left = o.List(1, [o.Number(1, 1), o.Number(1, 2), o.Number(1, 3)])

    actual_result = left.at(index)
    assert_expression_equal(expected_result, actual_result)


@pytest.mark.parametrize("index, expected_error_message", [
    (o.Number(1, -4), "Error at line 1: list index -4 is out of range"),
    (o.Number(1, 3), "Error at line 1: list index 3 is out of range"),
    (o.Number(1, 3.4), "Error at line 1: list index must be a whole number"),
    (o.Boolean(1, True), "Error at line 1: invalid types List and Boolean for INDEX"),
    (o.String(1, "hello, world"), "Error at line 1: invalid types List and String for INDEX"),
])
def test_at_error(index, expected_error_message):
    left = o.List(1, [o.Number(1, 1), o.Number(1, 2), o.Number(1, 3)])

    with pytest.raises(LanguageRuntimeException) as e:
        left.at(index)
    assert str(e.value) == expected_error_message


@pytest.mark.parametrize("left, right, expected_result", [
    (o.Number(1, 2), o.Number(1, 2), o.Number(1, 4)),
    (o.Number(1, 2), o.Number(1, 0), o.Number(1, 1)),
    (o.Number(1, 2), o.Number(1, -1), o.Number(1, 0.5))
])
def test_power(left, right, expected_result):
    actual_result = left.pow(right)
    assert_expression_equal(expected_result, actual_result)
