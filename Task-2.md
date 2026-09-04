[README](README.md) | [Introduction](Introduction.md) | [Datasets](Datasets.md) | [Tasks](Tasks.md) | [Task 1](Task-1.md) | Task 2 ⮕ | [Task 3](Task-3.md) | [Notebook](nids-as-centrality-refactored.ipynb)


# Task 2: Betweenness Centrality

The BC of an AS $v$ is defined as:

$$
BC(v) = \frac{1}{S} \sum_{u,w \in V}{\sigma_{uw}{(v)}}, \quad u \ne v \ne w
$$

where $S$ is the total number of paths, and $\sigma_{uw}{(v)}$ is the number of paths from $u$ to $w$ passing through $v$.

## Accumulating the Transit Counts

To compute $BC(v)$, we must collect:

* $S$, the total number of paths in our dataset
* $\sum_{u,w \in V}{\sigma_{uw}{(v)}}$, the number of paths that pass through $v$.

A standard strategy for this type of problem is accumulation. The idea is to iterate over the entire dataset and count how much each path contributes to $S$ and $\sum_{u, w \in V} \sigma_{uw}(v)$.

### Unweighted BC

In the unweighted case, each path contributes:

* $1$ to the total number of paths;
* $1$ to the number of paths passing through $v$, where $v$ ranges over the intermediate ASes.

For example, suppose the observed path is:

*A → B → C → D*

This path contributes $1$ to the total path count and $1$ to the path count for each of *A*, *B*, *C*, and *D*.

### Weighted BC

For weighted BC, paths are weighted according to the amount of address space associated with their origin prefixes.

For each unique path, we calculate its total weight by summing the weights of all prefixes announced by its origin:

```python
weight = sum(pfx_to_weight[o_pfx] for o_pfx in o_pfxs)
```

Thus, a path associated with a larger amount of address space contributes more to the weighted BC than a path associated with a smaller amount of address space.

## Computing the BC Scores

Once the counts have been accumulated, we can compute BC by dividing each AS's path count by the corresponding total.

For an AS (v):

$$
\frac{\text{number of observed paths containing }v}
{\text{total number of observed paths}}
$$

and:
$$
\frac{\text{total weight of paths containing }v}
{\text{total weight of all observed paths}}
$$

we have:

```py
bc_scores = defaultdict(lambda: {"uw": 0.0, "w": 0.0})

for asn in all_asn:
    bc_scores[asn] = {
        "uw": path_with_asn_uw[asn] / total_observed_path_uw,
        "w": path_with_asn_w[asn] / total_observed_path_w,
    }
```

## Plotting BC scores

Like in the BGP assignment, we can create a CCDF of the betweenness centralities.

```py
"""
CCDF for unweighted betweenness centrality.
For each BC value x, count how many ASes have BC >= x,
"""
bc_uw_list = [v for v in bc_df_enriched["uw"] if v > 0]
bc_uw_dist = Counter(bc_uw_list)
x_bc_uw = sorted(bc_uw_dist.keys())
y_bc_uw = []
remaining = len(bc_uw_list) 
for xi in x_bc_uw:
    y_bc_uw.append(remaining)
    remaining -= bc_uw_dist[xi]

"""
CCDF for weighted betweenness centrality.
Same computation, but for weighted betweenness centrality.
"""
bc_w_list = [v for v in bc_df_enriched["w"] if v > 0]
bc_w_dist = Counter(bc_w_list)
x_bc_w = sorted(bc_w_dist.keys())
y_bc_w = []
remaining = len(bc_w_list)
for xi in x_bc_w:
    y_bc_w.append(remaining)
    remaining -= bc_w_dist[xi]
```

[README](README.md) | [Introduction](Introduction.md) | [Datasets](Datasets.md) | [Tasks](Tasks.md) | [Task 1](Task-1.md) | Task 2 ⮕ | [Task 3](Task-3.md) | [Notebook](nids-as-centrality-refactored.ipynb)
