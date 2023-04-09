# TODO: implement AST visualization (may cause issued with deployment on pythonanywhere)
# # mypy error: Skipping analyzing "graphviz": module is installed, but missing library stubs or py.typed marker
# # reason for ignore: mypy doesn't know about dependency types
# import graphviz  # type: ignore
# from parser_.ast_objects import *
#
#
# class ASTVisualizer:
#     def __init__(self, ast):
#         self.ast = ast
#         self.dot = graphviz.Digraph(comment="Abstract Syntax Tree (AST)")
#
#     def visualize(self):
#         for statement in self.ast:
#             self.__visualize(statement)
#
#         self.dot.render("graph.gv", view=True)
#
#     def __visualize(self, expression):
#         node_id = id(expression)
#         if type(expression) == BinaryOperation:
#             self.add_node(node_id, expression.op.value)
#
#             if expression.left not in [Integer, Boolean]:
#                 self.add_edge(node_id, id(expression.left))
#
#             if expression.right not in [Integer, Boolean]:
#                 self.add_edge(node_id, id(expression.right))
#
#             self.__visualize(expression.left)
#             self.__visualize(expression.right)
#         elif type(expression) == Print:
#             self.add_node(node_id, "print")
#             for param in expression.params:
#                 self.add_edge(node_id, id(param))
#                 self.__visualize(param)
#         elif type(expression) == SetVariable:
#             self.add_node(node_id, f"{expression.name.value} =")
#             self.add_edge(node_id, id(expression.value))
#             self.__visualize(expression.value)
#         else:
#             self.add_node(id(expression), expression.token.value)
#
#     def add_node(self, _id, label):
#         self.dot.node(str(_id), str(label))
#
#     def add_edge(self, start, end):
#         self.dot.edge(str(start), str(end))
