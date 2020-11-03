
# openGraphMatching

A graph/subgraph matching library. Still under construction.







# Usage/Demo

The NaiveMatch is the minium implementation of subgraph matching algorithm.

Here is the demo code for running GQL: 

```python
import GQLMatcher from GQLMatcher

# Prepare query graph q and target graph G in advance.

matcherObj = GQLMatcher(G) # Initialize the object with targer graph G
matcherObj.is_subgraph_match(q) # Run the check match process
```
   
