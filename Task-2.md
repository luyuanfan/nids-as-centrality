# Task 2 Guidance: AS Hegemony

This page provides explanation for Task 2

## Filtering BGP route collector peers

We are filterting BGP collector peers down to "full-feed" viewpoints. Using the per-peer announcement from an earlier pass. In this case we are using only peers that announce at least 75% of IPv4 prefixes. This could allow for overcounting, but this will be corrected in a future cell.

```python
ALPHA = 0.1                # fraction of viewpoints trimmed at each end (paper's value)
FULL_FEED_FRACTION = 0.75  # a viewpoint must carry >= this fraction of all announced IPv4 prefixes

vp_threshold = FULL_FEED_FRACTION * len(norm_weight)

# peer_counts (from pass 1) sums announcements across collectors, so a peer
# feeding two collectors is counted about twice here. That only overshoots,
# never undershoots: no genuine full feed is lost at this stage, and impostors
# are re-checked against their deduplicated route count after pass 3.
vp_meta = sorted(k for k, c in peer_counts.items() if c >= vp_threshold)
vp_index = {peer_ip: j for j, (peer_ip, _) in enumerate(vp_meta)}
m = len(vp_meta)

print(f"{m} candidate full-feed viewpoints "
      f"(>= {vp_threshold:,.0f} of {len(norm_weight):,} IPv4 prefixes) "
      f"in {len({asn for _, asn in vp_meta})} peer ASes, "
      f"out of {len(peer_counts)} peers total")
```

---

## Pass over RIB dumps

Here we are tallying per-viewpoint and per-AS statistics needed to compute the AS Hegemony. Each route is deduplicated, unusable entries are skipped, and address-weighted mass and toure counts per viewpoint (vp_total_w / vp_total_u).

```Python
gc.collect()
gc.freeze()
gc.disable()   # the accumulators (and dedup table) are built inside the loop

t0 = time.time()
zero_row = array("q", [0]) * m
hege_acc = {}                      # AS -> (address mass per viewpoint, path count per viewpoint)
vp_total_w = array("q", zero_row)  # denominator per viewpoint: address mass
vp_total_u = array("q", zero_row)  # denominator per viewpoint: usable routes
# Within one RIB dump each (peer, prefix) already appears exactly once; the
# dedup table is only needed when collectors are merged and a peer feeds several.
seen = (SeenKeys(sum(c for (ip, _), c in peer_counts.items() if ip in vp_index))
        if len(RIB_PATHS) > 1 else None)
n_used = 0
for elem in iter_routes(RIB_PATHS, dedup=False, progress_every=0):
    j = vp_index.get(elem.peer_ip)
    if j is None:  # not a full-feed candidate
        continue
    if seen is not None and not seen.add(hash((elem.peer_ip, elem.prefix))):
        continue
    w = weights.get(elem.prefix)
    if w is None:  # IPv6, default route, or unparseable prefix
        continue
    path_str = elem.as_path
    if path_str is None or "{" in path_str:  # missing path or AS-set: skip
        continue
    n_used += 1
    if n_used % 5_000_000 == 0:
        print(f"  {n_used:,} viewpoint routes...")
    vp_total_w[j] += w
    vp_total_u[j] += 1
    for asn in set(path_str.split()):  # a set collapses prepending on its own
        acc = hege_acc.get(asn)
        if acc is None:
            acc = hege_acc[asn] = (array("q", zero_row), array("q", zero_row))
        acc[0][j] += w
        acc[1][j] += 1

gc.enable()
gc.unfreeze()
print(f"{n_used:,} routes from {m} candidate viewpoints, "
      f"{len(hege_acc):,} ASes on-path ({time.time() - t0:.0f}s)")
```

---

## AS Hegemony

Here we re-confirm the candidtae viewpoints that are true full-feeds after the deduplication. After this we compute the hegemony score for each AS as a trimmed mean of the per-viewpoint visibility fraction. We discard the top/bottom $\alpha$ fraction viewpoints per AS to exclude outliers. We also remove ASes with a score of zero. Then we create a DataFrame to create a human readable output for the top 25 ASes.

```Python
full = [j for j in range(m) if vp_total_u[j] >= vp_threshold]
n_vp = len(full)
if n_vp == 0:
    raise RuntimeError("no full-feed viewpoints — lower FULL_FEED_FRACTION or add collectors")
k = int(ALPHA * n_vp)
print(f"{n_vp} of {m} candidate viewpoints confirmed full-feed after dedup; "
      f"trimming {k} viewpoint(s) at each end (alpha={ALPHA})")
if n_vp < 20:
    print("WARNING: hegemony is unstable below ~20 viewpoints (paper, Fig. 1b)")

t0 = time.time()
totw = [vp_total_w[j] for j in full]
totu = [vp_total_u[j] for j in full]

hege_rows = []
for asn_s, (aw, au) in hege_acc.items():
    bc_w = sorted(aw[j] / tw for j, tw in zip(full, totw))
    bc_u = sorted(au[j] / tu for j, tu in zip(full, totu))
    hw = sum(bc_w[k:n_vp - k]) / (n_vp - 2 * k)
    hu = sum(bc_u[k:n_vp - k]) / (n_vp - 2 * k)
    if hw == 0 and hu == 0:  # visible only through trimmed viewpoints
        continue
    asn = int(asn_s)
    name, country = asn_info.get(asn, ("", ""))
    hege_rows.append({
        "asn": asn,
        "name": name[:48],
        "country": country,
        "hegemony_w": hw,
        "hegemony_u": hu,
        "viewpoints": sum(1 for x in bc_u if x > 0),
    })

hege_df = (pd.DataFrame(hege_rows)
             .sort_values("hegemony_w", ascending=False)
             .reset_index(drop=True))
hege_df.insert(0, "rank_w", hege_df.index + 1)
print(f"{len(hege_df):,} ASes scored ({time.time() - t0:.0f}s)")

hege_df.head(25).style.format({
    "hegemony_w": "{:.4f}",
    "hegemony_u": "{:.4f}",
}).hide(axis="index")
```

---

## Plotting

Here we make a log-log plot comparing the two centrality metrics per AS. The diagonal line across the middle would be perfectly followed if the two metrics agreed perfectly.

```python
both = df.merge(hege_df, on="asn", suffixes=("_bc", "_hege"))
pos = both[(both["bc_weighted"] > 0) & (both["hegemony_w"] > 0)]

fig, ax = plt.subplots(figsize=(6.5, 6))
fig.patch.set_facecolor(SURFACE)
style_axes(ax)

lo = max(min(pos["bc_weighted"].min(), pos["hegemony_w"].min()), 1e-9)
hi = max(pos["bc_weighted"].max(), pos["hegemony_w"].max()) * 2
ax.plot([lo, hi], [lo, hi], color=MUTED, linewidth=1, linestyle="--", zorder=1)
ax.annotate("equal under both metrics", xy=(hi, hi),
            xytext=(-8, -14), textcoords="offset points",
            ha="right", fontsize=8, color=MUTED)

ax.scatter(pos["bc_weighted"], pos["hegemony_w"],
           s=14, color=BLUE, alpha=0.45, linewidths=0, zorder=2)

for _, row in pos.nlargest(8, "hegemony_w").iterrows():
    ax.annotate(f"AS{row['asn']}", xy=(row["bc_weighted"], row["hegemony_w"]),
                xytext=(5, 3), textcoords="offset points",
                fontsize=8, color=INK2)

ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(lo, hi)
ax.set_ylim(lo, hi)
ax.set_xlabel("Pooled betweenness centrality (address-weighted)", color=INK2)
ax.set_ylabel("AS hegemony (address-weighted)", color=INK2)
ax.set_title(f"AS hegemony vs. pooled BC ({LABEL}, {SNAPSHOT_DATE})", color=INK)
fig.tight_layout()
plt.show()
```