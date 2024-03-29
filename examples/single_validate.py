import os.path as osp
import networkx as nx
import sys
import random
from openGraphMatching.utils import convert_graph, check_match_correctness, draw_graph
from openGraphMatching.matcher import GQLMatcher, CECIMatcher

dataset = 'validate'
path = osp.join(osp.dirname(osp.realpath(__file__)), '../dataset', dataset) 
datasetpath = path + '/query_graph/'
G = convert_graph(path + '/data_graph/HPRD.graph')

matcher = GQLMatcher(G)
print("Nodes in G:", len(G.nodes()))

query_prefix = 'query_dense_16_'
# sample = random.sample(range(1,201), 20) 
# print(sample)
# for i in sample:
for i in range(54, 55):
    query_name = query_prefix + str(i)
    query_path = query_name + '.graph'
    print(query_path)
    q = convert_graph(datasetpath + query_path)
    data = matcher.is_subgraph_match(q)
    print('Filtering rate is', data[0])

