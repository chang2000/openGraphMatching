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
        res = {}
        for i in q_nodes:
            res[i] = 0
        # Count C(u)
        for c in candidates:
            res[c[0]] += 1
        newdic = sorted(res.items(), key=lambda x: x[1], reverse=True)
        ans = [ele[0] for ele in newdic]
        return ans

