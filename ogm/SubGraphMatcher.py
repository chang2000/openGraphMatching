import abc
import sys
import time
import networkx as nx

class SubGraphMatcher(abc.ABC):
    def __init__(self, G):
        self.G = G
        self.G_nodes = list(G.nodes())
        self.G_edges = list(G.edges())
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
    
    @abc.abstractclassmethod
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