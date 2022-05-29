import graphviz

class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


class BinaryTree:
    def __init__(self):
        self.root = None
        self.dot = graphviz.Digraph(comment="Binary Tree")

    def add(self, val):
        if self.root is None:
            self.root = Node(val)
        else:
            self._add(val, self.root)

    def _add(self, val, node):
        if val < node.value:
            if node.left is not None:
                self._add(val, node.left)
            else:
                node.left = Node(val)
        else:
            if node.right is not None:
                self._add(val, node.right)
            else:
                node.right = Node(val)

    def print_tree(self):
        if self.root is not None:
            self._print_tree(self.root)

        self.dot.render("binary_tree.gv", view=True)

    def _print_tree(self, node):
        if node is not None:
            self.add_node(id(node), node.value)

            if node.left is not None:
                self.add_edge(id(node), id(node.left))

            if node.right is not None:
                self.add_edge(id(node), id(node.right))

            self._print_tree(node.left)
            self._print_tree(node.right)

    def add_node(self, _id, label):
        self.dot.node(str(_id), str(label))

    def add_edge(self, start_id, end_id):
        self.dot.edge(str(start_id), str(end_id))


b = BinaryTree()
b.add(10)
b.add(8)
b.add(12)
b.add(9)
b.add(7)
b.add(14)
b.add(11)
b.print_tree()
