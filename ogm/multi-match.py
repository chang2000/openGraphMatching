import networkx as nx
from SubGraphMatcherEnhanced import SubGraphMatcher
from utils.convert_graph import convert_graph
import sys
import os
import time

master_time = time.time()

G = convert_graph('./dataset/data_graph/HPRD.graph')
# G = convert_graph('./dataset/sample_dataset_copy/target.graph')
SGM = SubGraphMatcher(G)
dataset_path = './dataset/'
# dataset_path = './dataset/sample_dataset_copy/'
queries = os.listdir(dataset_path + 'query_graph')
queries.sort()
# print(queries)
counter = 0
avg_filter_rate = 1
# for e in queries:
for i in range(2):
    e = queries[i]
    counter += 1
    q = convert_graph(dataset_path + 'query_graph/' + e)
    print(f'Running query {counter}, query file is {e}')
    data =  SGM.check_match_subgraph(q)
    avg_filter_rate = (avg_filter_rate * (counter - 1) + data[0]) / counter

print("All queries done, average query time is")
print(f'--- {(time.time() - master_time) / len(queries)}s ---')
print('Some other data:')
print('Average filtering rate is', avg_filter_rate)
