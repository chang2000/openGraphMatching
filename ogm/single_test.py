import networkx as nx
from SubGraphMatcher import SubGraphMatcher
from utils.convert_graph import convert_graph
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



G = convert_graph('./dataset/data_graph/HPRD.graph')
q = convert_graph('./dataset/query_graph/query_dense_16_5.graph')
# G = convert_graph('./dataset/sample_dataset_copy/target.graph')
# q = convert_graph('./dataset/sample_dataset_copy/query_graph/query-1.graph')
# query_dense_16_107.graph
SGM = SubGraphMatcher(G)
data = SGM.check_match_subgraph(q)
# print(data[0])
for e in data[1]:
    print(e)
    print(check_edges_exist(len(list(q.nodes())), e, G, q))
    # nodes = []
    # for i in range(len(e)):
        # nodes.append(e[i])
    # print(nodes)
    # get the subgraph
    # subgraph = G.subgraph(nodes)
    # print(nx.is_connected(subgraph))
    # SGM_Small = SubGraphMatcher(subgraph)
    # SGM_Small.check_match_subgraph(q)
