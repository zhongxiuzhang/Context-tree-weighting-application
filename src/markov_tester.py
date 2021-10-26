import prob_tree
import generators
from fractions import Fraction
import sys
import graphviz

N = 20000
input_bits = generators.MarkovGen().next_n(N)
m = 3
D = 6
beta = Fraction(3, 4)
# print(input_bits, file=sys.stderr)
tree = prob_tree.prune_tree_main(input_bits, m, D, beta)
next_bits = generators.TreeGenerator(tree).next_n(N)
# print(next_bits, file=sys.stderr)
next_tree = prob_tree.prune_tree_main(next_bits, m, D, beta)
print(graphviz.main_node_to_graphviz(tree))
print(graphviz.main_node_to_graphviz(next_tree))