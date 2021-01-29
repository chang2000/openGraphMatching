import sys
import time
import copy
import networkx as nx
# from . import BaseMatcher

class Filter():
    def __init__(self, G):
        self.G = G
        self.G_nodes = list(G.nodes())
        self.G_edges = list(G.edges())
        self.G_labels = nx.get_node_attributes(G, 'feat')
        self.G_degree = G.degree()

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
        # Filter rate usage
        for c in res:
            v_set.add(c[1]) 
        # self.filter_rate = len(v_set) / len(self.G_nodes)
        # print("--- %s seconds ---, LDF Done" % (time.time() - start_time))
        # print(f"LDF, { self.filter_rate  * 100}% of the nodes left")
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
        # ALERT! SLOWNESS comes from here
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
        print(f"NLF, {len(v_set) / len(self.G_nodes)  * 100}% of the nodes left")
        self.filter_rate = len(v_set) / len(self.G_nodes)
        return candidates

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
        print(f"NLF, {len(v_set) / len(self.G_nodes)  * 100}% of the nodes left")
        self.filter_rate = len(v_set) / len(self.G_nodes)
        return candidates