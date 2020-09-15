import networkx as nx
from itertools import combinations

class SubGraphMatcher:
    def __init__(self, G_t):
        """
        G_q: the query graph
        G_t: the target graph

        Examples:
        -------
        >>> import SubGraphMatcher
        >>> G_t = nx.path_graph(4)
        >>> G_q = nx.path_graph(2)
        >>> SGM = SubGraphMatcher(G_t)
        >>> SGM.is_subgraph_match(G_q)
            True
        """
        try:
            assert (nx.is_connected(G_t))
        except:
            print('Input graphs should be connected')
            exit()
        self.G_t = G_t
        self.G_t_nodes = list(G_t.nodes())

    def generate_all_subgraphs(self, G_q):
        combs = list(combinations(self.G_t_nodes, len(list(G_q.nodes))))
        # print(combs)
        res = []
        for i in range(len(combs)):
            graph = self.G_t.subgraph(list(combs[i]))
            if nx.is_connected(graph): # Only generate connected candidates
                res.append(graph)
        return res

    def check_match_subgraph(self, G_q):
        # Type Check, the input G_q must be a networkx instance and connected
        try:
            assert (isinstance(G_q, nx.classes.graph.Graph) and nx.is_connected(G_q))
        except:
            print('Input query graph must be a single networkx instance.')
            exit()

        candidates = self.generate_all_subgraphs(G_q)
        for graph in candidates:
            if nx.is_isomorphic(graph, G_q):
                return True
        return False

    # 如何复用计算方式
    def check_match_from_subgraphs(self, G_q_list):
        try:
            assert (isinstance(G_q_list, list))
        except:
            print('Input queries must be a list')
            exit()
        pass

        
        


