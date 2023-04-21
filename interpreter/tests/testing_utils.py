from interpreter.parser_.ast_objects import *
from interpreter.parser_.parser_ import Parser
from interpreter.tokens.tokenizer import Tokenizer
from interpreter.tokens.token_queue import TokenQueue


def create_when(line_num: int, switch_expression: Expression, case_expressions: list[tuple[str, Expression, Expression]]) -> tuple[str, When]:
    conditions_and_expressions = []

    source = "when"
    if not isinstance(switch_expression, Boolean):
        source += f" {str(switch_expression)}"
    source += ":"

    for result in case_expressions:
        expr_src, left, right = result
        source += f"\n    {expr_src}"
        conditions_and_expressions.append((left, right))

    return source, When(line_num, switch_expression, conditions_and_expressions)


def parser(source: str) -> Parser:
    tokenizer = Tokenizer(source)
    tokens = TokenQueue(tokenizer)
    return Parser(tokens)


def assert_expression_equal(expected: Expression, actual: Expression) -> None:
    assert actual.line_num == expected.line_num

    if isinstance(expected, Number) and isinstance(actual, Number):
        assert actual.value == expected.value

    elif isinstance(expected, Boolean) and isinstance(actual, Boolean):
        assert actual.value == expected.value

    elif isinstance(expected, String) and isinstance(actual, String):
        assert actual.value == expected.value

    elif isinstance(expected, Identifier) and isinstance(actual, Identifier):
        assert actual.value == expected.value

    elif isinstance(expected, Error) and isinstance(actual, Error):
        assert actual.message == expected.message

    elif isinstance(expected, Output) and isinstance(actual, Output):
        assert actual.value == expected.value

    elif isinstance(expected, BuiltinFunction) and isinstance(actual, BuiltinFunction):
        assert actual.name == expected.name

    elif isinstance(expected, List) and isinstance(actual, List):
        assert len(actual.values) == len(expected.values)

        for e_val, a_val in zip(expected.values, actual.values):
            assert_expression_equal(e_val, a_val)

    elif isinstance(expected, Function) and isinstance(actual, Function):
        assert actual.body == expected.body
        assert len(actual.parameters) == len(expected.parameters)

        for e_val, a_val in zip(expected.parameters, actual.parameters):
            assert_expression_equal(e_val, a_val)

    elif isinstance(expected, FunctionCall) and isinstance(actual, FunctionCall):
        assert_expression_equal(expected.function, actual.function)
        assert_expression_equal(expected.call_params, actual.call_params)

    elif isinstance(expected, UnaryExpression) and isinstance(actual, UnaryExpression):
        assert_expression_equal(expected.expression, actual.expression)
        assert actual.operator == expected.operator

    elif isinstance(expected, PostfixExpression) and isinstance(actual, PostfixExpression):
        assert_expression_equal(expected.expression, actual.expression)
        assert actual.operator == expected.operator

    elif isinstance(expected, BinaryExpression) and isinstance(actual, BinaryExpression):
        assert_expression_equal(expected.left, actual.left)
        assert actual.operator == expected.operator
        assert_expression_equal(expected.right, actual.right)

    elif isinstance(expected, When) and isinstance(actual, When):
        assert_expression_equal(expected.expression, actual.expression)

        assert len(actual.case_expressions) == len(expected.case_expressions)

        for (expected_case, expected_expr), (actual_case, actual_expression) in zip(expected.case_expressions, actual.case_expressions):
            assert_expression_equal(expected_case, actual_case)
            assert_expression_equal(expected_expr, actual_expression)

    elif isinstance(expected, Assignment) and isinstance(actual, Assignment):
        assert actual.name == expected.name
        assert_expression_equal(expected.value, actual.value)

    else:
        assert False, f"Object types not equal. Actual type: {type(actual).__name__}; Expected type: {type(expected).__name__}"


def assert_expressions_equal(expected: list[Expression], actual: list[Expression]) -> None:
    assert len(actual) == len(expected)

    for exp, act in zip(expected, actual):
        assert_expression_equal(exp, act)


def assert_token_equal(expected: Token, actual: Token) -> None:
    assert actual.line_num == expected.line_num
    assert actual.value == expected.value
    assert actual.type == expected.type


def assert_tokens_equal(expected: list[Token], actual: list[Token]) -> None:
    assert len(actual) == len(expected)

    for exp, act in zip(expected, actual):
        assert_token_equal(exp, act)