import os
import time
import copy
import torch
import argparse
import numpy as np
import networkx as nx

from .config import parse_optimizer, parse_encoder
from .. import utils
from . import models
from . import BaseMatcher

class NeuralMatcher(BaseMatcher):
    def __init__(self, G):
        super().__init__(G)
        self.M = {}
        self.filter_rate = 1
        self.en_counter = 0
        self.G_labels = nx.get_node_attributes(G, 'feat')
        self.G_degree = G.degree()

    # Filter
    def LDF(self, q):
        """
        This function takes in a query graph and a target graph
        Returns a list of all the candidate vertex for each node in q filtered by LDF

        LDF: L(v) = L(u) and d(v) > d(u), as v in the candidate vertex
        """
        # Add Time Stamp
        print('Running LDF...')
        start_time = time.time()
        res = []
        q_degree = q.degree()
        q_labels = nx.get_node_attributes(q, 'feat')
        v_set = set()
        for u in q.nodes():
            for v in self.G_nodes:
                if self.G_degree[v] >= q_degree[u]:
                    if self.G_labels[v] == q_labels[u]:
                        res.append((u, v))
        for c in res:
            v_set.add(c[1]) 
        self.filter_rate = len(v_set) / len(self.G_nodes)
        print("--- %s seconds ---, LDF Done" % (time.time() - start_time))
        print(f"After the filtering, { self.filter_rate  * 100}% of the nodes left")
        return res

    def GQL_local_pruning(self, q, candidates):
        res = []
        for c in candidates:
            u, v = c[0], c[1]
            u_profile = self.profile_of_query_node(u, q)
            v_profile = self.profile_of_data_node(v)
            if u_profile.issubset(v_profile):
                res.append((u, v))
        vset = set()
        for c in res:
            vset.add(c[1]) 
        self.filter_rate = len(vset) / len(self.G_nodes)
        print(f"After the filtering, { self.filter_rate  * 100}% of the nodes left")
        return res

    def GQL_global_refinement(self, q, candidates):
        for c in candidates:
            u, v = c[0], c[1]
            n_u = list(q.neighbors(u))
            v_u = list(self.G.neighbors(v))
            for u_prime in n_u: # we want all the u_prime to be matched
                u_prime_matched = False
                for v_prime in v_u:
                    # check if v_prime is u_prime's candidate
                    # -> check (u_prime, v_prime) exists in candidates
                    # if not, than it will not be a fully match
                    # remove (u, v) from candidates
                    match = (u_prime, v_prime)
                    if match in candidates:
                        u_prime_matched = True
                        break
                if u_prime_matched == False:
                    # remove (u, v) from candidates
                    candidates = [c for c in candidates if not (c[1] == v and c[0] == u)]
                    # print(f'{(u, v)} is removed by gql global refinement')
                    break
        vset = set()
        for c in candidates:
            vset.add(c[1])
        self.filter_rate = len(vset) / len(self.G_nodes)
        print(f"After the filtering, { self.filter_rate  * 100}% of the nodes left")

        return candidates

    def filtering(self, G_q):
        imd = self.LDF(G_q)
        time_2 = time.time()
        print('Running GQL local pruning...')
        imd =  self.GQL_local_pruning(G_q, imd)
        time_3 = time.time()
        print(f'--- {time_3 - time_2} seconds ---, local pruning done')
        print('Running Global Refinement...')
        imd = self.GQL_global_refinement(G_q, imd)
        time_4 = time.time()
        print(f'--- {time_4 - time_3} seconds ---, global refinement done')

        return imd

    # Order
    def GQL_ordering(self, q, candidates):
        print('Using GQL ordering...')
        q_nodes = list(q.nodes())
        res = [[i, 0] for i in q_nodes]
        # Count C(u)
        for c in candidates:
            res[c[0]][1] += 1
        res.sort(key = lambda x: x[1])
        res.reverse()
        # print(res)
        res = [i[0] for i in res]
        # print(res)
        return res

    def ordering(self, G_q, imd):
        return self.GQL_ordering(G_q, imd)

    def backward_neighbors(self, u, order, q):
        res = set()
        index = order.index(u)
        neighbors = list(q.neighbors(u))
        keys = [0,1,2]
        ns = [n for n in neighbors if n in list(self.M.keys())]
        res.update(ns)
        return list(res)

    def get_extenable_vertex(self, order, i):
        return order[i - 1]

    def build_model(self, args):
        # build model
        if args.method_type == "order":
            model = models.OrderEmbedder(1, args.hidden_dim, args)
        elif args.method_type == "mlp":
            model = models.BaselineMLP(1, args.hidden_dim, args)
        model.to(utils.get_device())
        if args.test and args.model_path:
            model.load_state_dict(torch.load(args.model_path,
                map_location=utils.get_device()))
        return model

    def gen_alignment_matrix(self, query, model, imd, method_type="order"):
        print(type(query), type(self.G))
        mat = np.zeros((len(query), len(self.G)))
        # print("query target size", len(query), len(target))
        # for u in query.nodes:
        #     for v in target.nodes:
        for (u, v) in imd:
            batch = utils.batch_nx_graphs([query, self.G], anchors=[u, v])
            embs = model.emb_model(batch)
            pred = model(embs[0].unsqueeze(0), embs[1].unsqueeze(0))
            raw_pred = model.predict(pred)
            if method_type == "order":
                raw_pred = torch.log(raw_pred)
            elif method_type == "mlp":
                raw_pred = raw_pred[0][1]
            mat[u][v] = raw_pred.item()
        return mat

    def find_subgraph_match(self, G_q, imd, order):
        import matplotlib.pyplot as plt     # TODO:
        print('enumerating...')
        en_time = time.time()

        if not os.path.exists("plots/"):
            os.makedirs("plots/")
        if not os.path.exists("results/"):
            os.makedirs("results/")

        parser = argparse.ArgumentParser(description='Alignment arguments')
        parse_optimizer(parser)
        parse_encoder(parser)
        args = parser.parse_args()
        args.test = True

        model = self.build_model(args)
        mat = self.gen_alignment_matrix(G_q, model, imd,
            method_type=args.method_type)

        np.save("results/alignment.npy", mat)
        print("Saved alignment matrix in results/alignment.npy")

        plt.imshow(mat, interpolation="nearest")
        plt.savefig("plots/alignment.png")
        print("Saved alignment matrix plot in plots/alignment.png")

        print(f'enumeration done, takes {time.time() - en_time}s')
        print(f'enumeration runs {self.en_counter} times')
        print(f"Totally find {len(self.MatchingList)} matches.")
        output_data = [self.filter_rate, self.MatchingList]
        return output_data    # TODO:

    # Utility functions
    def profile_of_query_node(self, node_index, graph):
        """
        Return a set that contains all the labels of the given
        node's 1-hop neighbors.
        """
        graph_labels = nx.get_node_attributes(graph, 'feat')
        # print(graph_labels)
        neighbors = list(graph.neighbors(node_index))
        # print(neighbors)
        profile = set()
        for n in neighbors:
            profile.add(graph_labels[n])
        return profile

    def profile_of_data_node(self, node_index):
        neighbors = list(self.G.neighbors(node_index))
        profile = set()
        for n in neighbors:
            profile.add(self.G_labels[n])
        return profile
