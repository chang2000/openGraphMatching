import networkx as nx
from itertools import combinations
import matplotlib.pyplot as plt

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
    # def NLF(self, q, G):
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
                    print('nul', nul)
                    # compute N(v, l)
                    G_feats = [G.nodes[n]['feat'] for n in v_neighbors]
                    nvl = G_feats.count(l)
                    print('nvl', nvl)
                    if nul > nvl:
                        # remove v from candidate
                        # print(v)
                        # print('candidate is', candidates)
                        candidates = [c for c in candidates if c[1] != v]
                        # print('candidates after filtering', candidates)
        return candidates

        
     
        


