package tests

import (
	"boomerang/evaluator"
	"boomerang/node"
	"boomerang/tokens"
	"fmt"
	"testing"
)

func TestEvaluator_Numbers(t *testing.T) {

	numbers := []string{
		"5",
		"3.1415928",
		"44.357",
	}

	for i, number := range numbers {
		ast := []node.Node{
			CreateNumber(number),
		}

		actualResults := getEvaluatorResults(ast)
		expectedResults := []node.Node{
			CreateNumber(number),
		}

		AssertNodesEqual(t, i, expectedResults, actualResults)
	}
}

func TestEvaluator_Booleans(t *testing.T) {

	booleans := []string{
		"true",
		"false",
	}

	for i, boolean := range booleans {
		ast := []node.Node{
			CreateBoolean(boolean),
		}

		actualResults := getEvaluatorResults(ast)
		expectedResults := []node.Node{
			CreateBoolean(boolean),
		}

		AssertNodesEqual(t, i, expectedResults, actualResults)
	}
}

func TestEvaluator_NegativeNumber(t *testing.T) {
	ast := []node.Node{
		node.CreateUnaryExpression(
			CreateTokenFromToken(tokens.MINUS_TOKEN),
			CreateNumber("66"),
		),
	}

	actualResults := getEvaluatorResults(ast)
	expectedResults := []node.Node{
		CreateNumber("-66"),
	}

	AssertNodesEqual(t, 0, expectedResults, actualResults)
}

func TestEvaluator_Bang(t *testing.T) {

	tests := []struct {
		Input          node.Node
		ExpectedResult node.Node
	}{
		{
			Input:          CreateBooleanTrue(),
			ExpectedResult: CreateBooleanFalse(),
		},
		{
			Input:          CreateBooleanFalse(),
			ExpectedResult: CreateBooleanTrue(),
		},
	}

	for i, test := range tests {
		ast := []node.Node{
			node.CreateUnaryExpression(
				CreateTokenFromToken(tokens.NOT_TOKEN),
				test.Input,
			),
		}

		actualResults := getEvaluatorResults(ast)
		expectedResults := []node.Node{
			test.ExpectedResult,
		}

		AssertNodesEqual(t, i, expectedResults, actualResults)
	}
}

func TestEvaluator_Strings(t *testing.T) {

	tests := []struct {
		InputSource  string
		OutputSource string
		Params       []node.Node
	}{
		{
			InputSource:  "hello, world!",
			OutputSource: "hello, world!",
			Params:       []node.Node{},
		},
		{
			InputSource:  "the time is <0>:<1>",
			OutputSource: "the time is 12:45",
			Params: []node.Node{
				CreateNumber("12"),
				CreateNumber("45"),
			},
		},
		{
			InputSource:  "the result is <0>",
			OutputSource: "the result is 13",
			Params: []node.Node{
				node.CreateBinaryExpression(
					CreateNumber("7"),
					tokens.PLUS_TOKEN,
					CreateNumber("6"),
				),
			},
		},
		{
			InputSource:  "Hello, my name is <0>, and I am <1> years old!",
			OutputSource: "Hello, my name is John, and I am 5 years old!",
			Params: []node.Node{
				CreateRawString("John"),
				node.CreateBinaryExpression(
					CreateNumber("3"),
					tokens.PLUS_TOKEN,
					CreateNumber("2"),
				),
			},
		},
		{
			InputSource:  "My numbers are <0>!",
			OutputSource: "My numbers are (1, 2, 3, 4)!",
			Params: []node.Node{
				CreateList([]node.Node{
					CreateNumber("1"),
					CreateNumber("2"),
					CreateNumber("3"),
					CreateNumber("4"),
				}),
			},
		},
	}

	for i, test := range tests {
		ast := []node.Node{
			CreateString(test.InputSource, test.Params),
		}

		actualResults := getEvaluatorResults(ast)
		expectedResults := []node.Node{
			CreateRawString(test.OutputSource),
		}
		AssertNodesEqual(t, i, expectedResults, actualResults)
	}
}

func TestEvaluator_Parameters(t *testing.T) {

	tests := []struct {
		Parameters     []node.Node
		ExpectedResult node.Node
	}{
		{
			Parameters:     []node.Node{},
			ExpectedResult: CreateList([]node.Node{}),
		},
		{
			Parameters: []node.Node{
				CreateNumber("55"),
			},
			ExpectedResult: CreateList([]node.Node{CreateNumber("55")}),
		},
		{
			Parameters: []node.Node{
				CreateNumber("34"),
				node.CreateBinaryExpression(
					CreateNumber("40"),
					tokens.ASTERISK_TOKEN,
					CreateNumber("3"),
				),
				CreateNumber("66"),
			},
			ExpectedResult: CreateList([]node.Node{
				CreateNumber("34"),
				CreateNumber("120"),
				CreateNumber("66"),
			}),
		},
		{
			Parameters: []node.Node{
				CreateNumber("66"),
				CreateNumber("4"),
				CreateNumber("30"),
			},
			ExpectedResult: CreateList([]node.Node{
				CreateNumber("66"),
				CreateNumber("4"),
				CreateNumber("30"),
			}),
		},
		{
			Parameters: []node.Node{
				CreateNumber("5"),
				CreateList([]node.Node{
					CreateNumber("78"),
				}),
				CreateNumber("60"),
			},
			ExpectedResult: CreateList([]node.Node{
				CreateNumber("5"),
				CreateList([]node.Node{
					CreateNumber("78"),
				}),
				CreateNumber("60"),
			}),
		},
	}

	for i, test := range tests {
		ast := []node.Node{
			CreateList(test.Parameters),
		}

		actualResults := getEvaluatorResults(ast)
		expectedResults := []node.Node{
			test.ExpectedResult,
		}
		AssertNodesEqual(t, i, expectedResults, actualResults)
	}
}

func TestEvaluator_BinaryExpressions(t *testing.T) {

	tests := []struct {
		AST    node.Node
		Result node.Node
	}{
		// Math expression
		{
			AST: node.CreateBinaryExpression(
				CreateNumber("1"),
				CreateTokenFromToken(tokens.PLUS_TOKEN),
				CreateNumber("1"),
			),
			Result: CreateNumber("2"),
		},
		{
			AST: node.CreateBinaryExpression(
				CreateNumber("2"),
				CreateTokenFromToken(tokens.ASTERISK_TOKEN),
				CreateNumber("2"),
			),
			Result: CreateNumber("4"),
		},
		{
			AST: node.CreateBinaryExpression(
				CreateNumber("5"),
				CreateTokenFromToken(tokens.MINUS_TOKEN),
				CreateNumber("2"),
			),
			Result: CreateNumber("3"),
		},
		{
			AST: node.CreateBinaryExpression(
				CreateNumber("10"),
				CreateTokenFromToken(tokens.FORWARD_SLASH_TOKEN),
				CreateNumber("2"),
			),
			Result: CreateNumber("5"),
		},
		{
			AST: node.CreateBinaryExpression(
				CreateNumber("10"),
				CreateTokenFromToken(tokens.MODULO_TOKEN),
				CreateNumber("2"),
			),
			Result: CreateNumber("0"),
		},
		{
			AST: node.CreateBinaryExpression(
				CreateNumber("10"),
				CreateTokenFromToken(tokens.MODULO_TOKEN),
				CreateNumber("3"),
			),
			Result: CreateNumber("1"),
		},

		// List append
		{
			AST: node.CreateBinaryExpression(
				CreateList([]node.Node{
					CreateBooleanTrue(),
					CreateBooleanFalse(),
				}),
				CreateTokenFromToken(tokens.SEND_TOKEN),
				CreateBooleanTrue(),
			),
			Result: CreateList([]node.Node{
				CreateBooleanTrue(),
				CreateBooleanFalse(),
				CreateBooleanTrue(),
			}),
		},
		{
			AST: node.CreateBinaryExpression(
				CreateList([]node.Node{
					CreateBooleanTrue(),
					CreateBooleanFalse(),
				}),
				CreateTokenFromToken(tokens.SEND_TOKEN),
				CreateList([]node.Node{
					CreateBooleanFalse(),
					CreateBooleanTrue(),
				}),
			),
			Result: CreateList([]node.Node{
				CreateBooleanTrue(),
				CreateBooleanFalse(),
				CreateBooleanFalse(),
				CreateBooleanTrue(),
			}),
		},

		// "in" operator: 5 in (1, 3, 5)
		{
			AST: node.CreateBinaryExpression(
				CreateNumber("5"),
				CreateTokenFromToken(tokens.IN_TOKEN),
				CreateList([]node.Node{
					CreateNumber("1"),
					CreateNumber("3"),
					CreateNumber("5"),
				}),
			),
			Result: CreateBooleanTrue(),
		},

		// Boolean OR
		{
			AST: node.CreateBinaryExpression(
				CreateBooleanTrue(),
				CreateTokenFromToken(tokens.OR_TOKEN),
				CreateBooleanTrue(),
			),
			Result: CreateBooleanTrue(),
		},
		{
			AST: node.CreateBinaryExpression(
				CreateBooleanTrue(),
				CreateTokenFromToken(tokens.OR_TOKEN),
				CreateBooleanFalse(),
			),
			Result: CreateBooleanTrue(),
		},
		{
			AST: node.CreateBinaryExpression(
				CreateBooleanFalse(),
				CreateTokenFromToken(tokens.OR_TOKEN),
				CreateBooleanTrue(),
			),
			Result: CreateBooleanTrue(),
		},
		{
			AST: node.CreateBinaryExpression(
				CreateBooleanFalse(),
				CreateTokenFromToken(tokens.OR_TOKEN),
				CreateBooleanFalse(),
			),
			Result: CreateBooleanFalse(),
		},

		// Boolean AND
		{
			AST: node.CreateBinaryExpression(
				CreateBooleanTrue(),
				CreateTokenFromToken(tokens.AND_TOKEN),
				CreateBooleanTrue(),
			),
			Result: CreateBooleanTrue(),
		},
		{
			AST: node.CreateBinaryExpression(
				CreateBooleanTrue(),
				CreateTokenFromToken(tokens.AND_TOKEN),
				CreateBooleanFalse(),
			),
			Result: CreateBooleanFalse(),
		},
		{
			AST: node.CreateBinaryExpression(
				CreateBooleanFalse(),
				CreateTokenFromToken(tokens.AND_TOKEN),
				CreateBooleanTrue(),
			),
			Result: CreateBooleanFalse(),
		},
		{
			AST: node.CreateBinaryExpression(
				CreateBooleanFalse(),
				CreateTokenFromToken(tokens.AND_TOKEN),
				CreateBooleanFalse(),
			),
			Result: CreateBooleanFalse(),
		},
	}

	for i, test := range tests {
		ast := []node.Node{
			test.AST,
		}

		actualResults := getEvaluatorResults(ast)
		expectedResults := []node.Node{
			test.Result,
		}

		AssertNodesEqual(t, i, expectedResults, actualResults)
	}
}

func TestEvaluator_Variable(t *testing.T) {
	// Source: variable = 8 / 2; variable;
	ast := []node.Node{
		{
			Type: node.ASSIGN_STMT,
			Params: []node.Node{
				CreateIdentifier("variable"),
				node.CreateBinaryExpression(
					CreateNumber("8"),
					tokens.FORWARD_SLASH_TOKEN,
					CreateNumber("2"),
				),
			},
		},
		CreateIdentifier("variable"),
	}

	actualResults := getEvaluatorResults(ast)
	expectedResults := []node.Node{
		CreateNumber("4"),
		CreateNumber("4"),
	}
	AssertNodesEqual(t, 0, actualResults, expectedResults)
}

func TestEvaluator_MultipleVariableAssignment(t *testing.T) {
	tests := []struct {
		Identifiers []node.Node
		Values      []node.Node
		ReturnValue node.Node
	}{
		{
			Identifiers: []node.Node{
				CreateIdentifier("a"),
				CreateIdentifier("b"),
			},
			Values: []node.Node{
				CreateNumber("1"),
				CreateNumber("2"),
			},
			ReturnValue: CreateList([]node.Node{
				CreateNumber("1"),
				CreateNumber("2"),
			}),
		},
		{
			Identifiers: []node.Node{
				CreateIdentifier("a"),
				CreateIdentifier("b"),
			},
			Values: []node.Node{
				node.CreateBinaryExpression(
					CreateNumber("4.5"),
					CreateTokenFromToken(tokens.PLUS_TOKEN),
					CreateNumber("5.5"),
				),
				CreateNumber("2"),
			},
			ReturnValue: CreateList([]node.Node{
				CreateNumber("10"),
				CreateNumber("2"),
			}),
		},
		{
			Identifiers: []node.Node{
				CreateIdentifier("a"),
				CreateIdentifier("b"),
				CreateIdentifier("c"),
			},
			Values: []node.Node{
				CreateNumber("1"),
				CreateNumber("2"),
			},
			ReturnValue: CreateList([]node.Node{
				CreateNumber("1"),
				CreateNumber("2"),
				CreateMonad(nil),
			}),
		},
		{
			Identifiers: []node.Node{
				CreateIdentifier("a"),
				CreateIdentifier("b"),
				CreateIdentifier("c"),
				CreateIdentifier("d"),
			},
			Values: []node.Node{
				CreateNumber("1"),
			},
			ReturnValue: CreateList([]node.Node{
				CreateNumber("1"),
				CreateMonad(nil),
				CreateMonad(nil),
				CreateMonad(nil),
			}),
		},
		{
			Identifiers: []node.Node{
				CreateIdentifier("a"),
				CreateIdentifier("b"),
			},
			Values: []node.Node{
				CreateNumber("1"),
				CreateNumber("2"),
				CreateNumber("3"),
			},
			ReturnValue: CreateList([]node.Node{
				CreateNumber("1"),
				CreateList([]node.Node{
					CreateNumber("2"),
					CreateNumber("3"),
				}),
			}),
		},
		{
			Identifiers: []node.Node{
				CreateIdentifier("a"),
				CreateIdentifier("b"),
			},
			Values: []node.Node{
				CreateNumber("1"),
				CreateNumber("2"),
				CreateNumber("3"),
				CreateNumber("4"),
			},
			ReturnValue: CreateList([]node.Node{
				CreateNumber("1"),
				CreateList([]node.Node{
					CreateNumber("2"),
					CreateNumber("3"),
					CreateNumber("4"),
				}),
			}),
		},
	}

	for i, test := range tests {
		ast := []node.Node{
			CreateAssignmentNode(
				CreateList(test.Identifiers),
				CreateList(test.Values),
			),
		}

		actualResults := getEvaluatorResults(ast)
		expectedResults := []node.Node{
			test.ReturnValue,
		}
		AssertNodesEqual(t, i, expectedResults, actualResults)
	}
}

func TestEvaluator_Function(t *testing.T) {
	ast := []node.Node{
		CreateFunction(
			[]node.Node{
				CreateIdentifier("a"),
				CreateIdentifier("b"),
			},
			[]node.Node{
				node.CreateBinaryExpression(
					CreateIdentifier("a"),
					tokens.PLUS_TOKEN,
					CreateIdentifier("b"),
				),
			},
		),
	}

	actualResults := getEvaluatorResults(ast)
	AssertNodesEqual(t, 0, ast, actualResults)
}

func TestEvaluator_FunctionCall(t *testing.T) {

	keywordArgsFunction := CreateFunction(
		[]node.Node{
			CreateIdentifier("a"),
			CreateAssignmentNode(
				CreateIdentifier("b"),
				CreateNumber("1"),
			),
		},
		[]node.Node{
			CreateReturnStatement(
				node.CreateBinaryExpression(
					CreateIdentifier("a"),
					tokens.PLUS_TOKEN,
					CreateIdentifier("b"),
				),
			),
		},
	)

	divideFunction := CreateFunction(
		[]node.Node{
			CreateIdentifier("a"),
			CreateIdentifier("b"),
		},
		[]node.Node{
			CreateReturnStatement(
				node.CreateBinaryExpression(
					CreateIdentifier("a"),
					tokens.FORWARD_SLASH_TOKEN,
					CreateIdentifier("b"),
				),
			),
		},
	)

	tests := []struct {
		Function    node.Node
		Params      []node.Node
		ReturnValue node.Node
	}{
		// Function Literal
		{
			Function: CreateFunction(
				[]node.Node{
					CreateIdentifier("c"),
					CreateIdentifier("d"),
				},
				[]node.Node{
					CreateReturnStatement(
						node.CreateBinaryExpression(
							CreateIdentifier("c"),
							tokens.MINUS_TOKEN,
							CreateIdentifier("d"),
						),
					),
				},
			),
			Params: []node.Node{
				CreateNumber("10"),
				CreateNumber("2"),
			},
			ReturnValue: CreateNumber("8"),
		},

		// Value of return statement returned, not last/other statements
		{
			Function: CreateFunction(
				[]node.Node{
					CreateIdentifier("c"),
					CreateIdentifier("d"),
				},
				[]node.Node{
					CreateReturnStatement(
						node.CreateBinaryExpression(
							CreateIdentifier("c"),
							tokens.MINUS_TOKEN,
							CreateIdentifier("d"),
						),
					),
					CreateRawString("not returned"),
				},
			),
			Params: []node.Node{
				CreateNumber("10"),
				CreateNumber("2"),
			},
			ReturnValue: CreateNumber("8"),
		},

		// Keyword Arguments
		{
			Function: keywordArgsFunction,
			Params: []node.Node{
				CreateNumber("10"),
			},
			ReturnValue: CreateNumber("11"),
		},
		{
			Function: keywordArgsFunction,
			Params: []node.Node{
				CreateNumber("10"),
				CreateNumber("5"),
			},
			ReturnValue: CreateNumber("15"),
		},
		{
			// A function where the first parameter has a default value
			Function: CreateFunction(
				[]node.Node{
					CreateAssignmentNode(
						CreateIdentifier("a"),
						CreateNumber("1"),
					),
					CreateIdentifier("b"),
				},
				[]node.Node{
					CreateReturnStatement(
						node.CreateBinaryExpression(
							CreateIdentifier("a"),
							tokens.PLUS_TOKEN,
							CreateIdentifier("b"),
						),
					),
				},
			),
			Params: []node.Node{
				CreateNumber("4"),
				CreateNumber("3"),
			},
			ReturnValue: CreateNumber("7"),
		},

		// Function Call with identifier
		{
			Function: CreateIdentifier("divide"),
			Params: []node.Node{
				CreateNumber("10"),
				CreateNumber("2"),
			},
			ReturnValue: CreateBlockStatementReturnValue(CreateNumber("5").Ptr()),
		},
		{
			Function: CreateIdentifier("divide"),
			Params: []node.Node{
				CreateNumber("6"),
				CreateNumber("3"),
			},
			ReturnValue: CreateBlockStatementReturnValue(CreateNumber("2").Ptr()),
		},

		// No Parameters
		{
			Function: CreateFunction(
				[]node.Node{},
				[]node.Node{
					CreateReturnStatement(
						node.CreateBinaryExpression(
							CreateNumber("3"),
							tokens.PLUS_TOKEN,
							CreateNumber("4"),
						),
					),
				},
			),
			Params:      []node.Node{},
			ReturnValue: CreateNumber("7"),
		},

		// No return value
		{
			Function: CreateFunction(
				[]node.Node{},
				[]node.Node{},
			),
			Params:      []node.Node{},
			ReturnValue: CreateMonad(nil),
		},
		{
			Function: CreateFunction(
				[]node.Node{},
				[]node.Node{
					node.CreateBinaryExpression(
						CreateNumber("3"),
						CreateTokenFromToken(tokens.FORWARD_SLASH_TOKEN),
						CreateNumber("5"),
					),
				},
			),
			Params:      []node.Node{},
			ReturnValue: CreateMonad(nil),
		},

		// Return value propagates through block statements to function-level block statement
		{
			Function: CreateFunction(
				[]node.Node{},
				[]node.Node{
					CreateAssignmentNode(
						CreateIdentifier("i"),
						CreateNumber("0"),
					),
					CreateWhileLoop(
						node.CreateBinaryExpression(
							CreateIdentifier("i"),
							CreateTokenFromToken(tokens.LT_TOKEN),
							CreateNumber("10"),
						),
						[]node.Node{
							CreateWhenNode(
								CreateIdentifier("i"),
								[]node.Node{
									CreateWhenCaseNode(
										CreateNumber("5"),
										[]node.Node{
											CreateReturnStatement(
												CreateIdentifier("i"),
											),
										},
									),
								},
								[]node.Node{},
							),
							CreateAssignmentNode(
								CreateIdentifier("i"),
								node.CreateBinaryExpression(
									CreateIdentifier("i"),
									CreateTokenFromToken(tokens.PLUS_TOKEN),
									CreateNumber("1"),
								),
							),
						},
					),
				},
			),
			Params:      []node.Node{},
			ReturnValue: CreateNumber("5"),
		},
	}

	for i, test := range tests {
		ast := []node.Node{
			CreateAssignmentNode(
				CreateIdentifier("divide"),
				divideFunction,
			),
			CreateFunctionCall(test.Function, test.Params),
		}

		actualResults := getEvaluatorResults(ast)

		expectedReturnValue := test.ReturnValue
		expectedResults := []node.Node{
			divideFunction,
			CreateBlockStatementReturnValue(&expectedReturnValue),
		}

		AssertNodesEqual(t, i, expectedResults, actualResults)
	}
}

func TestEvaluator_ListIndex(t *testing.T) {

	tests := []struct {
		Collection    node.Node
		Index         node.Node
		ExpectedValue node.Node
	}{
		{
			Collection: CreateList([]node.Node{
				CreateNumber("1"),
				CreateNumber("2"),
				CreateNumber("3"),
			}),
			Index:         CreateNumber("1"),
			ExpectedValue: CreateNumber("2"),
		},
		{
			Collection:    CreateRawString("hello, world!"),
			Index:         CreateNumber("2"),
			ExpectedValue: CreateRawString("l"),
		},
	}

	for i, test := range tests {
		ast := []node.Node{
			node.CreateBinaryExpression(
				test.Collection,
				tokens.AT_TOKEN,
				test.Index,
			),
		}
		actualResults := getEvaluatorResults(ast)
		expectedResults := []node.Node{
			test.ExpectedValue,
		}
		AssertNodesEqual(t, i, expectedResults, actualResults)
	}
}

func TestEvaluator_FunctionCallOperatorPrecedence(t *testing.T) {
	/*
		Source:
			add = func(a, b) {
				return a + b;
			};

			sum = add <- (3, 4);
			value = unwrap <- (sum, 0) + 7;  # test that unwrap is called before adding 7 to result
			value;
	*/
	addFunction := CreateFunction(
		[]node.Node{
			CreateIdentifier("a"),
			CreateIdentifier("b"),
		},
		[]node.Node{
			CreateReturnStatement(
				node.CreateBinaryExpression(
					CreateIdentifier("a"),
					CreateTokenFromToken(tokens.PLUS_TOKEN),
					CreateIdentifier("b"),
				),
			),
		},
	)

	addFunctionReturnValue := CreateFunctionCall(
		CreateIdentifier("add"),
		[]node.Node{
			CreateNumber("3"),
			CreateNumber("4"),
		},
	)

	actualValue := node.CreateBinaryExpression(
		CreateFunctionCall(
			CreateBuiltinFunctionIdentifier("unwrap"),
			[]node.Node{
				CreateIdentifier("sum"),
				CreateNumber("0"),
			},
		),
		CreateTokenFromToken(tokens.PLUS_TOKEN),
		CreateNumber("3"),
	)

	ast := []node.Node{
		CreateAssignmentNode(CreateIdentifier("add"), addFunction),
		CreateAssignmentNode(CreateIdentifier("sum"), addFunctionReturnValue),
		CreateAssignmentNode(CreateIdentifier("value"), actualValue),
		CreateIdentifier("value"),
	}

	actualResults := getEvaluatorResults(ast)
	expectedResults := []node.Node{
		addFunction,
		CreateMonad(CreateNumber("7").Ptr()),
		CreateNumber("10"),
		CreateNumber("10"),
	}
	AssertNodesEqual(t, 0, expectedResults, actualResults)
}

func TestEvaluator_CompareOperators(t *testing.T) {

	tests := []struct {
		BinaryExpressionAST node.Node
		ExpectedResult      node.Node
	}{
		// Equals
		{
			BinaryExpressionAST: node.CreateBinaryExpression(
				CreateNumber("7"),
				CreateTokenFromToken(tokens.EQ_TOKEN),
				CreateNumber("7"),
			),
			ExpectedResult: CreateBooleanTrue(),
		},
		{
			BinaryExpressionAST: node.CreateBinaryExpression(
				CreateNumber("146"),
				CreateTokenFromToken(tokens.EQ_TOKEN),
				CreateNumber("66"),
			),
			ExpectedResult: CreateBooleanFalse(),
		},
		{
			BinaryExpressionAST: node.CreateBinaryExpression(
				CreateBooleanTrue(),
				CreateTokenFromToken(tokens.EQ_TOKEN),
				CreateRawString("true"),
			),
			ExpectedResult: CreateBooleanFalse(),
		},

		// Not Equals
		{
			BinaryExpressionAST: node.CreateBinaryExpression(
				CreateNumber("16"),
				CreateTokenFromToken(tokens.NE_TOKEN),
				CreateNumber("13"),
			),
			ExpectedResult: CreateBooleanTrue(),
		},
		{
			BinaryExpressionAST: node.CreateBinaryExpression(
				CreateNumber("16"),
				CreateTokenFromToken(tokens.NE_TOKEN),
				CreateNumber("16"),
			),
			ExpectedResult: CreateBooleanFalse(),
		},

		// Less than
		{
			BinaryExpressionAST: node.CreateBinaryExpression(
				CreateNumber("5"),
				CreateTokenFromToken(tokens.LT_TOKEN),
				CreateNumber("5"),
			),
			ExpectedResult: CreateBooleanFalse(),
		},
		{
			BinaryExpressionAST: node.CreateBinaryExpression(
				CreateNumber("4"),
				CreateTokenFromToken(tokens.LT_TOKEN),
				CreateNumber("5"),
			),
			ExpectedResult: CreateBooleanTrue(),
		},
		{
			BinaryExpressionAST: node.CreateBinaryExpression(
				CreateNumber("3.14159"),
				CreateTokenFromToken(tokens.LT_TOKEN),
				CreateNumber("36.9"),
			),
			ExpectedResult: CreateBooleanTrue(),
		},
		{
			BinaryExpressionAST: node.CreateBinaryExpression(
				CreateNumber("3.14159"),
				CreateTokenFromToken(tokens.LT_TOKEN),
				CreateNumber("3.14159"),
			),
			ExpectedResult: CreateBooleanFalse(),
		},
	}

	for i, test := range tests {
		ast := []node.Node{test.BinaryExpressionAST}

		actualResults := getEvaluatorResults(ast)
		expectedResults := []node.Node{
			test.ExpectedResult,
		}
		AssertNodesEqual(t, i, expectedResults, actualResults)
	}
}

func TestEvaluator_WhenExpression(t *testing.T) {

	tests := []struct {
		WhenCondition string
		ExpectedValue string
	}{
		{"0", "5"},
		{"1", "10"},
		{"2", "15"},
	}

	for i, test := range tests {
		ast := []node.Node{
			CreateWhenNode(
				CreateNumber(test.WhenCondition),
				[]node.Node{
					CreateWhenCaseNode(
						CreateNumber("0"),
						[]node.Node{
							CreateNumber("5"),
						},
					),
					CreateWhenCaseNode(
						CreateNumber("1"),
						[]node.Node{
							CreateNumber("10"),
						},
					),
				},
				[]node.Node{
					CreateNumber("15"),
				},
			),
		}

		actualResults := getEvaluatorResults(ast)
		expectedResults := []node.Node{
			CreateMonad(CreateNumber(test.ExpectedValue).Ptr()),
		}
		AssertNodesEqual(t, i, expectedResults, actualResults)
	}
}

func TestEvaluator_WhenExpressionIfStatement(t *testing.T) {

	tests := []struct {
		WhenCondition string
		ExpectedValue string
	}{
		{"true", "5"},
		{"false", "10"},
	}

	for i, test := range tests {
		ast := []node.Node{
			CreateAssignmentNode(CreateIdentifier("number"), CreateNumber("0")),
			CreateWhenNode(
				CreateBoolean(test.WhenCondition),
				[]node.Node{
					CreateWhenCaseNode(
						node.CreateBinaryExpression(
							CreateIdentifier("number"),
							CreateTokenFromToken(tokens.EQ_TOKEN),
							CreateNumber("0"),
						),
						[]node.Node{
							CreateNumber("5"),
						},
					),
					CreateWhenCaseNode(
						node.CreateBinaryExpression(
							CreateIdentifier("number"),
							CreateTokenFromToken(tokens.EQ_TOKEN),
							CreateNumber("1"),
						),
						[]node.Node{
							CreateNumber("10"),
						},
					),
				},
				[]node.Node{
					CreateNumber("15"),
				},
			),
		}

		actualResults := getEvaluatorResults(ast)
		expectedResults := []node.Node{
			CreateNumber("0"),
			CreateMonad(CreateNumber(test.ExpectedValue).Ptr()),
		}
		AssertNodesEqual(t, i, expectedResults, actualResults)
	}
}

func TestEvaluator_VariablesFromOuterScopes(t *testing.T) {
	// "var" is defined outside the function "f", but is still accessible within that function.
	ast := []node.Node{
		CreateAssignmentNode(CreateIdentifier("var"), CreateNumber("10")),
		CreateAssignmentNode(
			CreateIdentifier("f"),
			CreateFunction(
				[]node.Node{CreateIdentifier("c")},
				[]node.Node{
					CreateReturnStatement(
						node.CreateBinaryExpression(
							CreateIdentifier("c"),
							CreateTokenFromToken(tokens.PLUS_TOKEN),
							CreateIdentifier("var"),
						),
					),
				},
			),
		),
		node.CreateBinaryExpression(
			CreateIdentifier("f"),
			CreateTokenFromToken(tokens.SEND_TOKEN),
			CreateList([]node.Node{
				CreateNumber("2"),
			}),
		),
	}

	actualResults := getEvaluatorResults(ast)
	expectedResults := []node.Node{
		CreateNumber("10"),
		CreateFunction(
			[]node.Node{CreateIdentifier("c")},
			[]node.Node{
				CreateReturnStatement(
					node.CreateBinaryExpression(
						CreateIdentifier("c"),
						CreateTokenFromToken(tokens.PLUS_TOKEN),
						CreateIdentifier("var"),
					),
				),
			},
		),
		CreateMonad(CreateNumber("12").Ptr()),
	}
	AssertNodesEqual(t, 0, expectedResults, actualResults)
}

func TestEvaluator_ForLoop(t *testing.T) {

	tests := []struct {
		BlockStatement []node.Node
		ReturnValue    node.Node
	}{
		{
			BlockStatement: []node.Node{
				node.CreateBinaryExpression(
					CreateIdentifier("e"),
					CreateTokenFromToken(tokens.ASTERISK_TOKEN),
					CreateIdentifier("e"),
				),
			},
			ReturnValue: CreateList([]node.Node{
				CreateBlockStatementReturnValue(CreateNumber("1").Ptr()),
				CreateBlockStatementReturnValue(CreateNumber("4").Ptr()),
				CreateBlockStatementReturnValue(CreateNumber("9").Ptr()),
				CreateBlockStatementReturnValue(CreateNumber("16").Ptr()),
			}),
		},
	}

	for i, test := range tests {
		ast := []node.Node{
			CreateForLoop(
				CreateIdentifier("e"),
				CreateList([]node.Node{
					CreateNumber("1"),
					CreateNumber("2"),
					CreateNumber("3"),
					CreateNumber("4"),
				}),
				test.BlockStatement,
			),
		}

		actualResults := getEvaluatorResults(ast)
		expectedResults := []node.Node{
			test.ReturnValue,
		}
		AssertNodesEqual(t, i, expectedResults, actualResults)
	}
}

func TestEvaluator_ForLoopUnpacking(t *testing.T) {

	tests := []struct {
		Identifiers     node.Node
		List            node.Node
		BlockStatements []node.Node
		Output          string
	}{
		{
			Identifiers: CreateList([]node.Node{
				CreateIdentifier("i"),
			}),
			List: CreateList([]node.Node{
				CreateList([]node.Node{
					CreateNumber("0"), CreateBooleanTrue(),
				}),
				CreateList([]node.Node{
					CreateNumber("1"), CreateBooleanFalse(),
				}),
			}),
			BlockStatements: []node.Node{
				CreateFunctionCall(
					CreateBuiltinFunctionIdentifier("print"),
					[]node.Node{
						CreateIdentifier("i"),
					},
				),
			},
			Output: "(0, true)\n(1, false)\n",
		},
		{
			Identifiers: CreateList([]node.Node{
				CreateIdentifier("i"),
				CreateIdentifier("j"),
			}),
			List: CreateList([]node.Node{
				CreateList([]node.Node{
					CreateNumber("0"), CreateBooleanTrue(),
				}),
				CreateList([]node.Node{
					CreateNumber("1"), CreateBooleanFalse(),
				}),
			}),
			BlockStatements: []node.Node{
				CreateFunctionCall(
					CreateBuiltinFunctionIdentifier("print"),
					[]node.Node{
						CreateIdentifier("i"),
						CreateIdentifier("j"),
					},
				),
			},
			Output: "0 true\n1 false\n",
		},
		{
			Identifiers: CreateList([]node.Node{
				CreateIdentifier("i"),
				CreateIdentifier("j"),
				CreateIdentifier("k"),
			}),
			List: CreateList([]node.Node{
				CreateList([]node.Node{
					CreateNumber("0"), CreateBooleanTrue(),
				}),
				CreateList([]node.Node{
					CreateNumber("1"), CreateBooleanFalse(),
				}),
			}),
			BlockStatements: []node.Node{
				CreateFunctionCall(
					CreateBuiltinFunctionIdentifier("print"),
					[]node.Node{
						CreateIdentifier("i"),
						CreateIdentifier("j"),
						CreateIdentifier("k"),
					},
				),
			},
			Output: "0 true Monad{}\n1 false Monad{}\n",
		},
	}

	for i, test := range tests {
		ast := []node.Node{
			CreateForLoop(
				test.Identifiers,
				test.List,
				test.BlockStatements,
			),
		}

		AssertExpectedOutput(t, i, test.Output, func() {
			getEvaluatorResults(ast)
		})
	}
}

func TestEvaluator_WhileLoop(t *testing.T) {
	ast := []node.Node{
		CreateAssignmentNode(
			CreateIdentifier("i"),
			CreateNumber("0"),
		),
		CreateWhileLoop(
			node.CreateBinaryExpression(
				CreateIdentifier("i"),
				CreateTokenFromToken(tokens.LT_TOKEN),
				CreateNumber("10"),
			),
			[]node.Node{
				CreateAssignmentNode(
					CreateIdentifier("i"),
					node.CreateBinaryExpression(
						CreateIdentifier("i"),
						CreateTokenFromToken(tokens.PLUS_TOKEN),
						CreateNumber("1"),
					),
				),
			},
		),
		CreateIdentifier("i"),
	}
	actualResults := getEvaluatorResults(ast)
	expectedResults := []node.Node{
		CreateNumber("0"),
		CreateNumber("10"),
	}
	AssertNodesEqual(t, 0, expectedResults, actualResults)
}

func TestEvaluator_BreakStatement(t *testing.T) {
	ast := []node.Node{
		CreateAssignmentNode(CreateIdentifier("i"), CreateNumber("0")),
		CreateWhileLoop(
			node.CreateBinaryExpression(
				CreateIdentifier("i"),
				CreateTokenFromToken(tokens.LT_TOKEN),
				CreateNumber("10"),
			),
			[]node.Node{
				CreateAssignmentNode(
					CreateIdentifier("i"),
					node.CreateBinaryExpression(
						CreateIdentifier("i"),
						CreateTokenFromToken(tokens.PLUS_TOKEN),
						CreateNumber("1"),
					),
				),
				CreateBreakStatement(),
			},
		),
		CreateIdentifier("i"),
	}
	actualResults := getEvaluatorResults(ast)
	expectedResults := []node.Node{
		CreateNumber("0"),
		CreateNumber("1"),
	}
	AssertNodesEqual(t, 0, expectedResults, actualResults)
}

func TestEvaluator_Continue(t *testing.T) {
	ast := []node.Node{
		CreateForLoop(
			CreateIdentifier("e"),
			CreateList([]node.Node{
				CreateNumber("1"),
				CreateNumber("2"),
				CreateNumber("3"),
				CreateNumber("4"),
				CreateNumber("5"),
				CreateNumber("6"),
			}),
			[]node.Node{
				CreateWhenNode(
					CreateBooleanTrue(),
					[]node.Node{
						CreateWhenCaseNode(
							node.CreateBinaryExpression(
								node.CreateBinaryExpression(
									CreateIdentifier("e"),
									CreateTokenFromToken(tokens.MODULO_TOKEN),
									CreateNumber("2"),
								),
								CreateTokenFromToken(tokens.EQ_TOKEN),
								CreateNumber("0"),
							),
							[]node.Node{
								CreateIdentifier("e"),
							},
						),
					},
					[]node.Node{
						CreateContinueStatement(),
					},
				),
			},
		),
	}
	actualResults := getEvaluatorResults(ast)
	expectedResults := []node.Node{
		CreateList([]node.Node{
			CreateMonad(CreateNumber("2").Ptr()),
			CreateMonad(CreateNumber("4").Ptr()),
			CreateMonad(CreateNumber("6").Ptr()),
		}),
	}
	AssertNodesEqual(t, 0, expectedResults, actualResults)
}

/* * * * * * * *
 * ERROR TESTS *
 * * * * * * * */

func TestEvaluator_InvalidUnaryOperatorError(t *testing.T) {
	// an if-statement in the global scope containing a return statement should throw an error
	ast := []node.Node{
		node.CreateUnaryExpression(
			CreateTokenFromToken(tokens.PLUS_TOKEN),
			CreateNumber("1"),
		),
	}

	actualError := getEvaluatorError(t, ast)
	expectedError := "error at line 1: invalid unary operator: PLUS (\"+\")"

	AssertErrorEqual(t, 0, expectedError, actualError)
}

func TestEvaluator_InvalidBinaryOperatorError(t *testing.T) {
	ast := []node.Node{
		node.CreateBinaryExpression(
			CreateNumber("1"),
			CreateTokenFromToken(tokens.NOT_TOKEN),
			CreateNumber("1"),
		),
	}

	actualError := getEvaluatorError(t, ast)
	expectedError := "error at line 1: invalid binary operator: NOT (\"not\")"

	AssertErrorEqual(t, 0, expectedError, actualError)
}

func TestEvaluator_FunctionCallErrors(t *testing.T) {

	tests := []struct {
		FunctionCall node.Node
		Error        string
	}{
		{
			FunctionCall: CreateFunctionCall(
				CreateNumber("1"),
				[]node.Node{
					CreateNumber("1"),
					CreateNumber("2"),
				},
			),
			Error: "error at line 1: cannot make function call on type Number (\"1\")",
		},
		{
			FunctionCall: CreateFunctionCall(
				CreateFunction(
					[]node.Node{
						CreateAssignmentNode(CreateIdentifier("a"), CreateNumber("1")),
						CreateIdentifier("b"),
					},
					[]node.Node{},
				),
				[]node.Node{
					CreateNumber("1"),
				},
			),
			Error: "error at line 1: Function paramter \"b\" does not have a value. Either add 1 more values to the function call or assign \"b\" a default value in the function definition parameters.",
		},
		{
			FunctionCall: CreateFunctionCall(
				CreateFunction(
					[]node.Node{
						CreateAssignmentNode(CreateIdentifier("a"), CreateNumber("1")),
						CreateAssignmentNode(CreateIdentifier("b"), CreateNumber("2")),
						CreateIdentifier("c"),
					},
					[]node.Node{},
				),
				[]node.Node{
					CreateNumber("1"),
				},
			),
			Error: "error at line 1: Function paramter \"c\" does not have a value. Either add 2 more values to the function call or assign \"c\" a default value in the function definition parameters.",
		},
		{
			FunctionCall: CreateFunctionCall(
				CreateFunction(
					[]node.Node{
						CreateAssignmentNode(CreateIdentifier("a"), CreateNumber("1")),
						CreateAssignmentNode(CreateIdentifier("b"), CreateNumber("2")),
						CreateIdentifier("c"),
					},
					[]node.Node{},
				),
				[]node.Node{
					CreateNumber("5"),
					CreateNumber("5"),
				},
			),
			Error: "error at line 1: Function paramter \"c\" does not have a value. Either add 1 more values to the function call or assign \"c\" a default value in the function definition parameters.",
		},
		{
			FunctionCall: CreateFunctionCall(
				CreateFunction([]node.Node{
					CreateIdentifier("a"),
				},
					[]node.Node{},
				),
				[]node.Node{
					CreateNumber("1"),
					CreateNumber("2"),
				},
			),
			Error: "error at line 1: expected 1 arguments, got 2",
		},
	}

	for i, test := range tests {
		ast := []node.Node{test.FunctionCall}

		actualError := getEvaluatorError(t, ast)
		AssertErrorEqual(t, i, test.Error, actualError)
	}
}

func TestEvaluator_IndexValueNotIntegerError(t *testing.T) {
	// an if-statement in the global scope containing a return statement should throw an error
	ast := []node.Node{
		node.CreateBinaryExpression(
			CreateList([]node.Node{
				CreateNumber("1"),
			}),
			CreateTokenFromToken(tokens.AT_TOKEN),
			CreateNumber("3.4"),
		),
	}

	actualError := getEvaluatorError(t, ast)
	expectedError := "error at line 1: list index must be an integer"

	AssertErrorEqual(t, 0, expectedError, actualError)
}

func TestEvaluator_IndexOutOfRangeError(t *testing.T) {
	tests := []struct {
		Sequence node.Node
		Index    node.Node
		Error    string
	}{
		{
			Sequence: CreateList([]node.Node{
				CreateNumber("1"),
			}),
			Index: CreateNumber("3"),
			Error: "error at line 1: index of 3 out of range (0 to 0)",
		},
		{
			Sequence: CreateRawString("test string"),
			Index:    CreateNumber("-1"),
			Error:    "error at line 1: index of -1 out of range (0 to 10)",
		},
	}

	for i, test := range tests {
		ast := []node.Node{
			node.CreateBinaryExpression(
				test.Sequence,
				CreateTokenFromToken(tokens.AT_TOKEN),
				test.Index,
			),
		}

		actualError := getEvaluatorError(t, ast)

		AssertErrorEqual(t, i, test.Error, actualError)
	}
}

func TestEvaluator_IndexInvalidTypeError(t *testing.T) {
	// an if-statement in the global scope containing a return statement should throw an error
	ast := []node.Node{
		node.CreateBinaryExpression(
			CreateNumber("3"),
			CreateTokenFromToken(tokens.AT_TOKEN),
			CreateNumber("3"),
		),
	}

	actualError := getEvaluatorError(t, ast)
	expectedError := "error at line 1: invalid types for index: Number (\"3\") and Number (\"3\")"

	AssertErrorEqual(t, 0, expectedError, actualError)
}

func TestEvaluator_AddInvalidTypesError(t *testing.T) {
	ast := []node.Node{
		node.CreateBinaryExpression(
			CreateRawString("hello"),
			CreateTokenFromToken(tokens.PLUS_TOKEN),
			CreateRawString(" world!"),
		),
	}
	actualError := getEvaluatorError(t, ast)
	expectedError := "error at line 1: cannot add types String (\"hello\") and String (\" world!\")"

	AssertErrorEqual(t, 0, expectedError, actualError)
}

func TestEvaluator_SubtractInvalidTypesError(t *testing.T) {
	ast := []node.Node{
		node.CreateBinaryExpression(
			CreateRawString("hello"),
			CreateTokenFromToken(tokens.MINUS_TOKEN),
			CreateRawString(" world!"),
		),
	}
	actualError := getEvaluatorError(t, ast)
	expectedError := "error at line 1: cannot subtract types String (\"hello\") and String (\" world!\")"

	AssertErrorEqual(t, 0, expectedError, actualError)
}

func TestEvaluator_MultiplyInvalidTypesError(t *testing.T) {
	ast := []node.Node{
		node.CreateBinaryExpression(
			CreateRawString("hello"),
			CreateTokenFromToken(tokens.ASTERISK_TOKEN),
			CreateRawString(" world!"),
		),
	}
	actualError := getEvaluatorError(t, ast)
	expectedError := "error at line 1: cannot multiply types String (\"hello\") and String (\" world!\")"

	AssertErrorEqual(t, 0, expectedError, actualError)
}

func TestEvaluator_DivideInvalidTypesError(t *testing.T) {
	ast := []node.Node{
		node.CreateBinaryExpression(
			CreateBooleanTrue(),
			CreateTokenFromToken(tokens.FORWARD_SLASH_TOKEN),
			CreateBooleanFalse(),
		),
	}

	actualError := getEvaluatorError(t, ast)
	expectedError := "error at line 1: cannot divide types Boolean (\"true\") and Boolean (\"false\")"

	AssertErrorEqual(t, 0, expectedError, actualError)
}

func TestEvaluator_DivideZeroError(t *testing.T) {
	ast := []node.Node{
		node.CreateBinaryExpression(
			CreateNumber("1"),
			CreateTokenFromToken(tokens.FORWARD_SLASH_TOKEN),
			CreateNumber("0"),
		),
	}

	actualError := getEvaluatorError(t, ast)
	expectedError := "error at line 1: cannot divide by zero"

	AssertErrorEqual(t, 0, expectedError, actualError)
}

func TestEvaluator_SendInvalidTypesError(t *testing.T) {
	ast := []node.Node{
		node.CreateBinaryExpression(
			CreateBooleanTrue(),
			CreateTokenFromToken(tokens.SEND_TOKEN),
			CreateBooleanFalse(),
		),
	}

	actualError := getEvaluatorError(t, ast)
	expectedError := "error at line 1: cannot use send on types Boolean (\"true\") and Boolean (\"false\")"

	AssertErrorEqual(t, 0, expectedError, actualError)
}

func TestEvaluator_BangError(t *testing.T) {
	ast := []node.Node{
		node.CreateUnaryExpression(
			CreateTokenFromToken(tokens.NOT_TOKEN),
			CreateNumber("1"),
		),
	}
	actualError := getEvaluatorError(t, ast)
	expectedError := "error at line 1: invalid type for bang operator: Number (\"1\")"

	AssertErrorEqual(t, 0, expectedError, actualError)
}

func TestEvaluator_MinusUnayError(t *testing.T) {
	ast := []node.Node{
		node.CreateUnaryExpression(
			CreateTokenFromToken(tokens.MINUS_TOKEN),
			CreateBooleanFalse(),
		),
	}
	actualError := getEvaluatorError(t, ast)
	expectedError := "error at line 1: invalid type for minus operator: Boolean (\"false\")"

	AssertErrorEqual(t, 0, expectedError, actualError)
}

func TestEvaluator_InvalidLoopStatementsError(t *testing.T) {

	tests := []struct {
		Statement node.Node
		Error     string
	}{
		{
			Statement: CreateBreakStatement(),
			Error:     "error at line 1: break statements not allowed outside loops",
		},
		{
			Statement: CreateWhenNode(
				CreateBooleanTrue(),
				[]node.Node{
					CreateWhenCaseNode(
						CreateBooleanTrue(),
						[]node.Node{
							CreateBreakStatement(),
						},
					),
				},
				[]node.Node{},
			),
			Error: "error at line 1: break statements not allowed outside loops",
		},
		{
			Statement: CreateFunctionCall(
				CreateFunction(
					[]node.Node{},
					[]node.Node{
						CreateBreakStatement(),
					},
				),
				[]node.Node{},
			),
			Error: "error at line 1: break statements not allowed outside loops",
		},
		{
			Statement: CreateContinueStatement(),
			Error:     "error at line 1: continue statements not allowed outside loops",
		},
		{
			Statement: CreateWhenNode(
				CreateBooleanTrue(),
				[]node.Node{
					CreateWhenCaseNode(
						CreateBooleanTrue(),
						[]node.Node{
							CreateContinueStatement(),
						},
					),
				},
				[]node.Node{},
			),
			Error: "error at line 1: continue statements not allowed outside loops",
		},
		{
			Statement: CreateFunctionCall(
				CreateFunction(
					[]node.Node{},
					[]node.Node{
						CreateContinueStatement(),
					},
				),
				[]node.Node{},
			),
			Error: "error at line 1: continue statements not allowed outside loops",
		},
		{
			Statement: CreateReturnStatement(CreateNumber("0")),
			Error:     "error at line 1: return statements not allowed outside loops",
		},
		{
			Statement: CreateWhileLoop(
				CreateBooleanTrue(),
				[]node.Node{
					CreateReturnStatement(CreateNumber("-1")),
				},
			),
			Error: "error at line 1: return statements not allowed outside loops",
		},
		{
			Statement: CreateWhenNode(
				CreateBooleanTrue(),
				[]node.Node{},
				[]node.Node{
					CreateReturnStatement(CreateNumber("-2")),
				},
			),
			Error: "error at line 1: return statements not allowed outside loops",
		},
	}

	for i, test := range tests {
		ast := []node.Node{
			test.Statement,
		}
		actualError := getEvaluatorError(t, ast)

		AssertErrorEqual(t, i, test.Error, actualError)
	}
}

func TestEvaluator_VariableError(t *testing.T) {

	for i, identifier := range evaluator.GetBuiltinNames() {
		ast := []node.Node{
			CreateAssignmentNode(CreateIdentifier(identifier), CreateNumber("20")),
		}

		actualError := getEvaluatorError(t, ast)
		expectedError := fmt.Sprintf("error at line 1: \"%s\" is a builtin function or variable", identifier)

		AssertErrorEqual(t, i, expectedError, actualError)
	}
}

func TestEvaluator_MultipleVariableAssignmentError(t *testing.T) {

	tests := []struct {
		AST   []node.Node
		Error string
	}{
		{
			AST: []node.Node{
				CreateAssignmentNode(
					CreateNumber("5"),
					CreateNumber("10"),
				),
			},
			Error: "error at line 1: invalid type for assignment: Number (\"5\")",
		},
	}

	for i, test := range tests {
		actualError := getEvaluatorError(t, test.AST)
		AssertErrorEqual(t, i, test.Error, actualError)
	}
}

func TestEvaluator_BinaryExpressionErrors(t *testing.T) {

	tests := []struct {
		Left  node.Node
		Right node.Node
		Error string
	}{
		{
			Left:  CreateNumber("hello"),
			Right: CreateNumber("1"),
			Error: "error at line 1: cannot convert \"hello\" to a number",
		},
		{
			Left:  CreateNumber("1"),
			Right: CreateNumber("world"),
			Error: "error at line 1: cannot convert \"world\" to a number",
		},
	}

	for i, test := range tests {
		ast := []node.Node{
			node.CreateBinaryExpression(
				test.Left,
				CreateTokenFromToken(tokens.PLUS_TOKEN),
				test.Right,
			),
		}

		actualError := getEvaluatorError(t, ast)
		AssertErrorEqual(t, i, test.Error, actualError)
	}
}
