import networkx as nx
from CECIMatcher import CECIMatcher
from GQLMatcher import GQLMatcher
from NaiveMatcher import NaiveMatcher

from dbutils.convert_graph import convert_graph
import sys

# Smoke Test
def check_edges_exist(num_nodes, match_dict, G, q):
    edges = list(G.edges())
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if (i, j) in list(q.edges()):
                edge = tuple(sorted((e[i], e[j])))
                if edge not in edges:
                    print(f'{edge} not in graph edges')
                    return False
    return True 

# G = convert_graph('./dataset/hprd/data_graph/hprd.graph')
# q = convert_graph('./dataset/hprd/query_graph/query_sparse_32_200.graph')


# YouTube Dataset
# G = convert_graph('./dataset/youtube/data_graph/youtube.graph')
# q = convert_graph('./dataset/youtube/query_graph/query_dense_4_5.graph')

# Wordnet Dataset
# G = convert_graph('./dataset/wordnet/data_graph/wordnet.graph')
# q = convert_graph('./dataset/wordnet/query_graph/query_dense_20_9.graph')

G = convert_graph('./dataset/validate/data_graph/HPRD.graph')
# q = convert_graph('./dataset/validate/query_graph/query_dense_16_1.graph')
q = convert_graph('./dataset/validate/query_graph/query_dense_16_2.graph')
"""
# Classic Dataset
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
#"""
# cecimatch = CECIMatcher(G)
# data = cecimatch.is_subgraph_match(q)

# gqlmatch = GQLMatcher(G)
# data = gqlmatch.is_subgraph_match(q)

naivematch = NaiveMatcher(G)
naivematch.is_subgraph_match(q)

