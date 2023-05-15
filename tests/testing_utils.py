from interpreter.evaluator.evaluator import Evaluator, Environment
import interpreter.parser_.ast_objects as o
from interpreter.tokens.token import Token
from interpreter.parser_.parser_ import Parser
from interpreter.tokens.tokenizer import Tokenizer
from interpreter.tokens.token_queue import TokenQueue
from utils.utils import Platform


def get_tokens(source: str) -> list[Token]:
    return [t for t in Tokenizer(source)]


def parser(source: str) -> Parser:
    tokenizer = Tokenizer(source)
    tokens = TokenQueue(tokenizer)
    return Parser(tokens)


def evaluator_actual_result(source: str) -> tuple[list[o.Expression], list[str]]:
    t = Tokenizer(source)
    tokens = TokenQueue(t)

    p = Parser(tokens)
    ast = p.parse()

    e = Evaluator(ast, Environment(), Platform.TEST.name)
    return e.evaluate()


def create_when(line_num: int, switch_expression: o.Expression, case_expressions: list[tuple[str, o.Expression, o.Expression]]) -> tuple[str, o.When]:
    conditions_and_expressions = []

    source = "when"
    if not isinstance(switch_expression, o.Boolean):
        source += f" {str(switch_expression)}"
    source += ":"

    for result in case_expressions:
        expr_src, left, right = result
        source += f"\n    {expr_src}"
        conditions_and_expressions.append((left, right))

    return source, o.When(line_num, switch_expression, conditions_and_expressions)


def assert_expression_equal(expected: o.Expression, actual: o.Expression) -> None:
    assert actual.line_num == expected.line_num

    if isinstance(expected, o.Number) and isinstance(actual, o.Number):
        assert actual.value == expected.value, f"actual.value: {actual.value}, expected.value: {expected.value}"

    elif isinstance(expected, o.Boolean) and isinstance(actual, o.Boolean):
        assert actual.value == expected.value, f"actual.value: {actual.value}, expected.value: {expected.value}"

    elif isinstance(expected, o.String) and isinstance(actual, o.String):
        assert actual.value == expected.value, f"actual.value: {actual.value}, expected.value: {expected.value}"

    elif isinstance(expected, o.Identifier) and isinstance(actual, o.Identifier):
        assert actual.value == expected.value, f"actual.value: {actual.value}, expected.value: {expected.value}"

    elif isinstance(expected, o.Error) and isinstance(actual, o.Error):
        assert actual.message == expected.message, \
            f"actual.message: {actual.message}, expected.message: {expected.message}"

    elif isinstance(expected, o.BuiltinFunction) and isinstance(actual, o.BuiltinFunction):
        assert actual.name == expected.name, f"actual.value: {actual.name}, expected.value: {expected.name}"

    elif isinstance(expected, o.List) and isinstance(actual, o.List):
        assert len(actual.values) == len(expected.values), \
            f"len(actual.values): {len(actual.values)}, len(expected.values): {len(expected.values)}"

        for e_val, a_val in zip(expected.values, actual.values):
            assert_expression_equal(e_val, a_val)

    elif isinstance(expected, o.Function) and isinstance(actual, o.Function):
        assert_expression_equal(expected.body, actual.body)
        assert len(actual.parameters) == len(expected.parameters), \
            f"len(actual.parameters): {len(actual.parameters)}, len(expected.parameters): {len(expected.parameters)}"

        for e_val, a_val in zip(expected.parameters, actual.parameters):
            assert_expression_equal(e_val, a_val)

    elif isinstance(expected, o.FunctionCall) and isinstance(actual, o.FunctionCall):
        assert_expression_equal(expected.function, actual.function)
        assert_expression_equal(expected.call_params, actual.call_params)

    elif isinstance(expected, o.PrefixExpression) and isinstance(actual, o.PrefixExpression):
        assert_expression_equal(expected.expression, actual.expression)
        assert_token_equal(expected.operator, actual.operator)

    elif isinstance(expected, o.PostfixExpression) and isinstance(actual, o.PostfixExpression):
        assert_expression_equal(expected.expression, actual.expression)
        assert_token_equal(expected.operator, actual.operator)

    elif isinstance(expected, o.InfixExpression) and isinstance(actual, o.InfixExpression):
        assert_expression_equal(expected.left, actual.left)
        assert_token_equal(expected.operator, actual.operator)
        assert_expression_equal(expected.right, actual.right)

    elif isinstance(expected, o.When) and isinstance(actual, o.When):
        assert_expression_equal(expected.expression, actual.expression)

        assert len(actual.case_expressions) == len(expected.case_expressions), \
            f"len(actual.case_expressions): {len(actual.case_expressions)}, len(expected.case_expressions): {len(expected.case_expressions)}"

        for (expected_case, expected_expr), (actual_case, actual_expression) in zip(expected.case_expressions, actual.case_expressions):
            assert_expression_equal(expected_case, actual_case)
            assert_expression_equal(expected_expr, actual_expression)

    elif isinstance(expected, o.ForLoop) and isinstance(actual, o.ForLoop):
        assert actual.element_identifier == expected.element_identifier, \
            f"actual.element_identifier: {actual.element_identifier}, expected.element_identifier: {expected.element_identifier}"
        assert_expression_equal(expected.values, actual.values)
        assert_expression_equal(expected.expression, actual.expression)

    elif isinstance(expected, o.Assignment) and isinstance(actual, o.Assignment):
        assert actual.name == expected.name, f"actual.name: {actual.name}, expected.name: {expected.name}"
        assert_expression_equal(expected.value, actual.value)

    else:
        assert False, f"Object types not equal. Actual type: {type(actual).__name__}; Expected type: {type(expected).__name__}"


def assert_expressions_equal(expected: list[o.Expression], actual: list[o.Expression]) -> None:
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
