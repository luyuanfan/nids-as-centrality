[README](README.md) | [Introduction](Introduction.md) | [Datasets](Datasets.md) | [Tasks](Tasks.md) | [Task 1](Task-1.md) | [Task 2](Task-2.md) | Task 3 ⮕ | [Notebook](nids-as-centrality-refactored.ipynb)

# Task 3: Hegemony

In this task, you will use the local views created in Task 1 to compute AS hegemony. Hegemony combines the local BC scores from multiple peers into a single score for each AS.

For each ASN, we will:

1. Compute its local BC score from each peer's viewpoint.
2. Treat peers that do not observe the ASN as having a BC score of zero.
3. Sort the BC scores and discard a fraction of the most extreme scores from both ends.
4. Average the remaining scores to obtain the ASN's hegemony.

We use `ALPHA` to control how much of the most extreme scores are discarded from each end.

## Computing BC from each peer

`_bc_for_every_asn_per_peer` computes a local BC score for every ASN observed by one peer.

### Hints:

* `one_peer_view` contains the paths observed by a single peer. Iterate through its atom values and associated `o_asn_pfx_pairs` to examine those paths. 
* Each `(o_asn, o_pfx)` pair identifies an observed path and its origin prefix. Use `pfx_to_weight` to determine how much address space that prefix represents.
* For each observed path, keep track of both its contribution to the unweighted path count and its contribution to the weighted path total.
* For every ASN appearing on a path, track how many paths contain it and how much total path weight those paths represent.
* Use these totals to calculate the unweighted and weighted BC scores for each ASN, and store the two scores together in `peer_scores`.

## Combining all local BC into hegemony

In `compute_hegemony_scores`, first determine how many scores should be removed from each end using `ALPHA` and `all_peer`.

For each peer in `local_views`, use its `one_peer_view` to compute that peer's local BC scores. Store these results in `peer_scores` so that they can later be looked up for individual ASNs.

### Hints:

* `bc_score_lst_uw` and `bc_score_lst_w` should contain the unweighted and weighted BC scores for `target_asn` across all peers in `all_peer`.
* If a peer does not have a score for `target_asn`, treat its score as zero. This represents a viewpoint that did not observe that ASN.
* Sort both score lists so that the most biased viewpoints can be removed from each end.
* Use `n_drop` to remove the same number of scores from the low and high ends of each list.
* Average the remaining scores and store the results in `hege_scores[target_asn]["uw"]` and `hege_scores[target_asn]["w"]`.

[README](README.md) | [Introduction](Introduction.md) | [Datasets](Datasets.md) | [Tasks](Tasks.md) | [Task 1](Task-1.md) | [Task 2](Task-2.md) | Task 3 ⮕ | [Notebook](nids-as-centrality-refactored.ipynb)
