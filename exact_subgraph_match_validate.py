import os.path as osp
import networkx as nx
import sys
import random
from openGraphMatching.utils import convert_graph, check_match_correctness, draw_graph
from openGraphMatching.matcher import GQLMatcher, CECIMatcher

dataset = 'validate'
path = osp.join(osp.dirname(osp.realpath(__file__)), './dataset', dataset) 
datasetpath = path + '/query_graph/'
G = convert_graph(path + '/data_graph/HPRD.graph')

of = open('generated_ans.res', 'w')
matcher = GQLMatcher(G)

query_prefix = 'query_dense_16_'
# sample = random.sample(range(1,201), 20) 
# print(sample)
# for i in sample:
for i in range(1, 201):
    query_name = query_prefix + str(i)
    query_path = query_name + '.graph'
    print(query_path)
    q = convert_graph(datasetpath + query_path)
    data = matcher.is_subgraph_match(q)
    of.write(f'{query_path}:{len(data[1])}\n')
    print('Filtering rate is', data[0])

