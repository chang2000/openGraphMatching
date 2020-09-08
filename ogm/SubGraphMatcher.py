import networkx as nx
from itertools import combinations

class SubGraphMatcher:
    def __init__(self, G_q, G_t):
        """
        G_q: the query graph
        G_t: the target graph

        Examples:
        -------
        >>> import SubGraphMatcher
        >>> G_t = nx.path_graph(4)
        >>> G_q = nx.path_graph(2)
        >>> SGM = SubGraphMatcher(G_q, G_t)
        """
        try:
            assert (nx.is_connected(G_q) and nx.is_connected(G_t))
        except:
            print('Input graphs should be connected')
            exit()
        self.G_q = G_q
        self.G_t = G_t
        self.G_q_nodes = list(G_q.nodes())
        self.G_t_nodes = list(G_t.nodes())


    def generate_all_subgraphs(self):
        combs = list(combinations(self.G_t_nodes, len(self.G_q_nodes)))
        print(combs)
        res = []
        for i in range(len(combs)):
            graph = self.G_t.subgraph(list(combs[i]))
            if nx.is_connected(graph): # Only generate connected candidates
                res.append(graph)
        return res

    def is_subgraph_match(self):
        candidates = self.generate_all_subgraphs()
        for graph in candidates:
            if nx.is_isomorphic(graph, self.G_q):
                return True
        return False

