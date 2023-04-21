import token

import pytest

from interpreter.parser_.ast_objects import *
from interpreter.tokens import tokens as t

test_binary_expression = BinaryExpression(1, Identifier(1, "a"), Token(1, "+", t.PLUS), Identifier(1, "b"))

test_function = Function(
    1,
    [Identifier(1, "a"), Identifier(1, "b")],
    test_binary_expression
)


@pytest.mark.parametrize("ast_object, repr_str", [
    (
        Number(1, 1),
        "Number(line_num=1, value=1)"
    ),
    (
        Boolean(1, True),
        "Boolean(line_num=1, value=True)"
    ),
    (
        String(1, "hello, world!"),
        "String(line_num=1, value='hello, world!')"
    ),
    (
        List(1, [Number(1, 1), Number(1, 2)]),
        "List(line_num=1, values=[Number(line_num=1, value=1), Number(line_num=1, value=2)])"
    ),
    (
        Identifier(1, "name"),
        "Identifier(line_num=1, value='name')"
    ),
    (
        test_function,
        "Function(line_num=1, parameters=[Identifier(line_num=1, value='a'), Identifier(line_num=1, value='b')], body=BinaryExpression(line_num=1, left=Identifier(line_num=1, value='a'), operator=Token(line_num=1, value='+', type=PLUS), right=Identifier(line_num=1, value='b')))"
    ),
    (
        FunctionCall(1, test_function, List(1, [Number(1, 1), Number(1, 2)])),
        "FunctionCall(line_num=1, function=Function(line_num=1, parameters=[Identifier(line_num=1, value='a'), Identifier(line_num=1, value='b')], body=BinaryExpression(line_num=1, left=Identifier(line_num=1, value='a'), operator=Token(line_num=1, value='+', type=PLUS), right=Identifier(line_num=1, value='b'))), call_params=List(line_num=1, values=[Number(line_num=1, value=1), Number(line_num=1, value=2)]))"
    ),
    (
        When(1, Boolean(1, True), [(Boolean(1, False), String(1, "yes")), (Boolean(1, True), String(1, "no"))]),
        "When(line_num=1, expression=Boolean(line_num=1, value=True), case_expressions=[(Boolean(line_num=1, value=False), String(line_num=1, value='yes')), (Boolean(line_num=1, value=True), String(line_num=1, value='no'))])"
    ),
    (
        Output(1, "output!"),
        "Output(line_num=1, value='output!')"
    ),
    (
        BuiltinFunction(1, "print"),
        "BuiltinFunction(line_num=1, name='print')"
    ),
    (
        UnaryExpression(1, Token(1, "-", t.MINUS), Number(1, 1)),
        "UnaryExpression(line_num=1, operator=Token(line_num=1, value='-', type=MINUS), expression=Number(line_num=1, value=1))"
    ),
    (
        test_binary_expression,
        "BinaryExpression(line_num=1, left=Identifier(line_num=1, value='a'), operator=Token(line_num=1, value='+', type=PLUS), right=Identifier(line_num=1, value='b'))"
    ),
    (
        PostfixExpression(1, Token(1, "++", t.INC), Number(1, 5)),
        "PostfixExpression(line_num=1, operator=Token(line_num=1, value='++', type=INC), expression=Number(line_num=1, value=5))"
    ),
    (
        Assignment(1, "variable", String(1, "hello")),
        "Assignment(line_num=1, name='variable', value=String(line_num=1, value='hello'))"
    ),
    (
        Error(1, "error message"),
        "Error(line_num=1, message='error message')"
    )
])
def test_repr(ast_object, repr_str):
    assert repr(ast_object) == repr_str


@pytest.mark.parametrize("left, right, expected_result", [
    (
        List(1, [Number(1, 1), Number(1, 2)]),
        List(1, [Number(1, 3), Number(1, 4)]),
        List(1, [Number(1, 1), Number(1, 2), Number(1, 3), Number(1, 4)])
    ),
    (
        List(1, []),
        List(1, [Number(1, 3), Number(1, 4)]),
        List(1, [Number(1, 3), Number(1, 4)])
    ),
    (
        List(1, [Number(1, 1), Number(1, 2)]),
        List(1, []),
        List(1, [Number(1, 1), Number(1, 2)])
    ),
])
def test_add(left, right, expected_result):
    actual_result = left.add(right)
    assert actual_result == expected_result


@pytest.mark.parametrize("left, right, expected_result", [
    (
        List(1, [Number(1, 1)]),
        Number(1, 2),
        List(1, [Number(1, 1), Number(1, 2)])
    ),
    (
        List(1, [Number(1, 1)]),
        List(1, [String(1, "hello"), String(1, "world")]),
        List(1, [Number(1, 1), List(1, [String(1, "hello"), String(1, "world")])])
    ),
    (
        Function(
            1,
            [Identifier(1, "a"), Identifier(1, "b")],
            BinaryExpression(
                1,
                Identifier(1, "a"),
                Token(1, "+", t.PLUS),
                Identifier(1, "b")
            )
        ),
        List(1, [Number(1, 1), Number(1, 2)]),
        FunctionCall(
            1,
            Function(
                1,
                [Identifier(1, "a"), Identifier(1, "b")],
                BinaryExpression(
                    1,
                    Identifier(1, "a"),
                    Token(1, "+", t.PLUS),
                    Identifier(1, "b")
                )
            ),
            List(1, [Number(1, 1), Number(1, 2)])
        )
    )
])
def test_ptr(left, right, expected_result):
    actual_result = left.ptr(right)
    assert actual_result == expected_result
