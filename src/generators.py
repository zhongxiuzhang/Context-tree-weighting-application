import random
import tree

class Generator:
    """Base Generator class"""
    def next(self):
        """Get the next value.
        Returns:
            int: the next value.
        """
        pass
    
    def next_n(self, n):
        """Get the n next values.
        Returns:
            [int]: the next values.
        """
        res = []
        for _ in range(n):
            res.append(self.next())
        return res

class MarkovGen(Generator):
    def __init__(self):
        self.trans = {}
        self.trans[(0, 0)] = [0.3,0.6,0.1]
        self.trans[(0, 1)] = [0,1,0]
        self.trans[(1, 0)] = [0.3,0.6,0.1]
        self.trans[(1, 1)] = [0.2, 0.1, 0.7]
        self.trans[(0, 2)] = [0.2, 0.7, 0.1]
        self.trans[(2, 0)] = [0.3, 0.4 ,0.3]
        self.trans[(1, 2)] = [0.3, 0.5 ,0.2]
        self.trans[(2, 1)] = [0 ,1 ,0]
        self.trans[(2, 2)] = [0.1 ,0 ,0.9]
        self.mem = [0, 0]
    
    def next(self):
        probas = self.trans[(self.mem[-2], self.mem[-1])]
        prob0 = probas[0]
        prob1 = probas[1]
        n = 0
        val = random.random()
        if val < prob0:
            n = 0
        elif prob0 < val < prob1+prob0 :
            n = 1
        else : 
            n = 2
            
        self.mem = [self.mem[-1], n]
        return n
    

class TreeGenerator(Generator):
    def __init__(self, tree):
        self.tree = tree
        self.past = []

    def next(self):
        node = self.tree
        for c in reversed(self.past):
            next_node = node.children[c]
            if next_node:
                node = next_node
            else:
                break
        next_value = random.choices(range(node.m), node.count)[0]
        self.past.append(next_value)
        return next_value