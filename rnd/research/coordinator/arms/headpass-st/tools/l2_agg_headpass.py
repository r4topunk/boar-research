#!/usr/bin/env python3
"""HEADPASS-ST Opus L2 aggregation (0 LLM): ON Opus rows (gen/*.judgments.opus.jsonl) vs S Opus rows (packs/selftest-runs/st-<pack>-cut7-s42.judgments.opus.jsonl); also Haiku-vs-Opus agreement. Derived from agg_hp.py (Haiku). Estimator = packs-l2/tools/l2_agg.py unchanged
(load/ratios/boot/setstats/paired: per-item bootstrap of the ratio-of-sums difference, B 2000, seed 11, paired on queryId).
Cells: X1 (gen/st-<pack>-cut7-headpass-s42.judgments.jsonl) - S (packs/selftest-runs/st-<pack>-cut7-s42.judgments.jsonl) on the 180:
pooled, SE/topic, per pack, and the declared split from the step-0 replay (runs/split.jsonl: newly_present / nonfact_only / unchanged /
other_changed). No-harm: v0.1 + boar-simplewiki-en ON - OFF (57). Writes aggregates/agg.json. Usage: python3 -I agg_hp.py"""
import json, os, sys, collections, importlib.util, io, contextlib
ARMS = "<workspace>/rnd/research/coordinator/arms"; H = f"{ARMS}/headpass-st"
src = open(f"{ARMS}/packs-l2/tools/l2_agg.py").read().split("cell = sys.argv[1]")[0]  # estimator functions only
ns = {"__file__": f"{ARMS}/packs-l2/tools/l2_agg.py"}; exec(src, ns)
load, setstats, paired, SE, TOPIC = ns["load"], ns["setstats"], ns["paired"], ns["SE"], ns["TOPIC"]

import numpy as np
W, N, fam, pk, WH, NH = {}, {}, {}, {}, {}, {}
out = {"estimator": "l2_agg.py: per-item bootstrap ratio-of-sums diff, B 2000, seed 11, paired on queryId", "judge": "Opus judge.v1 N=4 shards, both orders", "packs": {}}
for p in SE + TOPIC:
    w = load(f"{H}/gen/st-{p}-cut7-headpass-s42.judgments.opus.jsonl"); n = load(f"{ARMS}/packs/selftest-runs/st-{p}-cut7-s42.judgments.opus.jsonl")
    wh = load(f"{H}/gen/st-{p}-cut7-headpass-s42.judgments.jsonl"); nh = load(f"{ARMS}/packs/selftest-runs/st-{p}-cut7-s42.judgments.jsonl")
    ids = sorted(set(w) & set(n))
    if len(ids) != 20: print(f"WARN {p}: n_paired {len(ids)} != 20 (left out)", file=sys.stderr); continue
    out["packs"][p] = {"ON": setstats(w, ids), "S": setstats(n, ids), "paired": paired(w, n, ids)}
    for q in ids: W[q], N[q], fam[q], pk[q], WH[q], NH[q] = w[q], n[q], "SE" if p in SE else "topic", p, wh[q], nh[q]
split = {d["id"]: d["split"] for d in map(json.loads, open(f"{H}/runs/split.jsonl"))}
groups = {"pooled": sorted(W), "SE": sorted(q for q in W if fam[q] == "SE"), "topic": sorted(q for q in W if fam[q] == "topic")}
for k in ("newly_present", "nonfact_only", "unchanged", "other_changed"): groups[f"split:{k}"] = sorted(q for q in W if split[q] == k)
groups["split:changed_all"] = sorted(q for q in W if split[q] != "unchanged")
out["groups"] = {g: {"ON": setstats(W, ids), "S": setstats(N, ids), "paired": paired(W, N, ids)} for g, ids in groups.items() if ids}
ids = sorted(W)
same_on = sum(W[q]["winner"] == WH[q]["winner"] for q in ids); same_s = sum(N[q]["winner"] == NH[q]["winner"] for q in ids)
do = np.array([W[q]["s"] - N[q]["s"] for q in ids]); dh = np.array([WH[q]["s"] - NH[q]["s"] for q in ids])
out["agreement"] = {"n": len(ids), "same_winner_ON": [same_on, len(ids)], "same_winner_S": [same_s, len(ids)], "per_item_delta_r": round(float(np.corrcoef(do, dh)[0, 1]), 3),
    "haiku_pooled_d_raw": paired(WH, NH, ids)["d_raw"]}
json.dump(out, open(f"{H}/aggregates/l2-opus.json", "w"), indent=1)
f = lambda r: f"n={r['paired']['n']:3d} d_raw {r['paired']['d_raw']:+.3f} ({r['paired']['d_raw_ci'][0]:+.3f}..{r['paired']['d_raw_ci'][1]:+.3f}) d_above_min {r['paired']['d_above_min']:+.3f} ({r['paired']['d_above_min_ci'][0]:+.3f}..{r['paired']['d_above_min_ci'][1]:+.3f}) b/w {r['paired']['items_better_worse'][0]}/{r['paired']['items_better_worse'][1]}"
for g, r in out["groups"].items(): print(f"{g:22s} ON {r['ON']['raw']:.3f} S {r['S']['raw']:.3f} W/T/L {r['ON']['win_tie_loss']} vs {r['S']['win_tie_loss']} {f(r)}")
for p, r in out["packs"].items(): print(f"pack {p:20s} ON {r['ON']['raw']:.3f} S {r['S']['raw']:.3f} {f(r)}")
print("agreement", json.dumps(out["agreement"]))
