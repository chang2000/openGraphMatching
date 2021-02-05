import time
import sys
import copy
import networkx as nx
from . import BaseMatcher
from . import filters as f
from . import orders as o
from . import enumeraters as e

class GQLMatcher(BaseMatcher):
    def __init__(self, G):
        super().__init__(G)
    
    def clear(self):
        self.MatchingList = []
        self.M = {} 
        self.filter_rate = 1
        self.en_counter = 1

    def filtering(self, q):
        prefilter = f.Filter(self.G)
        return prefilter.gql_filtering(q)

    def ordering(self, q, candidates):
        orderer = o.Order(self.G)
        return orderer.gql_order(q, candidates)


    def enumerate(self, q, imd, order, i):
        enu = e.Enumerater(self.G)
        enu.normal_enum(q, imd, order, i)
        return enu.res_getter()

    def is_subgraph_match(self, q):
        self.clear()
        print("GQL Running")
        main_start_time = time.time()
        # init the current matching first
        self.filter_rate = 1
        self.MachingList = []
        self.M = {}
        try:
            assert (isinstance(q, nx.classes.graph.Graph) and nx.is_connected(q))
        except:
            print('Input query graph must be a single networkx instance.')
            sys.exit()
        # Turn on / off the time -- verbose mode
        candidates = self.filtering(q)
        order = self.ordering(q, candidates)

        print('enumerating...')
        en_time = time.time() 
        match_list = self.enumerate(q, candidates, order, 1)
        print(f'enumeration done, takes {time.time() - en_time}s')
        print("--- %s seconds ---, Job done" % (time.time() - main_start_time))
        print(f"Totally find {len(match_list)} matches.")
        print(' ')
        return match_list