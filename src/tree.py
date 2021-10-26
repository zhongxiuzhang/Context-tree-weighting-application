from fractions import Fraction
import graphviz
import sys
import math


class Node:
    def __init__(self, value, m):
        """Constructs a Node to be used in a tree.

        Args:
            value (int|None): The value to be stored in this node.
            m (int): The alphabet size.
        """
        self.m = m
        self.value = value
        self.children = [None] * m
        self.count = [0] * m
        self.pe = None
        self.pw = None

    def count_leaves_at_depth(self, D, current_depth=1):
        return sum(1 for n in build_node_iter(self, at_depth=D) if n.is_leaf())

    def count_leaves(self):
        return sum(1 for n in build_node_iter(self) if n.is_leaf())

    def is_leaf(self):
        """
        Returns:
            bool: True if the node is a leaf ie. if it has no children.
        """
        return all(c is None for c in self.children)

    def get_pe(self):
        """
        Returns:
            Fraction: The Pe probability of this Node, calculated on demand. This value is not stored.
        """
        Ms = sum(self.count)
        m = self.m

        if Ms == 0:
            return Fraction(1, 1)

        num = 1
        for j in range(m):
            for i in range(self.count[j]):
                num *= 2 * i + 1
    
        den = 1
        for i in range(Ms):
            den *= 2 * i + m

        return Fraction(num, den)

    def get_pw(self, beta):
        """
        Returns:
            Fraction: The Pw probability of this Node, calculated on demand. This value is not stored.
        """
        if self.is_leaf():
            return self.pe
        else:
            sub = (1 - beta) * product(c.pw for c in self.children if c is not None)
            return beta * self.pe + sub

    def compute_probas(self, beta):
        """Compute all required probability on this Node. And store those values.
        Args:
            beta (Fraction): The beta value used in some probabilities.
        """
        for c in self.children:
            if c is not None:
                c.compute_probas(beta)
        self.pe = self.get_pe()
        self.pw = self.get_pw(beta)

    def compute_pi_T(self, beta, D):
        """Compute pi(T) for this top node.
        Args:
            beta (Fraction): the beta used by some probabilities computations.
            D (int): the depth of the tree, also the size of the context.
        Returns:
            Fraction: pi(T)
        """
        alpha = math.pow(1 - beta, 1 / (self.m - 1))
        cardT = self.count_leaves()
        Ld = self.count_leaves_at_depth(D)
        return Fraction(math.pow(alpha, cardT - 1)) * Fraction(math.pow(beta, cardT - Ld))

    def compute_pi_T_x(self, beta, D, prob):
        """Compute pi(T|x) for this top node.
        Args:
            beta (Fraction): the beta used by some probabilities computations.
            D (int): the depth of the tree, also the size of the context.
        Returns:
            Fraction: pi(T|x)
        """
        piT = self.compute_pi_T(beta, D)
        PxT = product(n.pe for n in build_node_iter(self) if n.is_leaf())
        return (PxT * piT) / prob

    def graphviz_label(self):
        """Description of interesting fields of the Node to be used by Graphviz.
        Returns:
            [(string, string, T -> value)]:
                the first element is the field name to be display,
                the second element is the name of the field attr ("pe" would be used if you want self.pe),
                the third element is the function to be used to convert to string, or None if you want the default __str__().
        """
        return [
            ("pe", "pe", graphviz.str_fraction),
            ("as", "count", None)
        ]

def build_node_iter(top_node, at_depth=None, current_depth=1):
    if at_depth is None:
        for c in top_node.children:
            if c is not None:
                for n in build_node_iter(c):
                    yield n
        yield top_node
    elif current_depth == at_depth:
        yield top_node
    else:
        for c in top_node.children:
            if c is not None:
                for n in build_node_iter(c, at_depth, current_depth + 1):
                    yield n


def build_counts(top_node, data, D, node_builder):
    """Complete the counts vector using some input data.
    Args:
        top_node (Node): the top node of the tree.
        data ([int]): the input data.
        D (int): the context size.
        node_builder ((int, int) -> Node): a node builder used when inserting a Node is needed.
            It takes the value of the node and the alphabet size as parameters.
    """
    m = top_node.m
    for width in range(1, D+1):
        for start in range(len(data) - width + 1):
            context = data[start:start+width]
            value = context[-1]
            pre = context[:-1]
            insert_node = top_node
            for c in reversed(pre):
                # shouldn't append in kTree so we can build a Node and not a KTreeNode
                if insert_node.children[c] is None:
                    insert_node.children[c] = node_builder(c, m)
                insert_node = insert_node.children[c]
            insert_node.count[value] += 1


def product(iter):
    """Utility product function
    Args:
        iter ([Fraction]): the elements to be used
    Returns:
        Fraction: the product of all the elements of iter
    """
    res = Fraction(1, 1)
    for elem in iter:
        res *= elem
    return res


def debug(*args):
    """Utility function to print message to sderr.
    Args:
        args (object): the elements to print.
    """
    print(*args, file=sys.stderr)

def log10_fraction(f):
    return math.log10(f.numerator) - math.log10(f.denominator)