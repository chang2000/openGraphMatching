import torch
from deepsnap.batch import Batch
from deepsnap.dataset import GraphDataset
import networkx as nx

import feature_preprocess

device_cache = None
def get_device():
    global device_cache
    if device_cache is None:
        device_cache = torch.device("cuda") if torch.cuda.is_available() \
            else torch.device("cpu")
        #device_cache = torch.device("cpu")
    return device_cache

def batch_nx_graphs(graphs, anchors=None):
    #motifs_batch = [pyg_utils.from_networkx(
    #    nx.convert_node_labels_to_integers(graph)) for graph in graphs]
    #loader = DataLoader(motifs_batch, batch_size=len(motifs_batch))
    #for b in loader: batch = b
    augmenter = feature_preprocess.FeatureAugment()
    
    if anchors is not None:
        for anchor, g in zip(anchors, graphs):
            for v in g.nodes:
                g.nodes[v]["node_feature"] = torch.tensor([float(v == anchor)])

    batch = Batch.from_data_list(GraphDataset.list_to_graphs(graphs))
    batch = augmenter.augment(batch)
    batch = batch.to(get_device())
    return batch

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
