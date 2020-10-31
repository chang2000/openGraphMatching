import networkx as nx
import sys
import random

from CECIMatcher import CECIMatcher
from GQLMatcher import GQLMatcher
from utils import convert_graph, check_match_correctness

datasetpath = './dataset/validate/query_graph/' 
G = convert_graph('./dataset/validate/data_graph/HPRD.graph')
matcher = GQLMatcher(G)

query_prefix = 'query_dense_16_'

sample = random.sample(range(1,201), 20) 

print(sample)
for i in sample:
    query_name = query_prefix + str(i)
    query_path = query_name + '.graph'
    print(query_path)
    q = convert_graph(datasetpath + query_path)
    data = matcher.is_subgraph_match(q)
    matchlist = data[1]
    flag = True
    for m in matchlist:
        if check_match_correctness(q, G, m) == False:
            flag = False
            break
    if flag:
        print('OK! It seems that every match is right\n')
    else:
        print('No!, i got something wrong\n')
        break
print('All validations passed')
