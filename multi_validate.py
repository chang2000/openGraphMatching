import networkx as nx
import sys
import random

# from openGraphMatching import CECIMatcher
# from openGraphMatching import GQLMatcher
# from openGraphMatching import FilterNeuralMatcher

from openGraphMatching.utils import convert_graph, check_match_correctness, draw_graph
import openGraphMatching as ogm



datasetpath = './dataset/validate/query_graph/' 
G = convert_graph('./dataset/validate/data_graph/HPRD.graph')

of = open('output.txt', 'w')
matcher = ogm.GQLMatcher(G)

query_prefix = 'query_dense_16_'

# sample = random.sample(range(1,201), 20) 

# print(sample)
# for i in sample:
for i in range(1, 201):
    query_name = query_prefix + str(i)
    query_path = query_name + '.graph'
    print(query_path)
    q = convert_graph(datasetpath + query_path)
    draw_graph(q)
    data = matcher.is_subgraph_match(q)
    of.write(f'{query_path}:{len(data[1])}\n')

    # Test wether each match is correct.
    # matchlist = data[1]
    # flag = True
    # for m in matchlist:
        # if check_match_correctness(q, G, m) == False:
            # flag = False
            # break
    # if flag:
        # print('OK! It seems that every match is right\n')
    # else:
        # print('No!, i got something wrong\n')
        # break
# print('All validations passed')
