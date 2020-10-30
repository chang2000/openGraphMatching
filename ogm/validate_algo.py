import networkx as nx
# from SubGraphMatcher import SubGraphMatcher
from CECIMatcher import CECIMatcher
from GQLMatcher import GQLMatcher
from dbutils.convert_graph import convert_graph
import sys

# Smoke Test
def check_edges_exist(num_nodes, match_dict, G, q):
    edges = list(G.edges())
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if (i, j) in list(q.edges()):
                edge = tuple(sorted((e[i], e[j])))
                if edge not in edges:
                    print(f'{edge} not in graph edges')
                    return False
    return True 

datasetpath = './dataset/validate/query_graph/' 
G = convert_graph('./dataset/validate/data_graph/HPRD.graph')

gqlmatch = GQLMatcher(G)
query_prefix = 'query_dense_16_'

f = open('validate_ouput.txt', "w")

for i in range(1, 11):
    query_name = query_prefix + str(i)
    query_path = query_name + '.graph'
    q = convert_graph(datasetpath + query_path)
    data = gqlmatch.is_subgraph_match(q)
    f.write(f"{query_name}:{len(data[1])}\n")

f.close()
