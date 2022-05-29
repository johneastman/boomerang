import graphviz
import _parser


class MyAST:
    def __init__(self, ast):
        self.ast = ast
        self.dot = graphviz.Digraph(comment="Abstract Syntax Tree (AST)")

    def visualize(self):
        statememnt = self.ast[0]
        self.__visualize(statememnt)
        self.dot.render("graph.gv", view=True)

    def __visualize(self, expression):
        if type(expression) == _parser.BinaryOperation:
            node_id = id(expression)
            self.add_node(node_id, expression.op.value)

            if expression.left not in [_parser.Number, _parser.Boolean]:
                self.add_edge(node_id, id(expression.left))

            if expression.right not in [_parser.Number, _parser.Boolean]:
                self.add_edge(node_id, id(expression.right))

            self.__visualize(expression.left)
            self.__visualize(expression.right)
        else:
            self.add_node(id(expression), expression.value)

    def add_node(self, _id, label):
        self.dot.node(str(_id), str(label))

    def add_edge(self, start, end):
        self.dot.edge(str(start), str(end))
