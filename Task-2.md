[README](README.md) | [Introduction](Introduction.md) | [Datasets](Datasets.md) | [Tasks](Tasks.md) | [Task 1](Task-1.md) | [Task 2 ⮕ | [Notebook](nids-as-centrality.ipynb)


# Task 2 Guidance: AS Hegemony

This page provides explanation for Task 2

## Pass over RIB dumps

Here we are tallying per-viewpoint and per-AS statistics needed to compute the AS Hegemony. Each route is deduplicated, unusable entries are skipped, and route counts and address-weighted route counts are accumulated per viewpoint (`vp_total_u` and `vp_total_w`).

```py
n_used = 0

routes_per_vp = {}     # map from ASes and VPs to count of routes
addresses_per_vp = {}  # map from ASes and VPs to weighted count of routes
# The following three lines behave like DefaultDicts. They are more
# memory efficient for this particular task
zero_row = array("q", [0]) * num_vps  # initialize everything to 0s
vp_total_u = array("q", zero_row)     # map from VPs to count of routes
vp_total_w = array("q", zero_row)     # map from VPs to weighted count of routes

# Table to ensure each route is considered only once
seen = SeenKeys(sum(c for (ip, _), c in peer_counts.items() if ip in vp_index))

for elem in iter_routes(RIB_PATHS, dedup=False, progress_every=0):
    j = vp_index.get(elem.peer_ip)

    # Filter out VPs that see few routes
    if j is None:
        continue
    # Filter out duplicate routes
    if not seen.add(hash((elem.peer_ip, elem.prefix))):
        continue

    w = weights.get(elem.prefix)

    # Filter out IPv6, default route, or unparseable prefix
    if w is None:
        continue
    path_str = elem.as_path
    # Filter out AS-set or missing path
    if path_str is None or "{" in path_str:
        continue

    n_used += 1
    if n_used % 5_000_000 == 0:
        print(f"  {n_used:,} viewpoint routes...")

    # Accumulate weight towards the denominator of BC_j(v)
    vp_total_u[j] += 1
    vp_total_w[j] += w

    path = []
    prev = None
    for hop in path_str.split():
        if hop != prev:  # collapse prepending
            path.append(hop)
            prev = hop

    for v in path[1:-1]:
        routes_acc = routes_per_vp.get(v)
        addresses_acc = addresses_per_vp.get(v)
        if addresses_acc is None:
            # In this case, routes_acc is also None
            routes_acc = routes_per_vp[v] = array("q", zero_row)
            addresses_acc = addresses_per_vp[v] = array("q", zero_row)

        # Accumulate weight towards the numerator of BC_j(v)
        routes_acc[j] += 1
        addresses_acc[j] += w
```

---

## AS Hegemony

Here we compute the hegemony score for each AS.

To do this, we start by considering a particular AS $v$. For each viewpoint $j$, we compute the betweenness centrality $BC_{(j)}(v)$ as in Task 1, only considering paths seen by $j$.

We discard the top and bottom $\alpha$ proportion of viewpoints to exclude outliers. We then average the per-VP betweenness centralities.

Then we create a `DataFrame` to create a human readable output for the top 25 ASes.

```py
vp_total_w = [vp_total_w[j] for j in valid_vp_indices]

# Find the number (alpha proprtion) of VPs to trim
n_vps_to_trim = math.floor(ALPHA * n_vp)

hege_rows = []
for asn_str, vp_w in addresses_per_vp.items():
    asn = int(asn_str)

    # For each viewpoint, compute the betweenness centrality of this asn
    vp_bc_w = sorted(vp_w[j] / vp_total_w[j] for j in valid_vp_indices)
    # Trim the top and bottom alpha proportion VPs and average
    hegemony = sum(vp_bc_w[n_vps_to_trim:n_vp - n_vps_to_trim]) / (n_vp - 2 * n_vps_to_trim)

    name, country = asn_info.get(asn, ("", ""))
    hege_rows.append({
        "asn": asn,
        "name": name[:48],
        "country": country,
        "hegemony": hegemony,
        "viewpoints": sum(1 for x in vp_bc_w if x > 0),
    })

hege_df = (pd.DataFrame(hege_rows)
             .sort_values("hegemony", ascending=False)
             .reset_index(drop=True))
hege_df.insert(0, "rank_w", hege_df.index + 1)
```

---

## Plotting

Here we make a log-log plot comparing the two centrality metrics per AS. The diagonal line across the middle would be perfectly followed if the two metrics agreed perfectly.

We additionally annotate the most extreme deviation between betweenness centrality and AS hegemony.

```py
both = df.merge(hege_df, on="asn", suffixes=("_bc", "_hege"))
pos = both[(both["bc_weighted"] > 0) & (both["hegemony"] > 0)]

fig, ax = plt.subplots(figsize=(6.5, 6))
fig.patch.set_facecolor(SURFACE)
style_axes(ax)

lo = max(min(pos["bc_weighted"].min(), pos["hegemony"].min()), 1e-9)
hi = max(pos["bc_weighted"].max(), pos["hegemony"].max()) * 2
ax.plot([lo, hi], [lo, hi], color=MUTED, linewidth=1, linestyle="--", zorder=1)
ax.annotate("equal under both metrics", xy=(hi, hi),
            xytext=(-8, -14), textcoords="offset points",
            ha="right", fontsize=8, color=MUTED)

ax.scatter(pos["bc_weighted"], pos["hegemony"],
           s=14, color=BLUE, alpha=0.45, linewidths=0, zorder=2)

asn_outlier = pos.iloc[(pos["bc_weighted"] / pos["hegemony"]).argmax()]
ax.annotate(f"AS{asn_outlier['asn']}", xy=(asn_outlier["bc_weighted"], asn_outlier["hegemony"]),
            xytext=(5, 3), textcoords="offset points",
            fontsize=8, color=INK2)

ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(lo, hi)
ax.set_ylim(lo, hi)
ax.set_xlabel("Weighted betweenness centrality", color=INK2)
ax.set_ylabel("AS hegemony", color=INK2)
ax.set_title(f"AS hegemony vs. Weighted BC ({LABEL}, {SNAPSHOT_DATE})", color=INK)
fig.tight_layout()
plt.show()
```

[README](README.md) | [Introduction](Introduction.md) | [Datasets](Datasets.md) | [Tasks](Tasks.md) | [Task 1](Task-1.md) | [Task 2 ⮕ | [Notebook](nids-as-centrality.ipynb)
