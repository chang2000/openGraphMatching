import networkx as nx
from SubGraphMatcher import SubGraphMatcher
from utils.convert_graph import convert_graph
import sys
# Smoke Test
G = convert_graph('./dataset/data_graph/HPRD.graph')
q = convert_graph('./dataset/query_graph/query_dense_16_107.graph')
# query_dense_16_107.graph
SGM = SubGraphMatcher(G)
SGM.check_match_subgraph(q)
