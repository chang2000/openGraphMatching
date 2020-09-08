import networkx as nx
import matplotlib.pyplot as plt
from SubGraphMatcher import SubGraphMatcher

def draw_graph(G):
    options = {
        'node_color': 'yellow',
        'node_size': 300,
        'width': 3,
        'with_labels': True
    }
    nx.draw(G, **options)
    plt.show()

# G_t = nx.path_graph(4000)
# G_t = nx.complete_graph(10)
G_t = nx.path_graph(10)
G_q = nx.path_graph(5)

# draw_graph(G_q)
# draw_graph(G_t)

SGM = SubGraphMatcher(G_q, G_t)
print(SGM.is_subgraph_match())

# G_q.add_node(3)
# SGM = SubGraphMatcher(G_q, G_t)
# print(SGM.is_subgraph_match())

