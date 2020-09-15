import networkx as nx
from itertools import combinations
import matplotlib.pyplot as plt
import sys

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
            True
        """
        try:
            assert (nx.is_connected(G))
        except:
            print('Input graphs should be connected')
            exit()
        self.G = G
        self.G_nodes = list(G.nodes())
        self.check_result = None
        self.M = {} # M is a dict

    def generate_all_subgraphs(self, G_q):
        combs = list(combinations(self.G_nodes, len(list(G_q.nodes))))
        res = []
        for i in range(len(combs)):
            graph = self.G.subgraph(list(combs[i]))
            if nx.is_connected(graph): # Only generate connected candidates
                res.append([combs[i], graph])
        return res


    def draw_check_result(self):
        if self.check_result != None:
            labels = nx.get_node_attributes(self.G, 'feat')
            pos = nx.spring_layout(self.G)
            options = { 'node_size': 400 }
            subgraph = self.G.subgraph(list(self.check_result))
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
            nx.draw_networkx_labels(self.G, pos, labels, font_size=16)
            plt.show()

    # 如何复用计算方式
    def check_match_from_subgraphs(self, G_q_list):
        try:
            assert (isinstance(G_q_list, list))
        except:
            print('Input queries must be a list')
            exit()
        pass
    
    # The Enhanced version

    # Basic Methods on filtering
    def LDF(self, q, G):
        """
        This function takes in a query graph and a target graph
        Returns a list of all the candidate vertex for each node in q filtered by LDF

        LDF: L(v) = L(u) and d(v) > d(u), as v in the candidate vertex
        """
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
        # print(labels_of_neighbor)
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
                        # remove v from candidate
                        # print(v)
                        # print('candidate is', candidates)
                        candidates = [c for c in candidates if not (c[0] == u and c[1] == v)]
                        # print('candidates after filtering', candidates)
        # print(candidates)
        return candidates

    # Ordering Parts
    def gen_ordering_order(self, q):
        return list(q.nodes())

    # Enumeration Methods
    def enumerate(self, q, G, C, A, order, i):
        if i == len(order) + 1:
            print('matching output:', self.M)
            return self.M

        # v is a extenable vertex
        u = self.get_extenable_vertex(order, i)
        lc = self.computeLC(q, G, C, A, order, u, i)
        print('lc is', lc)
        for c in lc:
            print(c)
            if c not in self.M:
                self.M[c[0]] = c[1]
                self.enumerate(q, G, C, A, order, i + 1)
                del self.M[c[0]]

    # ComputeLC of QuickSI and RI
    def computeLC(self, q, G, C, A, order, u, i):
        # print(C)
        # print(u)
        if i == 1: # do not care the edge
            return [c for c in C if c[0] == u]

        lc = []
        # examine the edge
        # get the parent of current match
        length = len(self.M)
        parent_of_u = order[i - 2]
        M_u_p = self.M[parent_of_u]
        print(M_u_p)
        print('Mup neghs:', list(G[M_u_p]))
        G_edges = list(self.G.edges())
        print(G_edges)
        for v in list(G.neighbors(M_u_p)):
            flag = True
            for u_prime in self.backward_neighbors(u, order, q):
                if u_prime != parent_of_u: 
                    # if (v, self.M[u_prime]) not in G_edges:
                        # flag = False
                        # break
                    pass
            if flag == True:
                # 可能会顺序出错
                lc.append((u, v))

        # return lc
        # Default
        return [c for c in C if c[0] == u]

    def backward_neighbors(self, u, order, q):
        return order

    def get_extenable_vertex(self, order, i):
        # order is just list on index here
        # I want to know what's the matching going on
        # find the latest match (right or wrong)
        length = len(self.M)
        print(self.M)
        if length == 0:
            return order[0]
        else:
            # latest_node = self.M[length - 1] 
            # print(latest_node)
            # index = order.index(latest_node[0])
            # print('return order is', index + 1 )
            return order[i - 1]
  
    """
    Rethink: 
    1. M should be a dict to make it easy to operate


    """
    def check_match_subgraph (self, q):
        try:
            assert (isinstance(q, nx.classes.graph.Graph) and nx.is_connected(q))
        except:
            print('Input query graph must be a single networkx instance.')
            sys.exit()

        C = self.NLF(q, self.G, self.LDF(q, self.G))
        A = None
        order = self.gen_ordering_order(q)
        res = self.enumerate(q, self.G, C, A, order, 1)
        print(res)
        return res
        

    # The naive way
    # def check_match_subgraph(self, G_q):
        # try:
            # assert (isinstance(G_q, nx.classes.graph.Graph) and nx.is_connected(G_q))
        # except:
            # print('Input query graph must be a single networkx instance.')
            # exit()

        # candidates = self.generate_all_subgraphs(G_q)
        # for candidate in candidates:
            # if nx.is_isomorphic(candidate[1], G_q):
                # self.check_result = candidate[0]
                # self.draw_check_result()
                # print('Matched!', candidate[0])
                # return True
        # return False
