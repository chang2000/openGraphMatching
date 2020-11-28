import abc
from abc import abstractmethod
import sys
import time
import copy
import networkx as nx

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
        res = []
        q_labels = nx.get_node_attributes(q, 'feat')
        for u in q.nodes():
            for v in self.G_nodes:
                if self.G_labels[v] == q_labels[u]:
                    res.append((u, v))
        return res

    def ordering(self, q, candidates):
        res = list(q.nodes())
        res.reverse()
        return res
    
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
                print(f"#{self.en_counter-1} round match {self.M}")
                self.enumerate(q, imd, order, i + 1)
                del self.M[c[0]]

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
        print()
        output_data = [self.filter_rate, self.MatchingList]
        return output_data

    def LDF(self, q):
        """
        This function takes in a query graph and a target graph
        Returns a list of all the candidate vertex for each node in q filtered by LDF

        LDF: L(v) = L(u) and d(v) > d(u), as v in the candidate vertex
        """
        print('Running LDF...')
        # Add Time Stamp
        start_time = time.time()
        res = []
        q_degree = q.degree()
        q_labels = nx.get_node_attributes(q, 'feat')

        # For monitering the filtering outcome
        v_set = set()

        for u in q.nodes():
            for v in self.G_nodes:
                if  self.G_labels[v] == q_labels[u] and self.G_degree[v] >= q_degree[u]:
                    res.append((u, v))

        for c in res:
            v_set.add(c[1]) 
        self.filter_rate = len(v_set) / len(self.G_nodes)
        print("--- %s seconds ---, LDF Done" % (time.time() - start_time))
        print(f"After LDF, { self.filter_rate  * 100}% of the nodes left")
        return res

    def NLF(self, q, candidates):
        """
        This function takes in a query graph and a target graph

        candidates is a list of tuples, the first element is u, the second element is the 
        candidate vertex v corresponding to u

        Returns a list of all the candidate vertex for each node in q filtered by NLF

        NLF: Use N(u) to prune C(u). 
            if there are l in L(N(u)) such that |N(u, l)| > |N(v, l)| 
                then remove v from C(u)

            Here L(N(u)) -> {L(u')| u' in N(u)} 
                 N(u,l) = {u' in N(u) | L(u') = l}
        """
        print('running NLF...')
        start_time = time.time()
        q_labels = nx.get_node_attributes(q, 'feat')
        # generate L(N(u)), the whole is a list of sets
        labels_of_neighbor = []
        for u in q.nodes():
            neighbors = q.neighbors(u)
            s = set()
            for n in neighbors:
                s.add(q_labels[n])
            labels_of_neighbor.append([u, s])
        v_set = set()
        can_copy = copy.deepcopy(candidates)
        # How about generate them before
        # ALERT! SLOWNESS
        u_neighbors_list = [list(q.neighbors(u)) for u in q.nodes()]
        v_neighbors_list = [list(self.G.neighbors(v)) for v in self.G_nodes]

        for u, v in can_copy: 
            q_feats = [q_labels[n] for n in u_neighbors_list[u]]
            G_feats = [self.G_labels[n] for n in v_neighbors_list[v]]
            for l in labels_of_neighbor[u][1]:
                # Compute N(u, l)
                nul = q_feats.count(l)
                # Compute N(v, l)
                nvl = G_feats.count(l)
                if nul > nvl:
                    candidates = [c for c in candidates if not (c[0] == u and c[1] == v)]

        for u, v in candidates:
            v_set.add(v)
        print("--- %s seconds ---, NLF Done" % (time.time() - start_time))
        print(f"After the filtering, {len(v_set) / len(self.G_nodes)  * 100}% of the nodes left")
        self.filter_rate = len(v_set) / len(self.G_nodes)
        return candidates

    def profile_of_query_node(self, node_index, graph):
        """
        Return a set that contains all the labels of the given
        node's 1-hop neighbors.
        """
        graph_labels = nx.get_node_attributes(graph, 'feat')
        # print(graph_labels)
        neighbors = list(graph.neighbors(node_index))
        # print(neighbors)
        profile = set()
        for n in neighbors:
            profile.add(graph_labels[n])
        return profile

    def profile_of_data_node(self, node_index):
        neighbors = list(self.G.neighbors(node_index))
        profile = set()
        for n in neighbors:
            profile.add(self.G_labels[n])
        return profile

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
