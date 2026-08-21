[README](README.md) | [Introduction](Introduction.md) | [Datasets](Datasets.md) | [Tasks](Tasks.md) | Task 1 ⮕ | [Task-2](Task 2.md) | [Notebook](nids-as-centrality.ipynb)


# Task 1: Betweenness Centrality

## Accumulating the Transit Counts
To compute the betweenness centrality at an AS $v$, we must compute:

* $S$, the total number of paths in our dataset;
* $\sum_{u, w \in V} \sigma_{uw}(v)$, the number of paths that pass through $v$.

A standard strategy for this type of problem is accumulation. The idea is to iterate over the entire dataset and count how much each route contributes to $S$ and $\sum_{u, w \in V} \sigma_{uw}(v)$.

In the unweighted case, each route contributes:

* $1$ to the total number of routes;
* $1$ to the number of routes passing through $v$, where $v$ ranges over the intermediate ASes.

![AS path example](images/rib-route.png)

For an explicit example, the AS path above would contribute $1$ to $S$ and $1$ to $\sum_{u, w \in V} \sigma_{uw}(\text{AS 724})$.

The betweenness centrality weighted by the size of the address space is computed in much the same way. The only difference is that we add $w$ instead of $1$, where $w$ is the size of the address space.

Continuing the above example, assuming the entirety of prefix `43.0.0.0/24` belongs to AS 8234, the path would contribute $2^{32 - 24} = 256$ to $S$ and $256$ to $\sum_{u, w \in V} \sigma_{uw}(v)$.

In terms of code:
```py
for elem in iter_routes(RIB_PATHS, dedup=True, expect_routes=n_entries, stats=route_stats):
    # w is the size of the address space ignoring the addresses covered
    # by children ASes
    w = weights.get(elem.prefix)

    # Code to parse out IPv6 paths, AS-sets, duplicate hops, etc.

    total_paths += ?   # Accumulate unweighted
    total_weight += ?  # Accumulate weighted
    for asn in set(path[1:-1]):
        # Iterate all intermediate ASes
        transit_u[asn] += ?  # Accumulate unweighted
        transit_w[asn] += ?  # Accumulate weighted
```

## Computing the Quotients
With the counts we calculated by accumulating, all that remains is to divide each $\sum_{u, w \in V} \sigma_{uw}(v)$ by $S$:

```py
rows = []
for asn_str in all_ases:
    n_paths = transit_u.get(asn_str, 0)  # Number of AS-paths through the AS
    asn_weight = transit_w.get(asn_str, 0)    # Number of paths through the AS weighted by address space size

    # Other variables

    rows.append({
        "bc_unweighted": ?  # Divide the unweighted number of paths by the total number of AS paths
        "bc_weighted": ?    # Divide the weighted number of paths by the total weighted number of paths

        # Other fields
    })
```

## Plotting
Like in the BGP assignment, we can create a CCDF of the betweenness centralities.

```py
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, SURFACE = "#e1e0d9", "#fcfcfb"
BLUE, ORANGE = "#2a78d6", "#eb6834"

def style_axes(ax):
    ax.set_facecolor(SURFACE)
    for spine in ax.spines.values():
        spine.set_color(MUTED)
        spine.set_linewidth(0.8)
    ax.tick_params(colors=MUTED, labelcolor=INK2)
    ax.grid(True, which="both", color=GRID, linewidth=0.6, alpha=0.6)
    ax.set_axisbelow(True)

def ccdf(values):
    xs = sorted(v for v in values if v > 0)  # edge ASes (BC = 0) cannot render on log axes
    return xs, [(len(xs) - i) / len(xs) for i in range(len(xs))]

fig, ax = plt.subplots(figsize=(7, 4.5))
fig.patch.set_facecolor(SURFACE)
style_axes(ax)

xw, yw = ccdf(df["bc_weighted"])
ax.plot(xw, yw, color=BLUE, linewidth=2, label="address-weighted")

ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("Betweenness centrality", color=INK2)
ax.set_ylabel("Proportion of ASes with BC ≥ x", color=INK2)
ax.set_title(f"CCDF of weighted betweenness centrality ({LABEL}, {SNAPSHOT_DATE})",
             color=INK)
fig.tight_layout()
plt.show()
```

[README](README.md) | [Introduction](Introduction.md) | [Datasets](Datasets.md) | [Tasks](Tasks.md) | Task 1 ⮕ | [Task 2](Task-2.md) | [Notebook](nids-as-centrality.ipynb)
