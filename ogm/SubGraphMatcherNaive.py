import networkx as nx
from itertools import combinations
import matplotlib.pyplot as plt

class SubGraphMatcherNaive:
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
        self.check_result = None

    def generate_all_subgraphs(self, G_q):
        combs = list(combinations(self.G_t_nodes, len(list(G_q.nodes))))
        res = []
        for i in range(len(combs)):
            graph = self.G_t.subgraph(list(combs[i]))
            if nx.is_connected(graph): # Only generate connected candidates
                res.append([combs[i], graph])
        return res

    def check_match_subgraph(self, G_q):
        # Type Check, the input G_q must be a networkx instance and connected
        try:
            assert (isinstance(G_q, nx.classes.graph.Graph) and nx.is_connected(G_q))
        except:
            print('Input query graph must be a single networkx instance.')
            exit()

        candidates = self.generate_all_subgraphs(G_q)
        for candidate in candidates:
            if nx.is_isomorphic(candidate[1], G_q):
                self.check_result = candidate[0]
                self.draw_check_result()
                print('Matched!', candidate[0])
                return True
        return False

    def draw_check_result(self):
        if self.check_result != None:
            labels = nx.get_node_attributes(self.G_t, 'feat')
            pos = nx.spring_layout(self.G_t)
            options = {
                        # 'node_color': 'yellow',
                        'node_size': 400,
                        # 'width': 3,
                        # 'labels': labels,
                        # 'with_labels': True
                        }
            subgraph = self.G_t.subgraph(list(self.check_result))
            nx.draw_networkx_nodes(
                    self.G_t, 
                    pos, 
                    nodelist=list(self.G_t.nodes()), 
                    node_color='yellow', 
                    **options)
            # Draw the subgraph nodes
            nx.draw_networkx_nodes(self.G_t, 
                    pos, 
                    nodelist=list(subgraph.nodes()), 
                    node_color='red', 
                    **options)

            # Draw all the edges
            nx.draw_networkx_edges(
                    self.G_t, 
                    pos, 
                    edgelist=list(self.G_t.edges()), 
                    width=3, 
                    edge_color='black')
            # Draw the subgraph edges
            nx.draw_networkx_edges(
                    self.G_t, 
                    pos, 
                    edgelist=list(subgraph.edges()), 
                    width=3, 
                    edge_color='red')
            labels = nx.get_node_attributes(self.G_t, 'feat') 
            nx.draw_networkx_labels(self.G_t, pos, labels, font_size=16)
            plt.show()

    # 如何复用计算方式
    def check_match_from_subgraphs(self, G_q_list):
        try:
            assert (isinstance(G_q_list, list))
        except:
            print('Input queries must be a list')
            exit()
        pass

     
        


