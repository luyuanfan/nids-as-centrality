[README](README.md) | Introduction ⮕ | [Datasets](Datasets.md) | [Tasks](Tasks.md) | [Task 1](Task-1.md) | [Task 2](Task-2.md) | [Task 3](Task-3.md) | [Notebook](nids-as-centrality-refactored.ipynb)

### Prerequisite NIDS Assignments

- [How the Internet assigns and uses Autonomous Systems (ASes)](https://github.com/CAIDA/nids-asn-introduction)
- [Understanding the BGP Control Plane](https://github.com/CAIDA/nids-bgp-control-plane)

### Recommended readings

- [AS Hegemony: A Robust Metric for AS Centrality](https://dl.acm.org/doi/10.1145/3123878.3131982) &mdash; A 3-page quick read. It defines Betweenness Centrality (BC) and Hegemony. Reading it will be **very useful** for understanding this assignment. 
- First 3 pages of [Characterizing Inter-Domain Rerouting by Betweenness Centrality after Disruptive Events](https://ieeexplore.ieee.org/document/6517118) &mdash; An application of BC to observe disruptive events on the Internet.

## What is AS Centrality and what does it offer?

In [nids-asn-introduction](https://github.com/CAIDA/nids-asn-introduction), we introduced **AS customer cone size** as an angle to look at an AS's importance. In this assignment, you will be introduced to *another* angle that evaluates AS importance: **AS centrality**.

Instead of looking at the size of customer cones, AS centrality quantifies how often the AS lies on paths between two other ASes, based on BGP routes.

## Two metrics: Betweenness Centrality and Hegemony

We focus on *two* common centrality metrics: **Betweenness Centrality (BC)** and **Hegemony**.

### Betweenness Centrality (BC)

**BC** treats ASes and AS paths as a graph. It then determines centrality of a node (an AS) by computing the fraction of paths that goes through it, out of all existing paths in the graph. Intuitively, one expects high BC scores for transit ASes as they occur on many paths, and low BC scores for stub ASes. By this definition, it requires the full view of the entire Internet graph &mdash; in our case, we ideally would need BGP data from *every* AS on the Internet. 

### Viewpoint bias in BGP data

Sadly, gathering data from every AS is not practically possible, considering the amount of cooperation it demands. As we learned in the [BGP assignment](https://github.com/CAIDA/nids-bgp-control-plane), BGP data archives (such as RouteViews and RIPE RIS) collect routing tables from only a limited number of peers and viewpoints (VPs). That is to say, we only have partial BGP routing data to work with. 

An unwanted consequence of applying BC on partial BGP data risks **inflating the centrality** of ASes that are topographically close to the viewpoints. These ASes may appear on a large portion of paths, not because they play a major transit role on the Internet, but simply because they are where data collection happens.

### AS Hegemony

Therefore, **AS hegemony** was devised as a variant of BC that takes into account this bias. Instead of trusting every viewpoint, hegemony drops the viewpoints that are most biased towards a given AS $v$. 

More specifically, to compute the hegemony score of an AS $v$, each viewpoint $w$ in the graph would give $v$ an BC score based on all the AS paths that $w$ observes. Then, we want to drop the most biased viewpoints towards $v$ (i.e., dropping the viewpoints that give $v$ the highest and lowest BC scores). Finally, we average the remaining BC scores and assign it as the hegemony score for $v$.

### Comparison

In short, the two metrics are very similar conceptually, except that hegemony is an adaptation of BC specifically to decrease viewpoint bias in the context of **observed BGP data**. 

In this module, you will implement parts of the BC and hegemony algorithms and compare their results.

## Weighing path based on destination prefix size

Previously, we saw that ASes can announce prefix blocks of very different sizes. Consequently, simply counting the number of announced prefixes in a customer cone is not an adequate proxy for an AS's topological importance; instead, we count the number of IP addresses covered by those prefixes.

Similarly, in this module, treating every path to a destination AS as equally important *hides* the amount of address space reachable with that path. Therefore, we weight each path by the size of the announced prefix associated with its destination.

## Formal definitions of BC and hegemony

### BC

The BC of an AS $v$ is defined as:

$$
BC(v) = \frac{1}{S} \sum_{u,w \in V}{\sigma_{uw}{(v)}}, \quad u \ne v \ne w
$$

where $S$ is the total number of paths, and $\sigma_{uw}{(v)}$ is the number of paths from $u$ to $w$ passing through $v$.

### Hegemony

The hegemony of an AS $v$ is the average of its BC scores across a set of viewpoints, after discarding the viewpoints that are most biased toward or away from $v$:

$$
H(v, \alpha) =
\frac{1}{n - 2\lfloor\alpha n\rfloor}
\sum_{j=\lfloor\alpha n\rfloor + 1}^{n-\lfloor\alpha n\rfloor} BC_j(v)
$$

where $n$ is the total number of viewpoints, $2\alpha$ is the fraction of viewpoints discarded, and the $BC_j(v)$ values are sorted from lowest to highest.

The BC score of $v$ from viewpoint $j$ is:

$$
BC_j(v) =
\begin{cases}
\displaystyle
\frac{1}{S_j}
\sum_{u,w \in V} \sigma_{uw}^{j}(v)
& \text{if viewpoint } j \text{ observes } v \\
0
& \text{otherwise}
\end{cases}
$$

where $S_j$ is the total number of paths observed by viewpoint $j$, and $\sigma_{uw}^{j}(v)$ is the number of paths from $u$ to $w$, as observed by viewpoint $j$, that pass through $v$.

The resulting $BC_j(v)$ values are then sorted, and the most extreme values are discarded before averaging the remaining scores.

[README](README.md) | Introduction ⮕ | [Datasets](Datasets.md) | [Tasks](Tasks.md) | [Task 1](Task-1.md) | [Task 2](Task-2.md) | [Task 3](Task-3.md) | [Notebook](nids-as-centrality-refactored.ipynb)