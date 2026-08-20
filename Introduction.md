[README](README.md) | Introduction ⮕ | [Datasets](Datasets.md) | [Tasks](Task.md) | [Task 1](Task-1.md) | [Task 2](Task-2.md) | [Task 3](Task-3.md) | [Notebook](nids-as-centrality-metric.ipynb)

### Prerequisite NIDS Assignments

- [How the Internet assigns and uses Autonomous Systems (ASes)](https://github.com/CAIDA/nids-asn-introduction)
- [Understanding the BGP Control Plane](https://github.com/CAIDA/nids-bgp-control-plane)

### Recommended readings

- [AS Hegemony: A Robust Metric for AS Centrality](https://dl.acm.org/doi/10.1145/3123878.3131982) (A 3-page paper that defines Betweenness Centrality and Hegemony)
- [Characterizing Inter-Domain Rerouting by Betweenness Centrality after Disruptive Events](https://ieeexplore.ieee.org/document/6517118) (An application of BC to observe disruptive events on the Internet)

## What is AS Centrality and what does it offer?

In [nids-asn-introduction](https://github.com/CAIDA/nids-asn-introduction), we introduced **AS customer cone size** as an angle to look at an AS's importance. In this assignment, you will be introduced to *another* angle that evaluates AS importance: **AS centrality**.

Instead of looking at the size of customer cones, AS centrality is interested in quantifying the likelihood of an AS to lie on paths between two other ASes, based on BGP routes. Broadly speaking, significant change in an AS's centrality can be a strong indicator of structural routing changes, potentially anomalous ones. 

## Two metrics: Betweenness Centrality and Hegemony

We focus on *two* common centrality metrics: firstly **Betweenness Centrality (BC)**, then **Hegemony**.

### Betweenness Centrality

Simply put, **betweenness centrality** treats ASes and AS paths as a graph; it then determines centrality of a node (an AS) by computing the fraction of paths that goes through it, out of all existing paths in the graph. Intuitively, one expects high BC scores for transit ASes as they occur on many paths, and low BC scores for stub ASes. By this definition, it requires the full view of the graph — in our case, we ideally would need BGP data from *every* border routers on the Internet.

### Viewpoint bias in BGP data

However, BGP routing data we have is partial. As we have learned in [nids-bgp-control-plane](https://github.com/CAIDA/nids-bgp-control-plane), BGP data archives (such as RouteViews) collect routing tables from only a limited number of viewpoints.

An unwanted consequence is that applying BC on partial BGP data, collected from a small set of viewpoints, risks **inflating the centrality** of the ASes hosting these viewpoints. These ASes may appear on a large share of paths, not because they play a major transit role on the Internet, but simply because that is where data collection happens.

### Hegemony

Therefore, **hegemony** was devised as a variant of BC that takes into account this bias. Instead of trusting every viewpoints, hegemony attempts to drop the viewpoints that are most biased towards the AS *v* in question. More specifically, it drops viewpoints with the highest (or lowest) number of paths passing through *v*. Then, it computes hegemony by averaging the fraction of paths going through *v* for each remaining viewpoint.

In short, the two metrics are very similar conceptually, except that hegemony is an adapatation of BC specifically to decrease collector bias in the context of **observed BGP data**.

## Weighing path based on destination AS address count

In [nids-bgp-control-plane](https://github.com/CAIDA/nids-bgp-control-plane), we have seen since AS can announce prefixes of very different sizes, counting the raw number of ASes in a customer cone is not a fair metric (instead we count the number of addresses). Similarly here, treating each path towards an destination AS as one equal unit hides how much addresses space it routes to.

## Formal definition of BC and hegemony

The betweenness centrality of an AS $v$ is defined by: 

$$
BC(v) = \frac{1}{S} \sum_{u,w \in V}{\sigma_{uw}{(v)}},
\qquad u \neq w \neq v
$$

where $S$ is the total number of paths, and $\sigma_{uw}{(v)}$ is the number of paths from $u$ to $w$ passing through $v$.


## Observing traffic rerouting on the Internet
