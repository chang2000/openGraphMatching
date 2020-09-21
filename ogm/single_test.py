import networkx as nx
from SubGraphMatcherEnhanced import SubGraphMatcher
from utils.convert_graph import convert_graph
import sys
# Smoke Test
G = convert_graph('./dataset/data_graph/HPRD.graph')
q1 = convert_graph('./dataset/query_graph/query_dense_16_1.graph')
print(nx.is_connected(G))
SGM = SubGraphMatcher(G)
SGM.check_match_subgraph(q1)
