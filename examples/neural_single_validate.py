import networkx as nx
from openGraphMatching import NeuralMatcher

from openGraphMatching.utils import convert_graph
from openGraphMatching.utils import check_match_correctness

import sys

G = convert_graph('./dataset/validate/data_graph/HPRD.graph')
# q = convert_graph('./dataset/validate/query_graph/query_dense_16_6.graph')
q = convert_graph('./dataset/validate/query_graph/query_dense_16_1.graph')

neuralmatch = NeuralMatcher(G)
data = neuralmatch.is_subgraph_match(q)

matchlist = data[1]
f = open("matchlist.data", "w")
for i in matchlist:
    f.write(str(i))
    f.write('\n')
f.close()

flag = True
for m in matchlist:
    if check_match_correctness(q, G, m) == False:
        flag = False
if flag:
    print('OK! It seems that every match is right')
else:
    print('No!, i got something wrong')

# Check duplicates
# print('Checking if there are any duplicates in the matching list...')
# unique_list = []
# for m in matchlist:
    # if m not in unique_list:
        # unique_list.append(m)
# if len(matchlist) == len(unique_list):
    # print('Yes, NO DUPLICATEs are found')
# else:
    # print('NONONONO, DUPLICATEs found')


