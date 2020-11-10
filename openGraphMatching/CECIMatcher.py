import time
import sys
import copy
import networkx as nx
from . import SubGraphMatcher

class CECIMatcher(SubGraphMatcher):
    def __init__(self, G):
        super().__init__(G)
        self.M = {}
        self.filter_rate = 1
        self.en_counter = 1 # What is the en_counter BTW

    def filtering(self, q):
        pass

    def ordering(self, q, candidates):
        pass

    def enumerate(self, q, C, A, order, i):
        self.en_counter += 1
        if i == len(order) + 1:
            if  self.M != None:
                if len(self.M) == len(list(q.nodes())):
                    M_copy = copy.deepcopy(self.M)
                    self.MatchingList.append(M_copy)
            return self.M
        # v is a extenable vertex
        u = self.get_extenable_vertex(order, i)
        lc = self.ceci_compute_LC(q, C, A, order, u, i)
        for c in lc:
            if c not in self.M and c[1] not in self.M.values():
                self.M[c[0]] = c[1]
                self.enumerate(q, C, A, order, i + 1)
                del self.M[c[0]]
    
    def ceci_compute_LC(self, q, C, A, order, u, i):
        if i == 1: # do not care the edge
            res = []
            for c in A[u][0]:
                res.append((u, c))
            return res

        bn = self.backward_neighbors(u, order, q)
        lc = []
        if len(bn) == 1:
            up = A[u][2][0]
            # find all edges, and all point out from up
            up_edges = A[up][1]
            M_u_p = self.M[up]
            for e in up_edges:
                if e[0] == M_u_p and e[1] in A[u][0]:
                    lc.append((u, e[1]))
            return lc 
        else: 
            set_list = []
            for u_prime in bn:
                M_u_prime = self.M[u_prime]
                u_prime_edges = A[u_prime][1]
                tmp_lc = set()
                for e in u_prime_edges:
                    if e[0] == M_u_prime and e[1] in A[u][0]:
                        tmp_lc.add((u, e[1]))
                set_list.append(tmp_lc)
            inct = set.intersection(*set_list)
            lc = list(inct)
        return lc


    def is_subgraph_match(self, q):
        print("CECI is used...")
        main_start_time = time.time()
        # init the current matching first
        self.filter_rate = 1
        self.MatchingList = []
        self.M = {}
        try:
            assert (isinstance(q, nx.classes.graph.Graph) and nx.is_connected(q))
        except:
            print('Input query graph must be a single networkx instance.')
            sys.exit()
        
        imd = self.LDF(q)
        imd = self.NLF(q, imd)
        NLF_candidates = copy.deepcopy(imd)
        time1 = time.time()
        print('ceci filtering is running...')
        imd = self.ceci_filtering(q, imd)
        print(f'--- {time.time() - time1} seconds ---, ceci ordering done')
        print()
        C = imd[0]
        A = imd[1]
        order = self.ceci_ordering(q, NLF_candidates)

        print('enumerating...')
        en_time = time.time()

        self.enumerate(q, C, A, order, 1)

        print(f'enumeration done, takes {time.time() - en_time}s')
        print(f'enumeration runs {self.en_counter} times')
        print("--- %s seconds ---, Job done" % (time.time() - main_start_time))
        # print(f"Totally find {len(self.MatchingList)} matches.")
        print(' ')
        print(' ')
        output_data = [self.filter_rate, self.MatchingList]
        return output_data

    def ceci_ordering(self, q, candidates):
        # The candidates is NLF candidates
        # Find the sourc for the bfs
        source = self.generate_bfs_source(q, candidates)
        tree = self.generate_bfs_tree(q, source)
        return list(tree.nodes())

    def generate_bfs_tree(self, q, source):
        tree = nx.bfs_tree(q, source=source)
        return tree

    def generate_bfs_source(self, q, candidates):
        can_dict = self.can_to_dict(candidates)
        nodes = list(q.nodes())
        minimum = float('inf')
        minimun_node = None
        for n in nodes:
            # print(len(can_dict[n]) / q.degree[n])
            value = len(can_dict[n]) / q.degree[n]
            if value < minimum:
                minimum = value
                minimum_node = n
        return  minimum_node

    def ceci_filtering(self, q, candidates):
        source = self.generate_bfs_source(q, candidates)
        bfs_tree = self.generate_bfs_tree(q, source)
        can_dict = self.can_to_dict(candidates) 
        traversal_order = self.ceci_ordering(q, candidates)
        """
        Build the auxiliary data structure
        """
        A = dict()
        for u in traversal_order:
            tmp = []
            tmp.append(u)
            A[u] = list()
            A[u].append(can_dict[u])
            edges = set()
            successors = list(bfs_tree.successors(u))
            predecessors = list(bfs_tree.predecessors(u))
            for up in successors:
                for v in can_dict[u]:                       
                    for vp in can_dict[up]:
                        # print(sorted((v,vp)))
                        tup = tuple(sorted((v, vp)))
                        if tup in self.G_edges:
                            # print(f'Caught! Add {(v, vp)} to edges')
                            edges.add((v, vp))                        
            A[u].append(edges)
            # Also need to find the node u's tree parent
            A[u].append(predecessors)
            

        # monitor the A
        # for a in A.keys():
        #     print(a, A[a])

        # Do the filtering
        # reverse_traversal_order = traversal_order.reverse()
        reverse_traversal_order = traversal_order
        for u in reverse_traversal_order: 
            # print('checking', u)
            # print('-----------')
            # Get N(u)
            neigh_of_u = list(q.neighbors(u))
            # iterate v, the data node
            can_of_u = copy.deepcopy(can_dict[u])
            for v in can_dict[u]:
                # get v's neighbors
                neigh_of_v = set(self.G.neighbors(v))
                # print(f'the neighbor of {v} is {neigh_of_v}')
                # Check weather N(v) \intersect C(u') is empty
                flag = True
                for u_prime in neigh_of_u:
                    can_u_prime = set(can_dict[u_prime])
                    # set operation
                    if can_u_prime & neigh_of_v:
                        inct = can_u_prime & neigh_of_v
                        # print('inct is', inct)
                        for vp in inct:
                            edge = [v, vp]
                            edge.sort()
                            edge = tuple(edge)
                            if edge in self.G_edges and reverse_traversal_order.index(u_prime) > traversal_order.index(u):
                                A[u][1].add((v, vp))
                    else:
                        flag = False
                        break

                if flag == False:
                    # remove v from u's candidates
                    # print(f'going to remove v{v}')
                    can_of_u.remove(v)
                    A[u][0] = can_of_u
                    # remove all the edges related to v
                    for a in A.keys():
                        A[a][1] = list(A[a][1])
                        for e in A[a][1]:
                            if v in e:
                                # print(f'remove {e} from {a} de edges')
                                A[a][1].remove(e)
                        A[a][1] = set(A[a][1])
            can_dict[u] = can_of_u   

        res = self.dict_to_can(can_dict)
        v_set = set()
        for c in res:
            v_set.add(c[1]) 
        self.filter_rate = len(v_set) / len(self.G_nodes)
        print(f"After ceci filtering, { self.filter_rate  * 100}% of the nodes left")
        return [res, A]

    def can_to_dict(self, candidates):
        res = dict({})
        last_node = None
        tmp_list = []
        for c in candidates:
            if c[0] == last_node:
                tmp_list.append(c[1])
            else:
                if last_node != None:
                    res[last_node] = tmp_list
                tmp_list = []
                last_node = c[0]
                tmp_list.append(c[1])
        res[last_node] = tmp_list
        return res

    def dict_to_can(self, dic):
        res = [] 
        for k in dic.keys():
            for v in dic[k]:
                res.append((k, v))
        return res  
    # generate the data structure
