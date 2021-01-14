import time
import sys
import copy
import networkx as nx
from . import BaseMatcher

class QuickSIMatcher(BaseMatcher):
    def __init__(self, G):
        super().__init__(G)
        self.M = {}
        self.filter_rate = 1

    def filtering(self, q):
        print('Using naive filtering...')
        imd = self.LDF(q)
        imd = self.NLF(q, imd)
        return imd

    # For ordering, no need to implement ordering here
    
    # Take care of this one
    def enumerate(self, q, candidates, order, i):
        print("Running QuickSI...")
        self.en_counter += 1
        if i == len(order) + 1:
            if self.M != None:
                if len(self.M) == len(list(q.nodes())):
                    M_copy = copy.deepcopy(self.M)
                    self.MatchingList.append(M_copy)
            return self.M
        
        # u is a extenable vertex
        u = self.get_extenable_vertex(order, i)
        lc = self.computeLC(q, candidates, order, u, i)
        for c in lc:
            if c not in self.M and c[1] not in self.M.values():
                self.M[c[0]] = c[1]
                self.enumerate(q, candidates, order, i + 1)
                del self.M[c[0]]

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

    def is_subgraph_match(self, q): 
        print('Naive match is used...')

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

        # Turn on / off the time
        candidates = self.filtering(q)
        order = self.ordering(q, candidates)

        print('enumerating...')
        en_time = time.time() 
        self.enumerate(q, candidates, order, 1)
        print(f'enumeration done, takes {time.time() - en_time}s')
        print(f'enumeration runs {self.en_counter} times')
        print("--- %s seconds ---, Job done" % (time.time() - main_start_time))
        print(f"Totally find {len(self.MatchingList)} matches.")
        print(' ')
        print(' ')
        output_data = [self.filter_rate, self.MatchingList]
        # print(output_data)
        return output_data
