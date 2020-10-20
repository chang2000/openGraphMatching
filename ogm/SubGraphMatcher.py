from copy import deepcopy
import networkx as nx
from itertools import combinations
import matplotlib.pyplot as plt
import sys
import copy
import time

from networkx.algorithms.assortativity.pairs import node_attribute_xy
from networkx.algorithms.dag import transitive_closure_dag
from networkx.algorithms.link_prediction import adamic_adar_index
from networkx.algorithms.operators.unary import reverse
from networkx.generators.intersection import general_random_intersection_graph
from networkx.generators.joint_degree_seq import _neighbor_switch
from numpy.core.einsumfunc import _can_dot

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

    # TODO Consider review NLF to avoid potential slowless
    def NLF(self, q, candidates):
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
        for c in can_copy: 
            u, v = c[0], c[1]
            u_neighbors = list(q[u]) # the nodes' index of u's neighbor
            v_neighbors = list(self.G[v]) # the nodes' index of v's neighbor
            for l in labels_of_neighbor[u][1]:
                # Compute N(u, l)
                q_feats = [q.nodes[n]['feat'] for n in u_neighbors]
                nul = q_feats.count(l)
                # Compute N(v, l)
                G_feats = [self.G.nodes[n]['feat'] for n in v_neighbors]
                nvl = G_feats.count(l)
                if nul > nvl:
                    candidates = [c for c in candidates if not (c[1] == v and c[0] == u)]

        for c in candidates:
            v_set.add(c[1])
        print("--- %s seconds ---, NLF Done" % (time.time() - start_time))
        print(f"After the filtering, {len(v_set) / len(self.G_nodes)  * 100}% of the nodes left")
        self.filter_rate = len(v_set) / len(self.G_nodes)
        return candidates

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
        print(f"After the filtering, { self.filter_rate  * 100}% of the nodes left")
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
        print(f"After the filtering, { self.filter_rate  * 100}% of the nodes left")
                    
        return candidates

    # Filtering in CECI
    """
    Generate the BFS Tree First
    The source point: TODO
    Already DONE: Find a dfs tree in the networkx 

    Survey here: what method is used in networkx to find the BFS tree of a graph? 
    It's written in PURE python code
    """

    # filtering method based on the observation 3.1
    # TODO Which one is faster? List or dict, if dict works well, consider rewrite it into list

    def generate_bfs_tree(self, q, source):
        tree = nx.bfs_tree(q, source=source)
        return tree

    def generate_bfs_source(self, q, candidates):
        can_dict = self.can_to_dict(candidates)
        nodes = list(q.nodes())
        minimum = float('inf')
        minimun_node = None
        for n in nodes:
            # print(len(can_dict[n]) / q.degree[n])
            value = len(can_dict[n]) / q.degree[n]
            if value < minimum:
                minimum = value
                minimum_node = n
        return  minimum_node

    def ceci_filtering(self, q, candidates):
        source = self.generate_bfs_source(q, candidates)
        bfs_tree = self.generate_bfs_tree(q, source)
        can_dict = self.can_to_dict(candidates) 
        traversal_order = self.ceci_ordering(q, candidates)
        """
        Build the auxiliary data structure
        """
        A = dict()
        for u in traversal_order:
            tmp = []
            tmp.append(u)
            A[u] = list()
            A[u].append(can_dict[u])
            edges = set()
            successors = list(bfs_tree.successors(u))
            predecessors = list(bfs_tree.predecessors(u))
            for up in successors:
                for v in can_dict[u]:                       
                    for vp in can_dict[up]:
                        # print(sorted((v,vp)))
                        tup = tuple(sorted((v, vp)))
                        if tup in self.G_edges:
                            # print(f'Caught! Add {(v, vp)} to edges')
                            edges.add((v, vp))                        
            A[u].append(edges)
            # Also need to find the node u's tree parent
            A[u].append(predecessors)
            

        # monitor the A
        # for a in A.keys():
        #     print(a, A[a])

        # Do the filtering
        # reverse_traversal_order = traversal_order.reverse()
        reverse_traversal_order = traversal_order
        for u in reverse_traversal_order: 
            # print('checking', u)
            # print('-----------')
            # Get N(u)
            neigh_of_u = list(q.neighbors(u))
            # iterate v, the data node
            can_of_u = copy.deepcopy(can_dict[u])
            for v in can_dict[u]:
                # get v's neighbors
                neigh_of_v = set(self.G.neighbors(v))
                # print(f'the neighbor of {v} is {neigh_of_v}')
                # Check weather N(v) \intersect C(u') is empty
                flag = True
                for u_prime in neigh_of_u:
                    can_u_prime = set(can_dict[u_prime])
                    # set operation
                    if can_u_prime & neigh_of_v:
                        inct = can_u_prime & neigh_of_v
                        # print('inct is', inct)
                        for vp in inct:
                            edge = [v, vp]
                            edge.sort()
                            edge = tuple(edge)
                            if edge in self.G_edges and reverse_traversal_order.index(u_prime) > traversal_order.index(u):
                                A[u][1].add((v, vp))
                    else:
                        flag = False
                        break

                if flag == False:
                    # remove v from u's candidates
                    # print(f'going to remove v{v}')
                    can_of_u.remove(v)
                    A[u][0] = can_of_u
                    # remove all the edges related to v
                    for a in A.keys():
                        A[a][1] = list(A[a][1])
                        for e in A[a][1]:
                            if v in e:
                                # print(f'remove {e} from {a} de edges')
                                A[a][1].remove(e)
                        A[a][1] = set(A[a][1])
            can_dict[u] = can_of_u   

        res = self.dict_to_can(can_dict)
        v_set = set()
        for c in res:
            v_set.add(c[1]) 
        self.filter_rate = len(v_set) / len(self.G_nodes)
        print(f"After ceci filtering, { self.filter_rate  * 100}% of the nodes left")
        return [res, A]

    def can_to_dict(self, candidates):
        res = dict({})
        last_node = None
        tmp_list = []
        for c in candidates:
            if c[0] == last_node:
                tmp_list.append(c[1])
            else:
                if last_node != None:
                    res[last_node] = tmp_list
                tmp_list = []
                last_node = c[0]
                tmp_list.append(c[1])
        res[last_node] = tmp_list
        return res

    def dict_to_can(self, dic):
        res = [] 
        for k in dic.keys():
            for v in dic[k]:
                res.append((k, v))
        return res  
    # generate the data structure

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
        res = [i[0] for i in res]
        return res

    def ceci_ordering(self, q, candidates):
        # The candidates is NLF candidates
        # Find the sourc for the bfs
        source = self.generate_bfs_source(q, candidates)
        tree = self.generate_bfs_tree(q, source)
        return list(tree.nodes())

    # Enumeration
    # > Enumeration for Plain Method and GQL
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
        # print(f'the local candidates for {u} is {lc}')
        for c in lc:
            if c not in self.M:
                self.M[c[0]] = c[1]
                self.enumerate(q, C, A, order, i + 1)
                del self.M[c[0]]

    # > Enumeration for CECI 
    def ceci_enumerate(self, q, C, A, order, i):
        self.en_counter += 1
        if i == len(order) + 1:
            if  self.M != None:
                if len(self.M) == len(list(q.nodes())):
                    M_copy = copy.deepcopy(self.M)
                    self.MatchingList.append(M_copy)
            return self.M
        # v is a extenable vertex
        u = self.get_extenable_vertex(order, i)
        lc = self.ceci_compute_LC(q, C, A, order, u, i)
        for c in lc:
            if c not in self.M:
                self.M[c[0]] = c[1]
                self.ceci_enumerate(q, C, A, order, i + 1)
                del self.M[c[0]]


    # ComputeLC of GraphQL
    def computeLC(self, q, C, A, order, u, i):
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

    def ceci_compute_LC(self, q, C, A, order, u, i):
        if i == 1: # do not care the edge
            res = []
            for c in A[u][0]:
                res.append((u, c))
            return res

        bn = self.backward_neighbors(u, order, q)
        lc = []
        if len(bn) == 1:
            up = A[u][2][0]
            # find all edges, and all point out from up
            up_edges = A[up][1]
            M_u_p = self.M[up]
            for e in up_edges:
                if e[0] == M_u_p and e[1] in A[u][0]:
                    lc.append((u, e[1]))
            return lc 
        else: 
            set_list = []
            for u_prime in bn:
                M_u_prime = self.M[u_prime]
                u_prime_edges = A[u_prime][1]
                tmp_lc = set()
                for e in u_prime_edges:
                    if e[0] == M_u_prime and e[1] in A[u][0]:
                        tmp_lc.add((u, e[1]))
                set_list.append(tmp_lc)
            inct = set.intersection(*set_list)
            lc = list(inct)
        return lc
        

    def backward_neighbors(self, u, order, q):
        res = set()
        index = order.index(u)
        neighbors = list(q.neighbors(u))
        keys = [0,1,2]
        ns = [n for n in neighbors if n in list(self.M.keys())]
        res.update(ns)
        return list(res)

    def get_extenable_vertex(self, order, i):
        return order[i - 1]

    # How to design for the different ALGOS?
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
        
        C = self.NLF(q, self.LDF(q))
        print(C)
        A = None
        order = self.plain_ordering(q)
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
        
        imd = self.LDF(q)
        time_2 = time.time()
        print('Running GQL local pruning...')
        imd =  self.GQL_local_pruning(q, imd)
        time_3 = time.time()
        print(f'--- {time_3 - time_2} seconds ---, local pruning done')
        print('Running Global Refinement...')
        imd = self.GQL_global_refinement(q, imd)
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

    def ceci_check_match_subgraph(self, q):
        print("CECI is used...")
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
        imd = self.LDF(q)
        imd = self.NLF(q, imd)
        NLF_candidates = copy.deepcopy(imd)
        time1 = time.time()
        print('ceci filtering is running...')
        imd = self.ceci_filtering(q, imd)
        print(f'--- {time.time() - time1} seconds ---, ceci ordering done')
        print()
        C = imd[0]
        A = imd[1]
        order = self.ceci_ordering(q, NLF_candidates)

        print('enumerating...')
        en_time = time.time()

        self.ceci_enumerate(q, C, A, order, 1)

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
        
     
