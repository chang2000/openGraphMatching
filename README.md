
# openGraphMatching

A Python Graph/Subgraph Matching programming library. Based on openGraphMatching and the framework provided, you can develop and test different subgraph matching algorithms efficiently. What's more, since the codebase is Python-based, algorithms with neural networks can be integrated easily with traditional subgraph matching algorithms. 

# Usage

Prerequisite `pytorch>=1.6, networkx, pytorch-geometric, deepsnap`.

A detailed environment configration can be found in `env.yml`.

The `BaseMatcher` is the minium implementation of subgraph matching algorithm.

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
  
  > If you are using conda-like package manager, we provide the conda environment file `env.yml` for this package. You may refer to this [link](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file) to install a conda environment by a environment file. In short, use this command `conda env create -f env.yml`. Then a conda envrionment named `ogm` is created.
  
- `pip install openGraphMatching` to install this package.
- Enter the `examples` folder, then run `python exact_subgraph_match_validate.py`to run the validation demo of this package.

# Internals

Each matcher follows the `filtering->ordering->enumerating` design pattern. In the directory `matcher` there are three files: `filters.py`, `orders.py`,`enumeraters.py`, where each file contains the general algorithms. 

For example, in the graphQL matcher, the code pipeline is like:

```python
from openGraphMatching import BaseMatcher
from openGraphMatching import filters as f
from openGraphMatching import orders as o
from openGraphMatching import enumeraters as e

class GQLMatcher(BaseMatcher):
    def __init__(self, G):
        super().__init__(G)

    def filtering(self, q):
        prefilter = f.Filter(self.G)
        return prefilter.gql_filtering(q)

    def ordering(self, q, candidates):
        orderer = o.Order(self.G)
        return orderer.gql_order(q, candidates)

    def enumerate(self, q, imd, order, i):
        enu = e.Enumerater(self.G)
        enu.normal_enum(q, imd, order, i)
        return enu.res_getter()

    def is_subgraph_match(self, q):
      	# Some verbose and statistics are skipped here
        candidates = self.filtering(q)
        order = self.ordering(q, candidates)
        match_list = self.enumerate(q, candidates, order, 1)
        return match_list
```

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



## Side word

- Cannot handle yeast well even it has a smaller dataset size, since around 10% of nodes left for 3000 nodes.
- The observation above inspires us to combine the traditional subgraph matching methods and the neural methods together.

