from typing import SupportsBytes


import time
import networkx as nx
from SubGraphMatcher import SubGraphMatcher

class GQLMatcher(SubGraphMatcher):
    def __init__(self, G):
        super().__init__(G)
        self.M = {}
        self.filter_rate = 1
        self.en_counter = 1 # What is the en_counter BTW


    def filtering(self, q):
        imd = self.LDF(q)
        print(imd)


    def find_subgraph_match(self, q, imd, order):
        return 0