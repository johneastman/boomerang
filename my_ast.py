import graphviz
import _parser


class MyAST:
    def __init__(self, ast):
        self.ast = ast
        self.dot = graphviz.Digraph(comment="Abstract Syntax Tree (AST)")

    def visualize(self):
        for statement in self.ast:
            self.__visualize(statement)

        self.dot.render("graph.gv", view=True)

    def __visualize(self, expression):
        node_id = id(expression)
        if type(expression) == _parser.BinaryOperation:
            self.add_node(node_id, expression.op.value)

            if expression.left not in [_parser.Number, _parser.Boolean]:
                self.add_edge(node_id, id(expression.left))

            if expression.right not in [_parser.Number, _parser.Boolean]:
                self.add_edge(node_id, id(expression.right))

            self.__visualize(expression.left)
            self.__visualize(expression.right)
        elif type(expression) == _parser.BuiltinFunction:
            self.add_node(node_id, expression.name)
            for param in expression.parameters:
                self.add_edge(node_id, id(param))
                self.__visualize(param)
        elif type(expression) == _parser.AssignVariable:
            self.add_node(node_id, f"let {expression.name.value} =")
            self.add_edge(node_id, id(expression.value))
            self.__visualize(expression.value)
        else:
            self.add_node(id(expression), expression.value)

    def add_node(self, _id, label):
        self.dot.node(str(_id), str(label))

    def add_edge(self, start, end):
        self.dot.edge(str(start), str(end))
