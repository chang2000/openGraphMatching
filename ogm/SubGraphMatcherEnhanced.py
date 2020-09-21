import networkx as nx
from itertools import combinations
import matplotlib.pyplot as plt
import sys
import copy
import time


class SubGraphMatcher:
    def __init__(self, G):
        """
        G_q: the query graph
        G: the target graph

        Examples:
        -------
        >>> import SubGraphMatcher
        >>> G = nx.path_graph(4)
        >>> G_q = nx.path_graph(2)
        >>> SGM = SubGraphMatcher(G)
        >>> SGM.is_subgraph_match(G_q)
            A list of matching
        """
        self.G = G
        self.G_nodes = list(G.nodes())
        self.M = {} # M is a dict
        self.MatchingList = []

    def draw_check_result(self, check_result):
        if check_result != None:
            # add node id to the label
            pos = nx.spring_layout(self.G)
            options = { 'node_size': 400 }
            subgraph = self.G.subgraph(list(check_result))
            nx.draw_networkx_nodes(
                    self.G, 
                    pos, 
                    nodelist=list(self.G.nodes()), 
                    node_color='yellow', 
                    **options)
            # Draw the subgraph nodes
            nx.draw_networkx_nodes(self.G, 
                    pos, 
                    nodelist=list(subgraph.nodes()), 
                    node_color='red', 
                    **options)

            # Draw all the edges
            nx.draw_networkx_edges(
                    self.G, 
                    pos, 
                    edgelist=list(self.G.edges()), 
                    width=3, 
                    edge_color='black')
            # Draw the subgraph edges
            nx.draw_networkx_edges(
                    self.G, 
                    pos, 
                    edgelist=list(subgraph.edges()), 
                    width=3, 
                    edge_color='red')
            labels = nx.get_node_attributes(self.G, 'feat') 
            for i in range(len(labels)):
                labels[i] = str(i) +  ','+ labels[i]
            nx.draw_networkx_labels(self.G, pos, labels, font_size=10)
            plt.show()

    # 如何复用计算方式
    def check_match_from_subgraphs(self, G_q_list):
        try:
            assert (isinstance(G_q_list, list))
        except:
            print('Input queries must be a list')
            sys.exit()
        pass
    
    # The Enhanced version

    # Basic Methods on filtering
    def LDF(self, q, G):
        """
        This function takes in a query graph and a target graph
        Returns a list of all the candidate vertex for each node in q filtered by LDF

        LDF: L(v) = L(u) and d(v) > d(u), as v in the candidate vertex
        """
        # Add Time Stamp
        start_time = time.time()
        res = []
        q_degree = q.degree()
        G_degree = G.degree()
        q_labels = nx.get_node_attributes(q, 'feat')
        G_labels = nx.get_node_attributes(G, 'feat')

        for u in q.nodes():
            for v in G.nodes():
                if G_degree[v] >= q_degree[u]:
                    if G_labels[v] == q_labels[u]:
                        res.append((u,v))
        print("--- %s seconds ---, LDF Done" % (time.time() - start_time))
        return res

    def NLF(self, q, G, candidates):
        """
        This function takes in a query graph and a target graph

        candidates is a list of tuples, the first element is u, the second element is the 
        candidate vertex of u

        Returns a list of all the candidate vertex for each node in q filtered by NLF

        NLF: Use N(u) to prune C(u). 
            if there are l in L(N(u)) such that |N(u, l)| > |N(v, l)| 
                then remove v from C(u)

            Here L(N(u)) -> {L(u')| u' in N(u)} 
                 N(u,l) = {u' in N(u) | L(u') = l}
        """
        start_time = time.time()
        q_degree = q.degree()
        G_degree = G.degree()
        q_labels = nx.get_node_attributes(q, 'feat')
        G_labels = nx.get_node_attributes(G, 'feat')
        # generate L(N(u)), the whole is a list of sets
        labels_of_neighbor = []
        for u in q.nodes():
            neighbors = q.neighbors(u)
            s = set()
            for n in neighbors:
                s.add(q_labels[n])
            labels_of_neighbor.append([u, s])
        for u in q.nodes():
            u_neighbors = list(q[u]) # node indexes of all the neighbors 
            for v in G.nodes():
                v_neighbors = G[v] # node indexes of all the neighbors
                for l in labels_of_neighbor[u][1]:
                    # Compute N(u, l)
                    q_feats = [q.nodes[n]['feat'] for n in u_neighbors]
                    nul = q_feats.count(l)
                    # Compute N(v, l)
                    G_feats = [G.nodes[n]['feat'] for n in v_neighbors]
                    nvl = G_feats.count(l)
                    if nul > nvl:
                        candidates = [c for c in candidates if not (c[0] == u and c[1] == v)]
        print("--- %s seconds ---, NLF Done" % (time.time() - start_time))
        print(f"After the filtering, {len(candidates) / len(G.nodes())  * 100}% of the nodes left")

        return candidates

    # Ordering Parts
    def gen_ordering_order(self, q):
        return list(q.nodes())

    # Enumeration Methods
    def enumerate(self, q, G, C, A, order, i):
        start_time = time.time()
        if i == len(order) + 1:
            if  self.M != None:
                if len(self.M) == len(list(q.nodes())):
                    M_copy = copy.deepcopy(self.M)
                    self.MatchingList.append(M_copy)
            print("--- %s seconds ---, Find one match" % (time.time() - start_time))
            return self.M

        # v is a extenable vertex
        u = self.get_extenable_vertex(order, i)
        lc = self.computeLC(q, G, C, A, order, u, i)
        for c in lc:
            if c not in self.M:
                self.M[c[0]] = c[1]
                self.enumerate(q, G, C, A, order, i + 1)
                del self.M[c[0]]

    # ComputeLC of QuickSI and RI
    def computeLC(self, q, G, C, A, order, u, i):
        if i == 1: # do not care the edge
            return [c for c in C if c[0] == u]
        lc = []
        # examine the edge
        G_edges = list(self.G.edges())
        flag = False
        bn = self.backward_neighbors(u, order, q)
        for v in C:
            if v[0] == u:
                flag = True
                # for u_prime in self.backward_neighbors(u, order, q):
                for u_prime in bn:
                    edge = [v[1], self.M[u_prime]]
                    edge.sort()
                    if  tuple(edge) not in G_edges:
                        flag = False
                        break
                if flag == True: # might have a sequence error
                    lc.append(v)
        return lc
        # return [c for c in C if c[0] == u]

    def backward_neighbors(self, u, order, q):
        res = set()
        index = order.index(u)
        neighbors = list(q.neighbors(u))
        keys = [0,1,2]
        ns = [n for n in neighbors if n in list(self.M.keys())]
        res.update(ns)
        return list(res)

    def get_extenable_vertex(self, order, i):
        length = len(self.M)
        if length == 0:
            return order[0]
        else:
            return order[i - 1]
  
    def check_match_subgraph (self, q):
        # init the current matching first
        main_start_time = time.time()
        self.MatchingList = []
        self.M = {}
        try:
            assert (isinstance(q, nx.classes.graph.Graph) and nx.is_connected(q))
        except:
            print('Input query graph must be a single networkx instance.')
            sys.exit()

        C = self.NLF(q, self.G, self.LDF(q, self.G))
        A = None
        order = self.gen_ordering_order(q)
        self.enumerate(q, self.G, C, A, order, 1)
        print("--- %s seconds ---, Job done" % (time.time() - main_start_time))
        return self.MatchingList

    def draw_multi_results(self):
        for match in self.MatchingList:
            self.draw_check_result(match.values())
