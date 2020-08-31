import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()
G.add_nodes_from([1, 2, 3, 4, 5, 6])
G.add_edges_from([(1, 2), (3, 4), (1, 3), (3, 5), (5, 6)])
print(G.nodes)
print(G.edges)

nx.draw(G, with_labels=True)
plt.show()
