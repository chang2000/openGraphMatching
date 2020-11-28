
# openGraphMatching

A Python Graph/Subgraph Matching programming library. Based on openGraphMatching and the framework provided, you can develop and test different subgraph matching algorithms efficiently. What's more, since the codebase is Python-based, algorithms with neural networks can be integrated easily with traditional subgraph matching algorithms. 

Read our [report](http://www.cse.cuhk.edu.hk/~tcwang8/report.pdf) for more information.(Not provided now)

# Usage

Prerequisite `pytorch>=1.6, networkx, pytorch-geometric, deepsnap`

The NaiveMatch is the minium implementation of subgraph matching algorithm.

Here is the demo code for running GraphQL algorithm: 

```python
import openGraphMatching.matcher as matcher

# Prepare query graph q and target graph G in advance. q and G are networkx instance.

m = matcher.GQLMatcher(G) # Initialize the object with targer graph G
m.is_subgraph_match(q) # Run the check match process
```

# Quickstart

- Clone this repository: `git clone https://github.com/chang2000/openGraphMatching`
- Install all prerequisite
  - [`networkx`](https://networkx.org/)
  - [`pytorch-geometric`](https://github.com/rusty1s/pytorch_geometric)
  - [`deepsnap`](https://github.com/snap-stanford/deepsnap)
-  `pip install openGraphMatching` to install this package.
- Go to `examples` and enjoy~

# Misc

1. Validate the correctness of algorithm.

   - We use HPRD (9460 nodes, 34998 edges) to validate the correctness considering the time consuming and program performance.
   - We provides 200 quries(dense, 16 nodes).
   - A correctness checker is implemented in `utils.py`.
   - Expected result of all the matching are provided in `expected.res`. Refer to the dataset `validate` for more information.

2. The data format of the datasets

   1. For each `.graph` file, the first line will always be `t x y` where `x` and `y` are two int indicates the number of nodes and edges

   2. Vertex data  `v v_id v_label v_degree`
3. Edge data `e v_id v_id`
   
   
