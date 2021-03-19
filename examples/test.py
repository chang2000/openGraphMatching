import networkx as nx
import openGraphMatching.matcher as matcher
from openGraphMatching.utils import convert_graph, check_match_correctness

# The classic example
# Construct the query graph
q = nx.Graph()
q.add_nodes_from([
    (0, {'feat': 'A'}),
    (1, {'feat': 'B'}),
    (2, {'feat': 'C'}),
    (3, {'feat': 'D'}),
])
q.add_edges_from([
    (0, 1),
    (0, 2),
    (1, 2),
    (1, 3),
    (2, 3)])

# Construct the target graph
G = nx.Graph()
G.add_nodes_from([
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
G.add_edges_from([
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

# q = nx.Graph()
# q.add_nodes_from([
    # (0, {'feat': 'A'}),
    # (1, {'feat': 'A'}),
    # (2, {'feat': 'A'}),
    # (3, {'feat': 'A'}),
    # (4, {'feat': 'A'}),
    # (5, {'feat': 'A'}),
    # ])
# q.add_edges_from([
    # (0, 1),
    # (1, 2),
    # (2, 3),
    # (3, 4),
    # (4, 5),
    # (5, 0),
# ])

# The circle example
"""
q = nx.Graph()
q.add_nodes_from([
    (0, {'feat': 'A'}),
    (1, {'feat': 'A'}),
    (2, {'feat': 'A'}),
    (3, {'feat': 'A'}),
    (4, {'feat': 'A'}),
    (5, {'feat': 'A'}),
    ])
q.add_edges_from([
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (4, 5),
    (5, 0),
])

G = nx.Graph()
G.add_nodes_from([
    (0, {'feat': 'A'}),
    (1, {'feat': 'A'}),
    (2, {'feat': 'A'}),
    (3, {'feat': 'A'}),
    (4, {'feat': 'A'}),
    (5, {'feat': 'A'}),
    (6, {'feat': 'A'}),
    ])
G.add_edges_from([
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (4, 5),
    (5, 0),
    (1, 6),
    (4, 6),
    ])
"""

# The testing example
# target_graph_path = './dataset/hprd/data_graph/hprd.graph'
# query_folder_path = './dataset/hprd/query_graph/'
# query_file_name = 'query_dense_16_1.graph'
# G = convert_graph(target_graph_path)
# q = convert_graph(query_folder_path + query_file_name)

"""
G = nx.Graph()
q = nx.Graph()
q.add_nodes_from([
    (0, {'feat': 'A'}),
    (1, {'feat': 'B'}),
    # (2, {'feat': 'C'}),
    # (3, {'feat': 'D'}),
    ])
q.add_edges_from([
    (0, 1),
    # (1, 2),
    # (2, 3),
])

G.add_nodes_from([
    (0, {'feat': 'A'}),
    (1, {'feat': 'B'}),
    (2, {'feat': 'C'}),
    (3, {'feat': 'D'}),
])
G.add_edges_from([
    (0, 1),
    (1, 2),
    (2, 3),
])
"""


# m = matcher.BaseMatcher(G)
print(q.nodes)
print(q.edges)
# m = matcher.GQLMatcher(G)
m = matcher.CECIMatcher(G)
l = m.is_subgraph_match(q)
for i in l:
    print(i)

