import networkx as nx
from SubGraphMatcherEnhanced import SubGraphMatcher
from utils.convert_graph import convert_graph
import sys
import os
# get the file list


# G = convert_graph('./dataset/data_graph/HPRD.graph')
G = convert_graph('./dataset/sample_dataset_copy/target.graph')
print(nx.is_connected(G))
SGM = SubGraphMatcher(G)
dataset_path = './dataset/sample_dataset_copy/'
# dataset_path = './dataset/'
# queries = os.listdir(dataset_path + 'query_graph')
queries = os.listdir(dataset_path + 'query_graph')
counter = 0
for e in queries:
    counter += 1
    q = convert_graph(dataset_path + 'query_graph/' + e)
    # q = convert_graph('./dataset/query_graph/' + e)
    print(f'Running query {counter}...')
    SGM.check_match_subgraph(q)



