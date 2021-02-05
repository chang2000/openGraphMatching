import abc
from abc import abstractmethod
import sys
import time
import copy
import networkx as nx
from . import filters as f
from . import orders as o

class BaseMatcher(abc.ABC):
    def __init__(self, G):
        self.G = G
        self.G_nodes = list(G.nodes())
        self.G_edges = list(G.edges())
        self.G_labels = nx.get_node_attributes(G, 'feat')
        self.G_degree = G.degree()
        self.MatchingList = []
        self.en_counter = 1
        self.M = {}
        self.filter_rate = 1

    def filtering(self, q):
        ''' Filter candidate vertices in the target graph
        '''
        prefilter = f.Filter(self.G)
        res = prefilter.ldf(q)
        res = prefilter.nlf(q, res)
        return res

    def ordering(self, q, candidates):
        orderer = o.Order(self.G)
        return orderer.naive_order(q, None)
    
    # @abc.abstractclassmethod
    def find_subgraph_match(self, q, imd, order):
        pass

    
    def enumerate(self, q, imd, order, i):
        self.en_counter += 1
        if i == len(order) + 1:
            if self.M != None:
                if len(self.M) == len(list(q.nodes())):
                    M_copy = copy.deepcopy(self.M)
                    self.MatchingList.append(M_copy)
            return self.M
        # v is a extenable vertex
        u = self.get_extenable_vertex(order, i)
        lc = self.computeLC(q, imd, order, u, i)
        # print(f'the local candidates for {u} is {lc}')
        for c in lc:
            if c not in self.M and c[1] not in self.M.values():
                self.M[c[0]] = c[1]
                # print(f"#{self.en_counter-1} round match {self.M}")
                self.enumerate(q, imd, order, i + 1)
                del self.M[c[0]]

    """ The core function will be used in different matchers.
    """
    def is_subgraph_match(self, q):
        try:
            assert (isinstance(q, nx.classes.graph.Graph) and nx.is_connected(q))
        except:
            print('Input query graph must be a single connected networkx instance.')
            sys.exit()
        main_start_time = time.time()
        imd = self.filtering(q)
        order = self.ordering(q, imd)
        data = self.enumerate(q, imd, order, 1)
        print("--- %s seconds ---, Job done" % (time.time() - main_start_time)) 

        output_data = [self.filter_rate, self.MatchingList]
        return output_data


    def plain_candidates(self, q):
        res = []
        for u in q.nodes():
            for v in self.G_nodes:
                res.append((u, v))
        return res

    # Methods used in the enumration part
    def backward_neighbors(self, u, order, q):
        res = set()
        neighbors = list(q.neighbors(u))
        ns = [n for n in neighbors if n in list(self.M.keys())]
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
                    edge = [v[1], self.M[u_prime]]
                    edge.sort()
                    if  tuple(edge) not in self.G_edges:
                        flag = False
                        break
                if flag == True: # might have a sequence error
                    lc.append(v)
        return lc
