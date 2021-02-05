import time
import copy
import networkx as nx

class Enumerater():
    def __init__(self, G):
        self.G = G
        self.G_nodes = list(G.nodes())
        self.G_edges = list(G.edges())
        self.G_labels = nx.get_node_attributes(G, 'feat')
        self.G_degree = G.degree()
        self.curr_match = {}
        self.match_list = []
    
    def res_getter(self):
        return self.match_list

    # Works when label are already checked
    def normal_enum(self, q, candidates, order, i):  
        if i == len(order) + 1:
            if self.curr_match != None and len(self.curr_match) == len(list(q.nodes())):
                self.match_list.append(copy.deepcopy(self.curr_match))
            return self.match_list

        u = self.get_extenable_vertex(order, i)
        lc = self.computeLC(q, candidates, order, u, i)

        for c in lc:
            if c not in self.curr_match and c[1] not in self.curr_match.values(): # no qualified candidates
                self.curr_match[c[0]] = c[1]
                self.normal_enum(q, candidates, order, i+1)
                del self.curr_match[c[0]]

    def backward_neighbors(self, u, order, q):
        res = set()
        neighbors = list(q.neighbors(u))
        ns = [n for n in neighbors if n in list(self.curr_match.keys())]
        res.update(ns)
        return list(res)

    def get_extenable_vertex(self, order, i):
        return order[i - 1]

    def computeLC(self, q, C, order, u, i):
        if i == 1: # do not care the edge
            return [c for c in C if c[0] == u]
        lc = []
        # examine the edge
        flag = False
        bn = self.backward_neighbors(u, order, q)
        # print(f'bn for {u} is {bn}')
        for v in C:
            if v[0] == u:
                flag = True
                # for u_prime in self.backward_neighbors(u, order, q):
                for u_prime in bn:
                    edge = [v[1], self.curr_match[u_prime]]
                    edge.sort()
                    if  tuple(edge) not in self.G_edges:
                        flag = False
                        break
                if flag == True: # might have a sequence error
                    lc.append(v)
        return lc