from interpreter.evaluator.evaluator import Evaluator, Environment
from interpreter.parser_.ast_objects import *
from interpreter.parser_.parser_ import Parser
from interpreter.tokens.tokenizer import Tokenizer
from interpreter.tokens.token_queue import TokenQueue
from utils.utils import Platform


def parser(source: str) -> Parser:
    tokenizer = Tokenizer(source)
    tokens = TokenQueue(tokenizer)
    return Parser(tokens)


def evaluator_actual_result(source: str) -> tuple[list[Expression], list[str]]:
    t = Tokenizer(source)
    tokens = TokenQueue(t)

    p = Parser(tokens)
    ast = p.parse()

    e = Evaluator(ast, Environment(), Platform.TEST.name)
    return e.evaluate()


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


def assert_expression_equal(expected: Expression, actual: Expression) -> None:
    assert actual.line_num == expected.line_num

    if isinstance(expected, Number) and isinstance(actual, Number):
        assert actual.value == expected.value, f"actual.value: {actual.value}, expected.value: {expected.value}"

    elif isinstance(expected, Boolean) and isinstance(actual, Boolean):
        assert actual.value == expected.value, f"actual.value: {actual.value}, expected.value: {expected.value}"

    elif isinstance(expected, String) and isinstance(actual, String):
        assert actual.value == expected.value, f"actual.value: {actual.value}, expected.value: {expected.value}"

    elif isinstance(expected, Identifier) and isinstance(actual, Identifier):
        assert actual.value == expected.value, f"actual.value: {actual.value}, expected.value: {expected.value}"

    elif isinstance(expected, Error) and isinstance(actual, Error):
        assert actual.message == expected.message, \
            f"actual.message: {actual.message}, expected.message: {expected.message}"

    elif isinstance(expected, BuiltinFunction) and isinstance(actual, BuiltinFunction):
        assert actual.name == expected.name, f"actual.value: {actual.name}, expected.value: {expected.name}"

    elif isinstance(expected, List) and isinstance(actual, List):
        assert len(actual.values) == len(expected.values), \
            f"len(actual.values): {len(actual.values)}, len(expected.values): {len(expected.values)}"

        for e_val, a_val in zip(expected.values, actual.values):
            assert_expression_equal(e_val, a_val)

    elif isinstance(expected, Function) and isinstance(actual, Function):
        assert_expression_equal(expected.body, actual.body)
        assert len(actual.parameters) == len(expected.parameters), \
            f"len(actual.parameters): {len(actual.parameters)}, len(expected.parameters): {len(expected.parameters)}"

        for e_val, a_val in zip(expected.parameters, actual.parameters):
            assert_expression_equal(e_val, a_val)

    elif isinstance(expected, FunctionCall) and isinstance(actual, FunctionCall):
        assert_expression_equal(expected.function, actual.function)
        assert_expression_equal(expected.call_params, actual.call_params)

    elif isinstance(expected, PrefixExpression) and isinstance(actual, PrefixExpression):
        assert_expression_equal(expected.expression, actual.expression)
        assert_token_equal(expected.operator, actual.operator)

    elif isinstance(expected, PostfixExpression) and isinstance(actual, PostfixExpression):
        assert_expression_equal(expected.expression, actual.expression)
        assert_token_equal(expected.operator, actual.operator)

    elif isinstance(expected, InfixExpression) and isinstance(actual, InfixExpression):
        assert_expression_equal(expected.left, actual.left)
        assert_token_equal(expected.operator, actual.operator)
        assert_expression_equal(expected.right, actual.right)

    elif isinstance(expected, When) and isinstance(actual, When):
        assert_expression_equal(expected.expression, actual.expression)

        assert len(actual.case_expressions) == len(expected.case_expressions), \
            f"len(actual.case_expressions): {len(actual.case_expressions)}, len(expected.case_expressions): {len(expected.case_expressions)}"

        for (expected_case, expected_expr), (actual_case, actual_expression) in zip(expected.case_expressions, actual.case_expressions):
            assert_expression_equal(expected_case, actual_case)
            assert_expression_equal(expected_expr, actual_expression)

    elif isinstance(expected, ForLoop) and isinstance(actual, ForLoop):
        assert actual.element_identifier == expected.element_identifier, \
            f"actual.element_identifier: {actual.element_identifier}, expected.element_identifier: {expected.element_identifier}"
        assert_expression_equal(expected.values, actual.values)
        assert_expression_equal(expected.expression, actual.expression)

    elif isinstance(expected, Assignment) and isinstance(actual, Assignment):
        assert actual.name == expected.name, f"actual.name: {actual.name}, expected.name: {expected.name}"
        assert_expression_equal(expected.value, actual.value)

    else:
        assert False, f"Object types not equal. Actual type: {type(actual).__name__}; Expected type: {type(expected).__name__}"


def assert_expressions_equal(expected: list[Expression], actual: list[Expression]) -> None:
    assert len(actual) == len(expected)

    for exp, act in zip(expected, actual):
        assert_expression_equal(exp, act)


def assert_token_equal(expected: Token, actual: Token) -> None:
    assert actual.line_num == expected.line_num, \
        f"actual.line_num: {actual.line_num}, expected.line_num: {expected.line_num}"
    assert actual.value == expected.value, \
        f"actual.value: {actual.value}, expected.value: {expected.value}"
    assert actual.type == expected.type, \
        f"actual.type: {actual.type}, expected.type: {expected.type}"


def assert_tokens_equal(expected: list[Token], actual: list[Token]) -> None:
    assert len(actual) == len(expected), \
        f"len(actual): {len(actual)}, len(expected): {len(expected)}"

    for exp, act in zip(expected, actual):
        assert_token_equal(exp, act)
