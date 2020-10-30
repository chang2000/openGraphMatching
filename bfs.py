from matplotlib.pyplot import draw
import networkx as nx
import matplotlib.pyplot as plt
from SubGraphMatcher import SubGraphMatcher

def draw_graph(G):
    labels = nx.get_node_attributes(G, 'feat') 
    for l in labels:
        labels[l] = str(l) + ":" + labels[l]
    options = {
        'node_color': 'yellow',
        'node_size': 400,
        'width': 3,
        'labels': labels,
        'with_labels': True
    }
    nx.draw(G, **options)
    plt.show()

G1 = nx.Graph() 
G1.add_nodes_from([ (0, {'feat': 'A'}),
    (1, {'feat': 'B'}),
    (2, {'feat': 'C'}),
    (3, {'feat': 'D'}),
])
G1.add_edges_from([
    (0, 1),
    (0, 2),
    (1, 2),
    (1, 3),
    (2, 3)])

G2 = nx.Graph()
G2.add_nodes_from([
    (0, {'feat': 'A'}),
    (1, {'feat': 'C'}),
    (2, {'feat': 'B'}),
    (3, {'feat': 'C'}),
    (4, {'feat': 'B'}),
    (5, {'feat': 'C'}),
    (6, {'feat': 'B'}),
    (7, {'feat': 'C'}),
    (8, {'feat': 'D'}),
    (9, {'feat': 'D'}),
    (10, {'feat': 'D'}),
    (11, {'feat': 'D'}),
    (12, {'feat': 'D'}),
    (13, {'feat': 'C'}),
    (14, {'feat': 'D'}),
])
G2.add_edges_from([
    (0, 1),
    (0, 2),
    (0, 3),
    (0, 4),
    (0, 5),
    (0, 6),
    (0, 7),
    (1, 2),
    (1, 8),
    (2, 9),
    (2, 10),
    (3, 4),
    (3, 10),
    (4, 5),
    (4, 10),
    (4, 11),
    (4, 12),
    (5, 12),
    (6, 12),
    (6, 13),
    (7, 14),
    (9, 10),
])
draw_graph(G1)
# draw_graph(G2)
bfs_res = nx.bfs_tree(G1, source=0)
print(bfs_res)
print(type(bfs_res))
print(bfs_res.nodes())
print(bfs_res.edges())
draw_graph(bfs_res)