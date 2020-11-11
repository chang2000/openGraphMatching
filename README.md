
# openGraphMatching

A graph/subgraph matching library. 

# Usage

Prerequisite `pytorch>=1.6, networkx, pytorch-geometric`

The NaiveMatch is the minium implementation of subgraph matching algorithm.

Here is the demo code for running GQL: 

```python
import openGraphMatching as ogm

# Prepare query graph q and target graph G in advance.

matcherObj = ogm.GQLMatcher(G) # Initialize the object with targer graph G
matcherObj.is_subgraph_match(q) # Run the check match process
```

## Quickstart

- Clone this repo
- Install all prerequisite
-  `pip install openGraphMatching` to install this package
- Run `test.py`or `multi-validate.py` to run the demo

# Misc

1. Validate the algorithm.

   - Use HPRD (9460 nodes, 34998 edges) to validate the correctness.
   - Provides 200 quries(dense, 16 nodes)
   - A correctness checker is implemented in `utils.py`.

2. The data format of the datasets

   1. For each `.graph` file, the first line will always be 

   `t x y` where `x` and `y` are two int indicates the number of nodes and edges

   2. Vertex data  `v v_id v_label v_degree`
   3. Edge data `e v_id v_id`

   
