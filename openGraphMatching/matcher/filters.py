import sys
import time
import copy
import networkx as nx

class Filter():
    def __init__(self, G):
        self.G = G
        self.G_nodes = list(G.nodes())
        self.G_edges = list(G.edges())
        self.G_labels = nx.get_node_attributes(G, 'feat')
        self.G_degree = G.degree()

    def naive_filter(self, q):
        res = []
        for u in q.nodes():
            for v in self.G_nodes:
                res.append((u, v))
        return res

    def ldf(self, q):
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
        # Filter rate usage
        for c in res:
            v_set.add(c[1]) 
        # self.filter_rate = len(v_set) / len(self.G_nodes)
        # print("--- %s seconds ---, LDF Done" % (time.time() - start_time))
        # print(f"LDF, { self.filter_rate  * 100}% of the nodes left")
        return res

    def nlf(self, q, candidates):
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
        labels_of_neighbor = {}
        for u in q.nodes():
            neighbors = q.neighbors(u)
            s = set()
            for n in neighbors:
                s.add(q_labels[n])
            labels_of_neighbor[u] =  s
        v_set = set()
        can_copy = copy.deepcopy(candidates)
        # How about generate them before
        # ALERT! SLOWNESS comes from here
        u_neighbors_dic = {}
        v_neighbors_dic = {}
        for u in q.nodes():
            u_neighbors_dic[u] = list(q.neighbors(u))
        for v in self.G_nodes:
            v_neighbors_dic[v] = list(self.G.neighbors(v))
        for u, v in can_copy: 
            q_feats = [q_labels[n] for n in u_neighbors_dic[u]]
            G_feats = [self.G_labels[n] for n in v_neighbors_dic[v]]
            for l in labels_of_neighbor[u]:
                # Compute N(u, l)
                nul = q_feats.count(l)
                # Compute N(v, l)
                nvl = G_feats.count(l)
                if nul > nvl:
                    candidates = [c for c in candidates if not (c[0] == u and c[1] == v)]

        for u, v in candidates:
            v_set.add(v)
        print("--- %s seconds ---, NLF Done" % (time.time() - start_time))
        print(f"NLF, {len(v_set) / len(self.G_nodes)  * 100}% of the nodes left")
        self.filter_rate = len(v_set) / len(self.G_nodes)
        return candidates

    def gql_local_pruning(self, q, candidates):
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
        # self.filter_rate = len(vset) / len(self.G_nodes)
        # print(f"After the GQL local pruning,  { self.filter_rate  * 100}% of the nodes left")
        return res 

    def gql_global_refinement(self, q, candidates):
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
        # print(f"After GQL global refinement, { self.filter_rate  * 100}% of the nodes left")
        return candidates

    def gql_filtering(self, q):
        imd = self.ldf(q)
        imd = self.nlf(q, imd)
        imd = self.gql_local_pruning(q, imd)
        imd = self.gql_global_refinement(q, imd)
        return imd

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