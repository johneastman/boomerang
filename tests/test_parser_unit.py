import pytest

from _parser._parser import Parser
from _parser.ast_objects import *
from tokens.tokenizer import Token, Tokenizer


def test_set_statement():
    tokenizer = Tokenizer("set variable = 1;")
    p = Parser(tokenizer)

    actual_assign_ast = p.assign()
    expected_assign_ast = SetVariable(
        Identifier("variable", 1),
        Integer(1, 1))
    assert actual_assign_ast == expected_assign_ast


operate_assign_tests = [
    ("+=", ASSIGN_ADD, "+", PLUS),
    ("-=", ASSIGN_SUB, "-", MINUS),
    ("*=", ASSIGN_MUL, "*", MULTIPLY),
    ("/=", ASSIGN_DIV, "/", DIVIDE),
]


@pytest.mark.parametrize("operator_assign_literal, operator_assign_type, operator_literal, operator_type", operate_assign_tests)
def test_set_statement_operate_assign(operator_assign_literal, operator_assign_type, operator_literal, operator_type):

    variable_name = "variable"
    source = f"set {variable_name} {operator_assign_literal} 1;"
    tokenizer = Tokenizer(source)

    identifier_token = Identifier(variable_name, 1)

    p = Parser(tokenizer)
    actual_assign_ast = p.assign()
    expected_assign_ast = SetVariable(
        identifier_token,
        BinaryOperation(
            identifier_token,
            Token(operator_literal, operator_type, 1),
            Integer(1, 1)))

    assert actual_assign_ast == expected_assign_ast


def test_loop():

    source = "while i < 10 {\n set i += 1; };"
    tokenizer = Tokenizer(source)

    p = Parser(tokenizer)
    actual_loop_ast = p.loop()
    expected_loop_ast = Loop(
        BinaryOperation(Identifier("i", 1), Token("<", LT, 1), Integer(10, 1)),
        [
            SetVariable(Identifier("i", 2),
                        BinaryOperation(Identifier("i", 2), Token("+", PLUS, 2), Integer(1, 2)))
        ]
    )

    assert actual_loop_ast == expected_loop_ast


tree_string_tests = [
    (
        Node(String("root", 1), 1),
        "\"root\" => []"
    ),
    (
        Node(String("root", 1), 1, children=[
            Node(Integer(1, 1), 1),
            Node(Float(3.14159, 1), 1)
        ]),
        "\"root\" => [1, 3.14159]"
    )
]


@pytest.mark.parametrize("tree, string_repr", tree_string_tests)
def test_tree_to_string(tree, string_repr):
    actual_value = str(tree)
    assert actual_value == string_repr
