# -*- coding: utf-8 -*-

from fractions import Fraction
import sys
import generators
import graphviz
import numpy as np
import tree
import math
from data import Data


def ij_iterator(kj, m):
    """Utility function that yields all elements of {i | 1 <= i <= kj} ^ m
    Yields:
        (int) * m: the current element of the set.
    """
    r = range(1, kj + 1)
    if m == 1:
        for i in r:
            yield (i,)
    else:
        for left in ij_iterator(kj, m - 1):
            for i in r:
                yield (*left, i)


class KTreeNode(tree.Node):
    def __init__(self, value, m, k):
        """Constructs a KTreeNode to be used in a tree.

        Args:
            value (int|None): The value to be stored in this node.
            m (int): the alphabet size.
            k (int): the number of trees requested.
        """
        super().__init__(value, m)
        self.k = k
        self.pms = [Fraction(0) for _ in range(k)]
        self.Bs = np.full((k, m), -1)

    def clone_without_children(self):
        """Clone this node without its children.
        Returns:
            KTreeNode: a node with the same value, m, k, count, pe, pms and Bs but without children.
        """
        node = KTreeNode(self.value, self.m, self.k)
        node.count = list(c for c in self.count)
        node.pe = self.pe
        node.pms = list(p for p in self.pms)
        node.Bs = np.copy(self.Bs)
        return node

    def graphviz_label(self):
        return [
            ("log(pe)", "pe", lambda value: tree.log10_fraction(value)),
            ("as", "count", None),
            ("pms", "pms", graphviz.str_fraction_array),
            ("Bs", "Bs", graphviz.str_matrix)
        ]


def build_full_tree(m, k, D):
    """Build a new m-ary tree of depth D.
    Args:
        m (int): the alphabet size.
        k (int): the number of trees requested (used for building the nodes).
        D (int): the depth of the tree.
    Returns:
        KTreeNode: the top node of the tree.
    """
    def build_node(value, m, k, depth_to_go):
        node = KTreeNode(value, m, k)
        if depth_to_go != 0:
            children = list(build_node(i, m, k, depth_to_go - 1)
                            for i in range(m))
            node.children = children
        return node
    return build_node(None, m, k, D - 1)


def build_matrix(node, m, k, D, beta):
    """Compute k-tree algorithm matrices for each node of the tree.
    Args:
        node (KTreeNode): the top node of the tree.
        m (int): the alphabet size.
        k (int): the number of trees requested.
        D (int): the depth of the tree.
    Returns:
        int: the kj of this node.
    """
    if node.is_leaf():
        node.pms[0] = node.pe
        node.Bs[0] = np.zeros((1, m), dtype=np.int64)
        return 1
    else:
        kjs = [build_matrix(c, m, k, D, beta) for c in node.children]
        kj = min(kjs)

        probas = [(beta * node.pe, np.zeros((1, m)))]
        for ijs in ij_iterator(kj, m):
            p = 1 - beta
            for j in range(m):
                p *= node.children[j].pms[ijs[j] - 1]
            probas.append((p, np.array(ijs)))

        # sort by proba in desc order
        probas.sort(key=lambda p: p[0], reverse=True)

        for i, (prob, vec) in enumerate(probas[:k]):  # we only keep k of them
            node.pms[i] = prob
            node.Bs[i] = vec
        # assert node.Bs.shape == (k, m)
        return min(k, kj + 1)


def extract_tree(node, ki):
    """Extracts the ki best-tree.
    Args:
        node (KTreeNode): the top node of the tree.
        ki (int): the 0-based index of the tree requested. 0 <= ki < k
    Returns:
        (KNodeTree, Fraction): the ki-best tree and the Pm associated with it
    """
    def inner(node, ki):
        """Extracts the ki best-tree. This function only returns the tree."""
        row = node.Bs[ki]
        new_node = node.clone_without_children()
        if all(elem == 0 for elem in row):
            return new_node
        else:
            new_children = list(inner(c, int(r) - 1)
                                for c, r in zip(node.children, row))
            new_node.children = new_children
            return new_node
    ki_tree = inner(node, ki)
    pm = ki_tree.pms[ki]
    return (ki_tree, pm)


def ktree_main(data, m, D, k, beta):
    """Main function for ktree algorithm.
    Args:
        data ([int]): the input data.
        m (int): the alphabet size.
        D (int): the depth of the tree, also the size of the context.
        k (int): the number of trees requested.
        beta (Fraction): the beta used by some probabilities computations.
    Returns:
        [KNodeTree]: returns the full tree and all k best trees
    """
    tree.debug("Building full tree")
    top = build_full_tree(m, k, D)

    tree.debug("Building counts")
    tree.build_counts(top, data, D, None)

    tree.debug("Computing probas")
    top.compute_probas(beta)

    tree.debug("Building matrix")
    build_matrix(top, m, k, D, beta)

    trees = []
    for score in range(k):
        tree.debug("Extracting tree {}".format(score))
        next_tree = extract_tree(top, score)
        trees.append(next_tree)
    return (top, trees)


if __name__ == "__main__":
    path = "./return_class_train.txt"
    #path = "./sp500_class.txt"
    #path = "../dataprojet2.txt"

    # input_bits = [0, 1, 2, 2, 1, 0]
    # input_bits=[0,1,0,1,1,1,0,1,0,1,0,1,0,1]

    # input_bits = [2, 0, 1, 0, 2, 1, 1, 0, 2, 0, 1, 0, 2, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1, 0, 2, 1, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 1, 1, 0, 2]
    # input_bits = generators.MarkovGen().next_n(5000)
    data = Data(path)
    D = 9
    beta = Fraction(1, 2)
    top, trees = ktree_main(data.data, m=data.m, D=D, k=5, beta=beta)

    if len(sys.argv) > 1 and sys.argv[1] == "html":
        pw = top.pw
        trees_probs = [(t, t.compute_pi_T_x(beta, D, pw)) for t, _ in trees]
        print(graphviz.multiple_trees_to_html(trees_probs, only_struct=True))
    else:
        for tree, _ in trees:
            print(graphviz.main_node_to_graphviz(tree))
