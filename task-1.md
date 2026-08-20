[README](README.md) | [Introduction](introduction.md) | [Tasks](tasks.md) | Task-1 | [Task-2](task-2.md) | [Notebook](as-betweenness-centrality.ipynb)

# Guide: Task 1

This guide walks through what the `as-betweenness-centrality` notebook does, why it's structured the way it is, and how to read its output. It follows the notebook's own cell order.

## 1. What the notebook computes

The notebook downloads BGP routing table snapshots ("RIB dumps") from RIPE RIS route collectors and computes, for every **transit AS** (Autonomous System), a **betweenness centrality** score: roughly, "what fraction of all observed Internet routes pass through this AS as a middleman?"

It computes two versions of that score:

- **Unweighted `bc_unweighted`** — the fraction of *distinct AS paths* that transit the AS.
- **Address-weighted `bc_weighted`** — the fraction of *routed IPv4 address space* that transits the AS, so a path to a huge legacy `/8` counts far more than a path to a single `/24`.

The metric is adapted from Liu, Luo, Chang & Su's 2013 IEEE JSAC paper *"Characterizing Inter-domain Rerouting by Betweenness Centrality after Disruptive Events,"* which defines centrality over AS paths actually observed in BGP (not shortest paths in an abstract graph, since BGP is policy-routed and doesn't take shortest paths).

## 2. The math, in plain terms

For a route from peer AS $u$ to origin AS $w$, every AS strictly in between is a "transit hop." Given the set $P$ of all distinct routes seen:

$$BC(v) = \frac{\text{number of routes in } P \text{ that transit } v}{|P|}$$

The address-weighted version replaces "count of 1" with "size of the destination prefix," using each prefix's **longest-prefix-match weight** — its full address-space size minus whatever is covered by more specific prefixes announced inside it (so no address is double-counted):

$$BC_w(v) = \frac{\sum_{\text{routes transiting } v} w(\text{destination prefix})}{\sum_{\text{all routes}} w(\text{destination prefix})}$$

Both scores land in $[0, 1]$.

## 3. Data source: RIPE RIS `bview` snapshots

RIPE RIS collectors (`rrc00`, `rrc01`, `rrc06`, `rrc10`, etc., at different global locations) each dump their full routing table every 8 hours as an MRT `bview` file. A single collector only sees the routes its own peers hand it, so it gives a *biased* view of the topology — the notebook lets you list several collectors in `COLLECTORS` to merge their vantage points into one broader (though never fully unbiased) path set.

Key config variables at the top:

| Variable | Purpose |
|---|---|
| `COLLECTORS` | Which RIS collectors to merge, e.g. `["rrc00", "rrc15", "rrc23"]` |
| `SNAPSHOT_DATE` / `SNAPSHOT_TIME` | All collectors must share one timestamp — the metric is defined on paths observed at a single instant |

Files are downloaded once and cached under `data/`, so re-running the notebook later costs nothing extra.

## 4. Aggregating collectors into one route set (`iter_routes`)

`iter_routes` is the shared reader used by both passes. It streams MRT announcement records from each file in turn and, when `dedup=True`, drops any route already seen — where a route is identified by its **(prefix, AS path)** pair. This matters because the same route commonly shows up at multiple collectors (e.g. a multihop peer feeding both `rrc00` and its local IXP collector), and counting it twice would distort the centrality numbers.

**Memory trick — `SeenKeys`.** Deduplicating tens of millions of routes means remembering every key seen so far. Instead of a Python `set` of hashes (~72 bytes/entry), the notebook implements `SeenKeys`: an open-addressed hash table backed by a raw `array("q")` of 64-bit integers (~16–32 bytes/entry). This roughly triples memory efficiency at the cost of ~20% more CPU time — worthwhile when the table holds ~10⁸ entries. The trade-off is a very small (< 0.1%) chance of two distinct routes colliding on the same 64-bit hash and one being dropped.

## 5. Pass 1 — collect announced IPv4 prefixes

Before any route can be *address-weighted*, the notebook needs the complete set of announced IPv4 prefixes (across all merged snapshots), because a prefix's weight depends on which other prefixes are nested inside it. Pass 1 just builds that set — `dedup=False` here, since collecting into a `set` already discards repeats for free, and skipping route-key deduplication saves the memory pass 2 will need.

## 6. Address weight per prefix (`address_weights`)

This function builds a `pytricia` longest-prefix-match trie over every announced IPv4 prefix and computes each one's **weight**: its full size ($2^{32-\text{length}}$) minus the sizes of prefixes announced *directly* inside it (its immediate children in the trie). Subtracting only direct children — not all descendants — is enough to remove every covered address exactly once, no matter how deeply nested the announcements are.

Two edge cases to know:

- A prefix fully covered by more-specific announcements gets **weight 0** — it still counts toward the unweighted metric, but contributes no address mass.
- `0.0.0.0/0` (a default route) is dropped outright, since it would otherwise swallow all unannounced address space.

The function returns two dictionaries: one keyed by the *raw* prefix strings from the MRT file (for fast lookup in pass 2), one keyed by *normalized* prefixes (for computing totals). Sanity check printed after this cell: total routed IPv4 space should land around **3.1 billion addresses (~73% of all of IPv4)**.

> **Note:** in the saved notebook, the output of this cell shows a Jupyter kernel crash right after printing the weight totals. The numbers it printed look sane, but if you're re-running this notebook, watch this cell — it's evidently memory- or resource-intensive at multi-collector scale and may need a machine with more RAM or a smaller `COLLECTORS` list (e.g. just `["rrc06"]` for a quick, low-memory test run).

## 7. Pass 2 — accumulate transit counts per AS

This is the main loop: iterate over the aggregated, deduplicated route set again, and for each route, credit every AS strictly between the first hop (peer) and last hop (origin) as a transit hop. Rules applied per route:

- **Prepending is collapsed** — an AS repeated consecutively in the path (a traffic-engineering trick) counts as one hop, not several.
- **Routes with an AS-set (`{...}`) are skipped** — these come from route aggregation and leave the actual AS sequence ambiguous. They're rare (well under 0.1% of routes).
- The **first and last ASes are endpoints, not transit** — they never get transit credit from their own routes.
- Every AS is credited **at most once per route**, even if the path loops.
- Every usable route (even ones with zero transit hops) still counts in the denominator.

Two accumulators are built: `transit_u` (plain path counts) and `transit_w` (address-weighted mass).

**Performance trick — freezing the garbage collector.** By this point, the process holds millions of long-lived Python objects (the trie, the weight dictionaries). Without intervention, every allocation inside this hot loop can trigger a full GC pass that re-scans all of them — the notebook measured an **~80× slowdown** from this. Calling `gc.freeze()` moves the existing heap out of the collector's scope entirely, then `gc.disable()` turns off collection for the duration of the loop (since the dedup table being built during the loop can't be covered by `freeze()`). This is safe here because nothing in the loop creates reference cycles, so skipping cycle detection costs nothing correctness-wise.

## 8. Normalize and rank

Divides each AS's accumulated counts by the totals to get the two `BC` scores, then enriches with AS names/countries pulled from RIPE's public `asn.txt`, and builds a ranked `pandas` DataFrame with both `rank_w` (by weighted score) and `rank_u` (by unweighted score) so you can compare rankings side by side. The `paths` and `addresses` columns are the raw numerators behind each score.

## 9. Visualizations

**CCDF plot** — for each centrality value $x$, how many transit ASes have $BC \geq x$, on log-log axes for both the weighted and unweighted metrics. Expect a heavy tail: most transit ASes carry a tiny sliver of paths/address-space, while a handful of large networks dominate.

**Scatter plot** — one point per transit AS, unweighted score (x-axis) vs. weighted score (y-axis), both log-scaled, with a diagonal reference line:

- **On the diagonal** — the AS transits an address-typical mix of prefixes.
- **Above the diagonal** — the AS carries disproportionately large prefixes (e.g. legacy `/8`s, big cloud/telco aggregates) — the weighted metric ranks it higher than raw path counting would.
- **Below the diagonal** — the AS mostly carries small, heavily deaggregated `/24`-style prefixes — path counting *overstates* how much address space actually depends on it.

## 10. Interpretation and caveats (from the notebook's closing section)

- **Vantage-point bias** — only paths visible to the chosen collectors' peers are counted, so topologically nearby ASes are over-represented (e.g. a `rrc06`-only run over-ranks Japanese carriers). Merging collectors narrows this bias but doesn't eliminate it, since RIS peers skew European and toward networks willing to peer with a collector at all.
- **Distinct paths, not path samples** — deduplicating by (prefix, AS path) means a route seen by 200 peers scores the same as one seen by a single peer. This is a deliberate simplification relative to the original paper's formulation.
- **Peers are structurally under-counted** — a collector's own peer AS is always an endpoint of its routes, never a transit hop, so it can never earn transit credit there.
- **Control-plane, not traffic** — the weighting reflects *potential* address-space reach, not actual measured traffic volume, which varies enormously per address.
- **Single time slot** — the source paper's real interest is the *change* in $BC$ between consecutive time slots (to localize disruptive events like outages or hijacks). Re-running this notebook across consecutive snapshots with a fixed `COLLECTORS` list and differencing the results is the natural next step.
- **No bogon filtering** — announcements of reserved/unallocated address space are counted like anything else; a stricter analysis would filter these out first.

## 11. Practical tips for re-running

- Start with a single small collector (`COLLECTORS = ["rrc06"]`) to validate the pipeline end-to-end in a few minutes before scaling up to multi-collector, full-table runs.
- Pass 1 and the weighting step are the most memory/time-intensive stages at multi-collector scale (tens of millions of RIB entries); watch memory usage there given the kernel crash noted above.
- Snapshots are cached in `data/` after first download, so iterating on later cells (weighting, pass 2, plots) doesn't require re-downloading.




