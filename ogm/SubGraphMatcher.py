import abc
from abc import abstractmethod
import sys
import time
import copy
import networkx as nx

class SubGraphMatcher(abc.ABC):
    def __init__(self, G):
        self.G = G
        self.G_nodes = list(G.nodes())
        self.G_edges = list(G.edges())
        # self.G_labels = nx.get_edge_attributes(G, 'feat')
        self.G_degree = G.degree()
        self.MatchingList = []

    def filtering(self, q):
        ''' Filter candidate vertices in the target graph
        '''
        res = []
        for u in q.nodes():
            for v in self.G_nodes:
                res.append((u, v))
        return res

    def ordering(self, q, order):
        return order
    
    # @abc.abstractclassmethod
    def find_subgraph_match(self, q, imd, order):
        ''' Enumerate partial results
        '''
        pass
    
    def is_subgraph_match(self, q):
        try:
            assert (isinstance(q, nx.classes.graph.Graph) and nx.is_connected(q))
        except:
            print('Input query graph must be a single connected networkx instance.')
            sys.exit()
        main_start_time = time.time()
        imd = self.filtering(q)
        order = self.ordering(q, imd)
        data = self.find_subgraph_match(q, imd, order)
        print("--- %s seconds ---, Job done" % (time.time() - main_start_time)) 
        print()
        return data

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
        G_labels = nx.get_node_attributes(self.G, 'feat')
        v_set = set()
        for u in q.nodes():
            for v in self.G_nodes:
                if self.G_degree[v] >= q_degree[u]:
                    if G_labels[v] == q_labels[u]:
                        res.append((u, v))
        for c in res:
            v_set.add(c[1]) 
        self.filter_rate = len(v_set) / len(self.G_nodes)
        print("--- %s seconds ---, LDF Done" % (time.time() - start_time))
        print(f"After the filtering, { self.filter_rate  * 100}% of the nodes left")
        return res

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
                # TODO rethink how to handle this part
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



