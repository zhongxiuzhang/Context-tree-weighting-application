import tree
import graphviz
import sys
from data import Data
from fractions import Fraction


class ProbNode(tree.Node):
    def get_pm(self, beta):
        """
        Returns:
            Fraction: The Pm probability of this Node, calculated on demand. This value is not stored.
        """
        if self.is_leaf():
            return self.pe
        else:
            left = beta * self.pe
            right = (1 - beta) * \
                tree.product(c.pm for c in self.children if c is not None)
            if left >= right:
                self.should_prune = True
            return max(left, right)

    def compute_probas(self, beta):
        super().compute_probas(beta)
        self.should_prune = False
        self.pm = self.get_pm(beta)

    def prune(self):
        """Prune all nodes marked as so by the Pm computation.
        """
        if self.should_prune:
            self.children = [None] * self.m
        else:
            for c in self.children:
                if c is not None:
                    c.prune()

    def graphviz_label(self):
        return [
            ("pe", "pe", graphviz.str_fraction),
            ("pw", "pw", graphviz.str_fraction),
            ("pm", "pm", graphviz.str_fraction),
            ("as", "count", None)
        ]


def prune_tree_main(data, m, D, beta):
    """Main function for MAPT algorithm.
    Args:
        data ([int]): the input data.
        m (int): the alphabet size.
        D (int): the depth of the tree, also the size of the context.
        beta (Fraction): the beta used by some probabilities computations.
    Returns:
        KTreeNode: the top node of the pruned tree.
    """
    top = ProbNode(None, m)
    tree.debug("Building tree")
    tree.build_counts(top, data, D, lambda value, m: ProbNode(value, m))

    tree.debug("Computing probas")
    top.compute_probas(beta)

    tree.debug("Pruning tree")
    top.prune()
    return top


if __name__ == "__main__":
    path = "../dataprojet2.txt"
    data = Data(path)

    top_tree = prune_tree_main(data.data, m=data.m, D=6, beta=Fraction(1, 2))
    print(graphviz.main_node_to_graphviz(top_tree, only_struct=True))
