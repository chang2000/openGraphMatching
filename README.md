# openGraphMatching

A graph/subgraph matching library.



# Introduction



# Usage/Demo



# Details on the implmentation

## 1. The data format of the *candidates*

The *candiates* is generated in the fitering part. It's stored as **Array of Tuples**. For node $u_i$ in the query graph, if $v_j$ can be the corresponding node in the target graph, then the tuple $(u_i, v_j)$ will be stored in the final list. 

Considering the complex operation on candidates in *CFL-like* algorithms, store the candidates with a dictionary **MAY ALSO BE ENSSENTIAL**.

> Why use tuple?  
>
> Can we have a better idea?

## 2. 

# Misc

1. Validate the algorithm.

   - Use HPRD (9460 nodes, 34998 edges) to validate the correctness.
   - Provides 200 quries(dense, 16 nodes)
   - a `expected_output.res` is provided with the file name and correct answer

2. The data format of the datasets

   1. For each `.graph` file, the first line will always be 

   `t x y` where `x` and `y` are two int indicates the number of nodes and edges

   2. Vertex data  `v v_id v_label v_degree`
   3. Edge data `e v_id v_id`

3. 