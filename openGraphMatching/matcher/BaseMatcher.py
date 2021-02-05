import abc
from abc import abstractmethod
import sys
import time
import copy
import networkx as nx
from . import filters as f
from . import orders as o
from . import enumeraters as e

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
        return res

    def ordering(self, q, candidates):
        orderer = o.Order(self.G)
        return orderer.naive_order(q, None)
    
    # @abc.abstractclassmethod
    def find_subgraph_match(self, q, imd, order):
        pass

    def enumerate(self, q, imd, order, i):
        enu = e.Enumerater(self.G)
        enu.normal_enum(q, imd, order, i)
        return enu.res_getter()
    
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
        match_list = self.enumerate(q, imd, order, 1)
        print("--- %s seconds ---, Job done" % (time.time() - main_start_time)) 
        return match_list