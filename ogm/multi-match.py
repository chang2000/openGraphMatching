import networkx as nx
from SubGraphMatcher import SubGraphMatcher
from utils.convert_graph import convert_graph
import sys
import os
import time
import re
import random
master_time = time.time()
dataset_name = 'hprd'
G = convert_graph(f'./dataset/{dataset_name}/data_graph/{dataset_name}.graph')

SGM = SubGraphMatcher(G)
queries = os.listdir(f'./dataset/{dataset_name}/query_graph')
# queries.sort(key=lambda f: int(re.sub('\D', '', f)))
queries.sort()
# random.shuffle(queries)
counter = 0
avg_filter_rate = 1
# for e in queries:
query_times = 0
for i in range(15):
    query_times += 1
    e = queries[i]
    counter += 1
    q = convert_graph(f'./dataset/{dataset_name}/query_graph/' + e)
    print(f'Running query {counter}, query file is {e}')
    # data = SGM.check_match_subgraph(q)
    data = SGM.gql_check_match_subgraph(q)
    avg_filter_rate = (avg_filter_rate * (counter - 1) + data[0]) / counter

print("All queries done, average query time is")
print(f'--- {(time.time() - master_time) / query_times}s ---')
print('Some other data:')
print(f'Average filtering rate is {avg_filter_rate * 100}%')
