# Use this file to generate the networkx instance.
import networkx as nx

def convert_graph(filepath):
    f = open(filepath, "r")
    # retrive the information of the first line
    first_line = f.readline()
    meta_data = first_line.split(' ')
    num_nodes = int(meta_data[1])
    num_edge = int(meta_data[2])
    graph_nodes = []
    graph_edges = []
    # read nodes
    # ['e', $node_id, $node_label, $node_degree]
    for _ in range(num_nodes):
        line = f.readline()
        node_data = line.split(' ')
        graph_nodes.append((int(node_data[1]), {'feat' : node_data[2]}))
        
    # read edges
    for _ in range(num_edge):
        line = f.readline()
        edge_data = line.split(' ')
        graph_edges.append((int(edge_data[1]), int(edge_data[2])))
    g = nx.Graph()
    g.add_nodes_from(graph_nodes)
    g.add_edges_from(graph_edges)
    return g