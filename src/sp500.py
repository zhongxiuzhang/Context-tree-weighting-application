import prob_tree
import kTree
import csv
from fractions import Fraction
import graphviz
import tree
from data import Data

# path = "./input_data/GSPC.csv"
# data = []
# with open(path) as f:
#     reader = csv.DictReader(f)
#     for row in reader:
#         data.append(float(row["Adj Close"]))

# diff = []
# for (a, b) in zip(data, data[1:]):
#     diff.append(b / a * 100 - 100)

# data = []
# for d in diff:
#     v = None
#     if d <= -5:
#         v = 0
#     elif -5 < d and d <= -3:
#         v = 1
#     elif -3 < d and d <= -1:
#         v = 2
#     elif -1 < d and d <= 1:
#         v = 3
#     elif 1 < d and d <= 3:
#         v = 4
#     elif 3 < d and d <= 5:
#         v = 5
#     elif d > 5:
#         v = 6
#     data.append(v)

alphabet_size = 4
tree_depth = 9
beta = Fraction(1, 2)

path = "./return_class_train.txt"
#path = "./sp500_class.txt"
data_ = Data(path)
data = data_.data

top = prob_tree.prune_tree_main(data, alphabet_size, tree_depth, beta)
prob = top.pw
# print(float(top.compute_pi_T_x(beta, tree_depth, prob)))
print(graphviz.main_node_to_graphviz(top))