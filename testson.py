import networkx as nx
from dbutils.convert_graph import convert_graph
from dbutils.check_subgraph_correctness import check_subgraph_correctness

import sys
from SubGraphMatcher import SubGraphMatcher
from NaiveMatcher import NaiveMatcher

class Test(SubGraphMatcher):
    def __init__(self, G):
        super().__init__(G);
        self.M = {};
        self.filter_rate = 1
        self.enumerate_counter = 1

    def printInfo(self):
        # print('The G nodes is', self.G_nodes)
        # print('The G edges is', self.G_edges)
        # print('The G degree is', self.G_degree)
        print('The G labels is', self.G_labels)
        # print('After regeneration, The G labels is', G_labels)


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

matcher = NaiveMatcher(G)
data = matcher.is_subgraph_match(q)
ml = data[1]
print(ml)

for m in ml:
    print(check_subgraph_correctness(q, G, m))
