import subprocess
import sys
import tree

class GraphvizDrawer:
    def __init__(self):
        """Constructs a new Drawer.
        """
        self.counter = 0
        self.s = "digraph nodes {\n\tnode [shape=record];\n"

    def next_name(self):
        """Get a new unique node name.
        Returns:
            string: a new unique node name.
        """
        i = self.counter
        self.counter += 1
        return "name{}".format(i)

    def add_node(self, name, label,max_index):
        """Add a node to the graph.
        Params:
            name (string): the name of the node.
            label (string): the label of the node.
        """
        if(max_index==0):
            self.s += "\t{} [fontcolor=red, label=\"{}\"];\n".format(name, label)
        elif(max_index==1):
            self.s += "\t{} [fontcolor=orange, label=\"{}\"];\n".format(name, label)
        elif(max_index==2):
            self.s += "\t{} [fontcolor=lightskyblue, label=\"{}\"];\n".format(name, label)
        elif(max_index==3):
            self.s += "\t{} [fontcolor=green, label=\"{}\"];\n".format(name, label)
        else:
            self.s += "\t{} [label=\"{}\"];\n".format(name, label)
        #self.s += "\t{} [fontcolor=red, label=\"{}\"];\n".format(name, label)
    
    def add_edge(self, node1, node2, label):
        """Add an edge to the graph.
        Params:
            node1 (string): the name of the first node.
            node2 (string): the name of the second node.
            label (string): the label of the edge.
        """
        self.s += "\t{} -> {} [label={}];\n".format(node1, node2, label)

    def add_tree_node(self, node, only_struct):
        """Add a tree node to the graph.
        Params:
            node (Node): node to add to the graph.
            only_struct (bool): allows to not draw the label of the node.
                Used to only show the structure of the tree.
        Returns:
            string: the name of the node added (to build edges).
        """

        def build_label(node):
            """Build the label according to the node graphviz description"""
            label = "{"
            elems = []
            for (attr_name, attr, func) in node.graphviz_label():
                value = getattr(node, attr)
                if func is not None:
                    value = func(value)
                elems.append("{}={}".format(attr_name, value))
                #elems.append('abc')
                #elems.append('<font color=\'red\'>{}={}</font>'.format(attr_name, value))
                #elems.append('\033[1;35m{}={}\033[0m'.format(attr_name, value))
            label += " | ".join(elems)
            label += "}"
            return label

        name = self.next_name()
        label = build_label(node) if not only_struct else ""
        if node.is_leaf():
            max_index=node.count.index(max(node.count))
        else:
            max_index=5
        self.add_node(name, label, max_index)

        for c in node.children:
            if c is not None:
                sub_name = self.add_tree_node(c, only_struct)
                self.add_edge(name, sub_name, c.value)
        return name

    def build(self):
        """End drawing and build final string
        Returns:
            string: the graphviz description of the graph.
        """
        return self.s + "}\n"

def str_fraction_array(arr):
    """Utility fonction to print fraction arrays."""
    return [str_fraction(elem) for elem in arr]

def str_fraction(f):
    """Utility fonction to print fractions."""
    return float(f) if f else 0.0

def str_matrix(Bs):
    """Utility fonction to print matrix (mainly Bs)."""
    res = "\\n"
    for row in Bs:
        if all(elem == 0 for elem in row):
            res += "[{}]".format(", ".join(["*"] * len(row)))
        else:
            res += str(row)
        res += "\\n"
    return res


def main_node_to_graphviz(node, only_struct=False):
    """Get graphviz description of a node tree
    Args:
        node (Node): the top node of the tree.
        only_struct (bool=False): allows to not draw the label of the node.
            Used to only show the structure of the tree.
    Returns:
        string: The graphviz description of the tree.
    """
    drawer = GraphvizDrawer()
    drawer.add_tree_node(node, only_struct)
    return drawer.build()

def multiple_trees_to_html(trees, only_struct=False):
    """Get html page from multiple trees. Requires dot to be installed and in path.
    Args:
        trees ([(Node, Fraction)]): the trees and probabilities to display.
        only_struct (bool=False): allows to not draw the label of the node.
            Used to only show the structure of the tree.
    Returns:
        string: the content of the html page.
    """

    def dot2svg(dot_content):
        cmd = ["dot", "-Tsvg"]
        with subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE) as proc:
            proc.stdin.write(dot_content.encode())
            proc.stdin.close()
            output = proc.stdout.read()
            return output.decode()

    def remove_header(svg):
        lines = []
        in_svg = False
        for line in svg.split("\n"):
            if in_svg:
                lines.append(line + "\n")
            elif line.lstrip().startswith("<svg"):
                in_svg = True
                lines.append(line + "\n")
        return "".join(lines)
    
    def proba_desc(best, prob):
        if best is None:
            return "pi(T|x) = {}".format(float(prob))
        else:
            ratio = best / prob
            #while ratio < 1.0:
            #    ratio *= 10
            return "Ratio probas = {}".format(float(ratio))
    
    html_trees = []
    best_proba = None

    for (index, (t, prob)) in enumerate(trees):
        dot_content = main_node_to_graphviz(t, only_struct)
        svg = remove_header(dot2svg(dot_content))
        title = "Arbre {}. {}".format(index + 1, proba_desc(best_proba, prob))
        html_tree = "<div class=\"tree_box\">\n<h1>{}</h1>\n<div class=\"tree\">{}</div>\n</div>\n".format(title, svg)
        html_trees.append(html_tree)
        if best_proba is None:
            best_proba = prob
    
    page = """
    <!doctype html>
    <html lang="fr">
    <head>
        <style>
            main {{
                display: flex;
            }}
            .tree {{
                padding: 3px;
            }}
            .tree_box {{
                margin: 20px;
            }}
        </style>
    </head>
    <body><main>{}</main></body>
    </html>""".format("".join(html_trees))
    return page