import time
import sys
import copy
import networkx as nx
from . import SubGraphMatcher

class GQLMatcher(SubGraphMatcher):
    def __init__(self, G):
        super().__init__(G)
        self.M = {}
        self.filter_rate = 1
        self.en_counter = 1
    
    def clear(self):
        self.MatchingList = []
        self.M = {} 
        self.filter_rate = 1
        self.en_counter = 1

    def filtering(self, q):
        imd = self.LDF(q)
        imd = self.NLF(q, imd)
        imd = self.GQL_local_pruning(q, imd)
        imd = self.GQL_global_refinement(q, imd)
        return imd

    def ordering(self, q, candidates):
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
                self.enumerate(q, imd, order, i + 1)
                del self.M[c[0]]

    def is_subgraph_match(self, q):
        self.clear()
        print("GQL is used...")
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

    def GQL_local_pruning(self, q, candidates):
        res = []
        for c in candidates:
            u, v = c[0], c[1]
            u_profile = self.profile_of_query_node(u, q)
            v_profile = self.profile_of_data_node(v)
            if u_profile.issubset(v_profile):
                res.append((u, v))
        vset = set()
        for c in res:
            vset.add(c[1]) 
        self.filter_rate = len(vset) / len(self.G_nodes)
        print(f"After the GQL local pruning,  { self.filter_rate  * 100}% of the nodes left")
        return res 

    def GQL_global_refinement(self, q, candidates):
        for c in candidates:
            u, v = c[0], c[1]
            n_u = list(q.neighbors(u))
            v_u = list(self.G.neighbors(v))
            for u_prime in n_u: # we want all the u_prime to be matched
                u_prime_matched = False
                for v_prime in v_u:
                    # check if v_prime is u_prime's candidate
                    # -> check (u_prime, v_prime) exists in candidates
                    # if not, than it will not be a fully match
                    # remove (u, v) from candidates
                    match = (u_prime, v_prime)
                    if match in candidates:
                        u_prime_matched = True
                        break
                if u_prime_matched == False:
                    # remove (u, v) from candidates
                    candidates = [c for c in candidates if not (c[1] == v and c[0] == u)]
                    # print(f'{(u, v)} is removed by gql global refinement')
                    break
        vset = set()
        for c in candidates:
            vset.add(c[1]) 
        self.filter_rate = len(vset) / len(self.G_nodes)
        print(f"After GQL global refinement, { self.filter_rate  * 100}% of the nodes left")
        return candidates

    # GQL Compute LC
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
