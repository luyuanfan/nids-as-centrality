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

In task 1 and 2, you will implement parts of the BC and hegemony algorithms and compare their results. 

## Weighing path based on destination AS address count

Previously, we have seen since AS can announce prefixes of very different sizes, counting the raw number of ASes in a customer cone is not a fair metric (instead we count the number of addresses). Similarly here, treating each path towards an destination AS as one equal unit *hides* how much addresses space it routes to. Therefore, we want to weigh each path by the size the AS's address space that it eventually leads to. 

## Formal definitions of BC and hegemony

The betweenness centrality of an AS $v$ is defined as: 

$$
BC(v) = \frac{1}{S} \sum_{u,w \in V}{\sigma_{uw}{(v)}}
$$

where $S$ is the total number of paths, and $\sigma_{uw}{(v)}$ is the number of paths from $u$ to $w$ passing through $v$. 

The hegemony of an AS $v$ is an aggregation of the BC scores of an AS $v$ across a number of viewpoints:

$$
H(v, \alpha) = \frac{1}{n - (2\lfloor\alpha n\rfloor)} \sum_{j=\lfloor\alpha n\rfloor + 1}^{n - \lfloor\alpha n\rfloor} BC_{(j)}(v)
$$

where $n$ is the total number of viewpoints, $2\alpha$ is the ratio of discarded biased viewpoints, and $BC_(j)(v)$ is $v$'s BC value computed with paths from only one viewpoint $j$.

## Observing traffic rerouting on the Internet

So far, we have been seeing AS centrality as a static score at a certain point in time. One of its application is monitoring the *change* of an AS's centrality over a period of time to detect rerouting events. 

Rerouting produces a very specific signature: the AS(es) that lose traffic see their centrality drop, while the AS(es) that absorb the rerouted traffic see theirs rise.

For task 3, you will apply hegemony on real world BGP routing data and interpret the changes in centrality score. 