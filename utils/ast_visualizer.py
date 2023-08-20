# mypy error: Skipping analyzing "graphviz": module is installed, but missing library stubs or py.typed marker
#
# reason for ignore: mypy doesn't know about dependency types
import graphviz  # type: ignore
from interpreter.parser_.ast_objects import *
from interpreter.parser_.builtin_ast_objects import BuiltinFunction


class ASTVisualizer:
    def __init__(self, ast: list[Expression]):
        self.ast = ast
        self.dot = graphviz.Digraph(comment="Abstract Syntax Tree (AST)")

    def visualize(self) -> bytes:
        root_node_id = "0"
        self.add_node(root_node_id, "Expressions")
        for statement in self.ast:
            self.__visualize(statement)
            self.add_edge(root_node_id, statement)

        # mypy error: Returning Any from function declared to return "bytes"
        #
        # Reason for ignoring: This does return bytes, but mypy doesn't know about dependency types
        return self.dot.pipe(format="pdf")  # type: ignore

    def __visualize(self, expression: Expression) -> None:
        node_id = str(id(expression))

        if any(isinstance(expression, type_)
               for type_ in [Number, String, Boolean, Error, Identifier]):
            self.add_node(node_id, str(expression))

        elif isinstance(expression, BuiltinFunction):
            # For builtin functions, the node display value is the name of the object.
            self.add_node(node_id, type(expression).__name__)

        elif isinstance(expression, List):
            self.add_node(node_id, "List")
            for value in expression.values:
                self.add_edge(node_id, value)
                self.__visualize(value)

        elif isinstance(expression, InfixExpression):
            self.add_node(node_id, expression.operator.value)

            self.add_edge(node_id, expression.left)
            self.__visualize(expression.left)

            self.add_edge(node_id, expression.right)
            self.__visualize(expression.right)

        elif isinstance(expression, PrefixExpression) or isinstance(expression, PostfixExpression):
            self.add_node(node_id, expression.operator.value)
            self.add_edge(node_id, expression.expression)
            self.__visualize(expression.expression)

        elif isinstance(expression, Assignment):
            self.add_node(node_id, "=")
            self.add_edge(node_id, expression.name)
            self.add_edge(node_id, expression.value)
            self.__visualize(expression.value)

        elif isinstance(expression, Function):
            self.add_node(node_id, "Function")

            parameters_node_id = f"{node_id}_parameters"
            self.add_node(parameters_node_id, "Parameters")
            self.add_edge(node_id, parameters_node_id)

            for param in expression.parameters:
                self.add_edge(parameters_node_id, param)
                self.__visualize(param)

            self.add_edge(node_id, expression.body)
            self.__visualize(expression.body)

        elif isinstance(expression, When):
            self.add_node(node_id, "When")

            when_expression_node_id = f"{node_id}_expression"
            self.add_node(when_expression_node_id, "Expression")
            self.add_edge(node_id, when_expression_node_id)

            self.add_edge(when_expression_node_id, expression.expression)
            self.__visualize(expression.expression)

            cases_node_id = f"{node_id}_cases"
            self.add_node(cases_node_id, "Cases")
            self.add_edge(node_id, cases_node_id)

            for i, (case_condition, case_val) in enumerate(expression.case_expressions):
                case_index_node = f"{cases_node_id}_case_{i}"
                self.add_node(case_index_node, f"Case {i}" if i < len(expression.case_expressions) - 1 else "Else")
                self.add_edge(cases_node_id, case_index_node)

                self.add_edge(case_index_node, case_condition)
                self.__visualize(case_condition)

                self.add_edge(case_index_node, case_val)
                self.__visualize(case_val)

        elif isinstance(expression, ForLoop):
            self.add_node(node_id, f"For Loop")

            # "in" keyword
            in_id = f"{node_id}_in"
            self.add_node(in_id, "in")
            self.add_edge(node_id, in_id)

            element_identifier_id = f"{node_id}_element_{expression.element_identifier}"
            self.add_node(element_identifier_id, expression.element_identifier)
            self.add_edge(in_id, element_identifier_id)

            # Values/List
            self.add_edge(in_id, expression.values)
            self.__visualize(expression.values)

            # For loop expression
            self.add_edge(node_id, expression.expression)
            self.__visualize(expression.expression)

        else:
            raise Exception(f"Unsupported type: {type(expression).__name__}")

    def add_node(self, _id: str, label: str) -> None:
        self.dot.node(str(_id), label)

    def add_edge(self, start: str | Expression, end: str | Expression) -> None:
        start_id = str(id(start)) if isinstance(start, Expression) else start
        end_id = str(id(end)) if isinstance(end, Expression) else end
        self.dot.edge(start_id, end_id)
