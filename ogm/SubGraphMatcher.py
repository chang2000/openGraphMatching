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
        self.G_edges = list(G.edges())
        self.M = {} # M is a dict
        self.MatchingList = []
        self.filter_rate = 1
        self.en_counter = 0 
        self.G_labels = nx.get_node_attributes(G, 'feat')
        self.G_degree = G.degree()

    # Filtering
    def LDF(self, q, G):
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
        v_set = set()
        for u in q.nodes():
            for v in self.G_nodes:
                if self.G_degree[v] >= q_degree[u]:
                    if self.G_labels[v] == q_labels[u]:
                        res.append((u, v))
        for c in res:
            v_set.add(c[1]) 
        self.filter_rate = len(v_set) / len(self.G_nodes)
        print("--- %s seconds ---, LDF Done" % (time.time() - start_time))
        print(f"After the filtering, { self.filter_rate  * 100}% of the nodes left")
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
        print('running NLF...')
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
        v_set = set()
        can_copy = copy.deepcopy(candidates)
        for c in can_copy: 
            u, v = c[0], c[1]
            u_neighbors = list(q[u]) # the nodes' index of u's neighbor
            v_neighbors = list(G[v]) # the nodes' index of v's neighbor
            for l in labels_of_neighbor[u][1]:
                # Compute N(u, l)
                q_feats = [q.nodes[n]['feat'] for n in u_neighbors]
                nul = q_feats.count(l)
                # Compute N(v, l)
                G_feats = [G.nodes[n]['feat'] for n in v_neighbors]
                nvl = G_feats.count(l)
                if nul > nvl:
                    # candidates = [c for c in candidates if  (c[1] != v or c[0] != u)]
                    candidates = [c for c in candidates if not (c[1] == v and c[0] == u)]

        for c in candidates:
            v_set.add(c[1])
        # print("NLF output", candidates[0], len(candidates))
        print("--- %s seconds ---, NLF Done" % (time.time() - start_time))
        print(f"After the filtering, {len(v_set) / len(G.nodes())  * 100}% of the nodes left")
        self.filter_rate = len(v_set) / len(G.nodes())
        return candidates

    def GQL_local_pruning(self, q, G, candidates):
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
        print(f"After the filtering, { self.filter_rate  * 100}% of the nodes left")
        return res

    def GQL_global_refinement(self, q, G, candidates):
        for c in candidates:
            u, v = c[0], c[1]
            n_u = list(q.neighbors(u))
            v_u = list(G.neighbors(v))
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
        print(f"After the filtering, { self.filter_rate  * 100}% of the nodes left")
                    
        return candidates

    # Ordering
    def plain_ordering(self, q):
        print('Using plain ordering...')
        return list(q.nodes())

    def GQL_ordering(self, q, candidates):
        print('Using GQL ordering...')
        q_nodes = list(q.nodes())
        res = [[i, 0] for i in q_nodes]
        # Count C(u)
        for c in candidates:
            res[c[0]][1] += 1
        res.sort(key = lambda x: x[1])
        res.reverse()
        # print(res)
        res = [i[0] for i in res]
        # print(res)
        return res
        
    # Enumeration
    def enumerate(self, q, C, A, order, i):
        self.en_counter += 1
        if i == len(order) + 1:
            if  self.M != None:
                if len(self.M) == len(list(q.nodes())):
                    M_copy = copy.deepcopy(self.M)
                    self.MatchingList.append(M_copy)
            return self.M

        # v is a extenable vertex
        u = self.get_extenable_vertex(order, i)
        lc = self.computeLC(q, C, A, order, u, i)
        for c in lc:
            if c not in self.M:
                self.M[c[0]] = c[1]
                self.enumerate(q, C, A, order, i + 1)
                del self.M[c[0]]

    # ComputeLC of GraphQL
    def computeLC(self, q, C, A, order, u, i):
        if i == 1: # do not care the edge
            return [c for c in C if c[0] == u]
        lc = []
        # examine the edge
        flag = False
        bn = self.backward_neighbors(u, order, q)
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
        main_start_time = time.time()
        # init the current matching first
        self.filter_rate = 1
        self.MatchingList = []
        self.M = {}
        try:
            assert (isinstance(q, nx.classes.graph.Graph) and nx.is_connected(q))
        except:
            print('Input query graph must be a single networkx instance.')
            sys.exit()
        
        C = self.NLF(q, self.G, self.LDF(q, self.G))
        A = None
        order = self.plain_ordering(q)
        # order = self.GQL_ordering(q, C)
        print('enumerating...')
        en_time = time.time()

        self.enumerate(q, self.G, C, A, order, 1)

        print(f'enumeration done, takes {time.time() - en_time}s')
        print(f'enumeration runs {self.en_counter} times')
        print("--- %s seconds ---, Job done" % (time.time() - main_start_time))
        print(f"Totally find {len(self.MatchingList)} matches.")
        print(' ')
        print(' ')
        output_data = [self.filter_rate, self.MatchingList]
        return output_data

    def gql_check_match_subgraph (self, q):
        main_start_time = time.time()
        # init the current matching first
        self.filter_rate = 1
        self.MatchingList = []
        self.M = {}
        try:
            assert (isinstance(q, nx.classes.graph.Graph) and nx.is_connected(q))
        except:
            print('Input query graph must be a single networkx instance.')
            sys.exit()
        
        imd = self.LDF(q, self.G)
        time_2 = time.time()
        print('Running GQL local pruning...')
        imd =  self.GQL_local_pruning(q, self.G, imd)
        time_3 = time.time()
        print(f'--- {time_3 - time_2} seconds ---, local pruning done')
        imd = self.GQL_global_refinement(q, self.G, imd)
        time_4 = time.time()
        print(f'--- {time_4 - time_3} seconds ---, global refinement done')
        C = imd
        A = None
        order = self.GQL_ordering(q, C)
        print('enumerating...')
        en_time = time.time()

        self.enumerate(q, C, A, order, 1)


        print(f'enumeration done, takes {time.time() - en_time}s')
        print(f'enumeration runs {self.en_counter} times')
        print("--- %s seconds ---, Job done" % (time.time() - main_start_time))
        print(f"Totally find {len(self.MatchingList)} matches.")
        print(' ')
        print(' ')
        output_data = [self.filter_rate, self.MatchingList]
        return output_data


    # Utility functions
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

    #  Visualize related
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
                    edgelist=self.G_edges, 
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
    def draw_multi_results(self):
        for match in self.MatchingList:
            self.draw_check_result(match.values())
        
     