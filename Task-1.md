[README](README.md) | [Introduction](Introduction.md) | [Datasets](Datasets.md) | [Tasks](Tasks.md) | Task 1 ⮕ | [Task 2](Task-2.md) | [Task 3](Task-3.md) | [Notebook](nids-as-centrality-refactored.ipynb)

# Task 1: Process BGP Data

In this task, you will process the BGP RIB snapshots and organize the data into 
structures that will be used to compute AS centrality in the following tasks.

You will parse the RIB files using BGPKIT and extract the information needed to 
represent the BGP topology from multiple viewpoints. In particular, you will:

1. **Store each announced prefix in a radix tree** so you can look up which prefixes 
are contained within others. 
2. **Build a view for each peer** by collecting every AS path observed by that peer.
3. **Keep track of every ASN and peer** that shows up in the data.
4. **Track all unique AS paths across the entire dataset**, since the same AS path
may be observed by multiple peers.

The resulting data structures will provide the foundation for computing both
unweighted and weighted betweenness centrality in Task 2 and hegemony in Task 3.

## Hints:

* Add the announced IPv4 prefix to the radix tree pyt.
* The full AS path is available as `element.as_path`. Split it into individual ASNs, 
then separate the path into atom and the origin ASN `o_asn`.
* Use `element.peer_ip` to identify the peer that observed the announcement.
* Add the observed path and its origin information to that peer's entry in `local_views`.
* Add the peer IP address to `all_peer`.
* Add every ASN in the AS path to `all_asn`.
* Add the path and its origin prefix to `unique_paths`.

[README](README.md) | [Introduction](Introduction.md) | [Datasets](Datasets.md) | [Tasks](Tasks.md) | Task 1 ⮕ | [Task 2](Task-2.md) | [Task 3](Task-3.md) | [Notebook](nids-as-centrality-refactored.ipynb)