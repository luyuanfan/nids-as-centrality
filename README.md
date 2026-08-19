# etp-as-centrality-metric

This repository contains an implementation of the betweenness centrality metric based on RIPE RIS MRT file data.

## Notebook

[`as-betweenness-centrality.ipynb`](as-betweenness-centrality.ipynb) downloads
one or more RIPE RIS `bview` RIB snapshots (MRT format), parses them with
[`pybgpkit`](https://github.com/bgpkit/bgpkit-parser), merges them into a single
route set deduplicated by *(prefix, AS path)*, and computes the
betweenness centrality of every transit AS over the observed AS paths — both
unweighted (path count) and weighted by the number of IPv4 addresses of each
path's destination prefix (longest-prefix-match deduplicated, so nested
announcements are not double-counted).

The metric follows Liu, Luo, Chang & Su,
[*Characterizing Inter-domain Rerouting by Betweenness Centrality after
Disruptive Events*](https://rockykcc.github.io/pub/JSAC-betweenness-centrality-13.pdf)
(IEEE JSAC 2013). The data-handling approach mirrors the
[nids-bgp-control-plane-key](https://github.com/CAIDA/nids-bgp-control-plane-key)
reference notebook.

## Running

The notebook installs its own dependencies (`pybgpkit-parser`, `pytricia`,
`pandas`, `matplotlib`) in its first cell. The collectors and snapshot timestamp
are set at the top of the download cell: `COLLECTORS` is a list, and listing
several (e.g. `["rrc00", "rrc06", "rrc10"]`) merges their vantage points into
one route set, dropping routes already seen. The default is `["rrc00"]`
(Amsterdam multihop, largest peer set, ~414 MB download); use
`COLLECTORS = ["rrc06"]` for a quick test run that finishes in a few minutes.
Snapshots are cached under `data/`.
