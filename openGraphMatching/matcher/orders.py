import sys
import time
import copy
import networkx as nx

class Order():
    def __init__(self, G):
        self.G = G
        self.G_nodes = list(G.nodes())
        self.G_edges = list(G.edges())
        self.G_labels = nx.get_node_attributes(G, 'feat')
        self.G_degree = G.degree()

    def naive_order(self, q, candidates=None):
        return list(q.nodes())

    def gql_order(self, q, candidates):
        print('Using GQL ordering...')
        q_nodes = list(q.nodes())
        res = [[i, 0] for i in q_nodes]
        # Count C(u)
        for c in candidates:
            res[c[0]][1] += 1
        res.sort(key = lambda x: x[1])
        res.reverse()
        res = [i[0] for i in res]
        return res

