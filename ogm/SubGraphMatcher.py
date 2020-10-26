import abc
from abc import abstractmethod
import sys
import time
import networkx as nx

class SubGraphMatcher(abc.ABC):
    def __init__(self, G):
        self.G = G
        self.G_nodes = list(G.nodes())
        self.G_edges = list(G.edges())
        # self.G_labels = nx.get_edge_attributes(G, 'feat')
        self.G_degree = G.degree()
        self.MatchingList = []

    def filtering(self, q):
        ''' Filter candidate vertices in the target graph
        '''
        res = []
        for u in q.nodes():
            for v in self.G_nodes:
                res.append((u, v))
        return res

    def ordering(self, q, order):
        return order
    
    # @abc.abstractclassmethod
    def find_subgraph_match(self, q, imd, order):
        ''' Enumerate partial results
        '''
        pass
    
    def is_subgraph_match(self, q):
        try:
            assert (isinstance(q, nx.classes.graph.Graph) and nx.is_connected(q))
        except:
            print('Input query graph must be a single connected networkx instance.')
            sys.exit()
        main_start_time = time.time()
        imd = self.filtering(q)
        order = self.ordering(q, imd)
        data = self.find_subgraph_match(q, imd, order)
        print("--- %s seconds ---, Job done" % (time.time() - main_start_time)) 
        print()
        return data

    def LDF(self, q):
        """
        This function takes in a query graph and a target graph
        Returns a list of all the candidate vertex for each node in q filtered by LDF

        LDF: L(v) = L(u) and d(v) > d(u), as v in the candidate vertex
        """
        # Add Time Stamp
        print('Running LDF...')
        start_time = time.time()
        res = []
        q_degree = q.degree()
        q_labels = nx.get_node_attributes(q, 'feat')
        G_labels = nx.get_node_attributes(self.G, 'feat')
        v_set = set()
        for u in q.nodes():
            for v in self.G_nodes:
                if self.G_degree[v] >= q_degree[u]:
                    if G_labels[v] == q_labels[u]:
                        res.append((u, v))
        for c in res:
            v_set.add(c[1]) 
        self.filter_rate = len(v_set) / len(self.G_nodes)
        print("--- %s seconds ---, LDF Done" % (time.time() - start_time))
        print(f"After the filtering, { self.filter_rate  * 100}% of the nodes left")
        return res