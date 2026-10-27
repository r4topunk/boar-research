#!/usr/bin/env python3
"""HEADPASS-X2b stages 2-3 aggregation (0 LLM). Estimator = packs-l2/tools/l2_agg.py unchanged (per-item bootstrap of the ratio-of-sums
difference, B 2000, seed 11, paired on queryId), as agg_hp.py / l2_agg_headpass.py.
Usage: python3 -I agg_x2b.py            Haiku: gen-x2b/*.judgments.jsonl vs S (packs/selftest-runs/*.judgments.jsonl) -> aggregates/agg-x2b.json
       python3 -I agg_x2b.py --opus     Opus:  gen-x2b/*.judgments.opus.jsonl vs S *.judgments.opus.jsonl -> aggregates/l2-opus-x2b.json
Cells: X2b - S on the 180 (pooled, SE/topic, per pack); declared split from the step-0 replay (runs-x2/split-x2b.jsonl split_vs_S:
newly_present_x2b / present_x1 / nonfact_only / unchanged / other_changed) and the generation-side split (aggregates/gen-split-x2b.json,
precheck_x2b.py); X2b - X1 (gen/st-<pack>-cut7-headpass-s42 judgments, same judge) descriptive; v0.1 + simplewiki ON - OFF (57; Haiku only).
--opus also: Haiku/Opus agreement (same winner, per-item delta r)."""
import json, sys, collections
ARMS = "<workspace>/rnd/research/coordinator/arms"; H = f"{ARMS}/headpass-st"
src = open(f"{ARMS}/packs-l2/tools/l2_agg.py").read().split("cell = sys.argv[1]")[0]
ns = {"__file__": f"{ARMS}/packs-l2/tools/l2_agg.py"}; exec(src, ns)
load, setstats, paired, SE, TOPIC = ns["load"], ns["setstats"], ns["paired"], ns["SE"], ns["TOPIC"]
OPUS = "--opus" in sys.argv; sfx = ".judgments.opus.jsonl" if OPUS else ".judgments.jsonl"
W, N, X, fam = {}, {}, {}, {}; WH, NH = {}, {}
out = {"estimator": "l2_agg.py: per-item bootstrap ratio-of-sums diff, B 2000, seed 11, paired on queryId",
       "judge": "Opus judge.v1 N=4 shards, both orders" if OPUS else "claude-haiku-5-5 effort low, N=4 shards, both orders", "packs": {}}
for p in SE + TOPIC:
    w = load(f"{H}/gen-x2b/st-{p}-cut7-headpassx2b-s42{sfx}"); n = load(f"{ARMS}/packs/selftest-runs/st-{p}-cut7-s42{sfx}")
    x = load(f"{H}/gen/st-{p}-cut7-headpass-s42{sfx}")
    ids = sorted(set(w) & set(n))
    if len(ids) != 20: print(f"WARN {p}: n_paired {len(ids)} != 20 (left out)", file=sys.stderr); continue
    out["packs"][p] = {"X2b": setstats(w, ids), "S": setstats(n, ids), "paired": paired(w, n, ids)}
    xi = sorted(set(ids) & set(x))
    if xi: out["packs"][p]["vsX1"] = paired(w, x, xi)
    for q in ids: W[q], N[q], fam[q] = w[q], n[q], "SE" if p in SE else "topic"
    for q in xi: X[q] = x[q]
    if OPUS:
        wh = load(f"{H}/gen-x2b/st-{p}-cut7-headpassx2b-s42.judgments.jsonl"); nh = load(f"{ARMS}/packs/selftest-runs/st-{p}-cut7-s42.judgments.jsonl")
        for q in ids: WH[q], NH[q] = wh[q], nh[q]
split = {d["id"]: d["split_vs_S"] for d in map(json.loads, open(f"{H}/runs-x2/split-x2b.jsonl"))}
gsplit = json.load(open(f"{H}/aggregates/gen-split-x2b.json"))
groups = {"pooled": sorted(W), "SE": sorted(q for q in W if fam[q] == "SE"), "topic": sorted(q for q in W if fam[q] == "topic")}
for k in ("newly_present_x2b", "present_x1", "nonfact_only", "unchanged", "other_changed"):
    groups[f"split:{k}"] = sorted(q for q in W if split[q] == k); groups[f"gen:{k}"] = sorted(q for q in W if gsplit.get(q) == k)
out["split_counts"] = dict(collections.Counter(split[q] for q in W)); out["gen_split_counts"] = dict(collections.Counter(gsplit.get(q) for q in W))
out["groups"] = {}
for g, ids in groups.items():
    if not ids: continue
    r = {"X2b": setstats(W, ids), "S": setstats(N, ids), "paired": paired(W, N, ids)}
    xi = [q for q in ids if q in X]
    if xi: r["vsX1"] = paired(W, X, xi); r["X1"] = setstats(X, xi)
    out["groups"][g] = r
import os
if not OPUS and os.path.exists(f"{H}/gen-x2b/v01-sw-cut7-x2b-on-s42.judgments.jsonl"):
    on, off = load(f"{H}/gen-x2b/v01-sw-cut7-x2b-on-s42.judgments.jsonl"), load(f"{H}/gen-x2b/v01-sw-cut7-x2b-off-s42.judgments.jsonl")
    vid = sorted(set(on) & set(off))
    if vid:
        fired = set()
        for l in open(f"{H}/gen-x2b/v01-sw-cut7-x2b-on-s42.traces.jsonl"):
            t = json.loads(l)
            if any(c.startswith(("headpass:add:", "headpass:dense:add:")) for c in (t.get("route") or {}).get("reasonCodes") or []): fired.add(t["itemId"])
        out["v01sw"] = {"all": {"ON": setstats(on, vid), "OFF": setstats(off, vid), "paired": paired(on, off, vid)}, "fired_n_gen": len(fired)}
        fv = sorted(fired & set(vid))
        if fv: out["v01sw"]["fired"] = {"ON": setstats(on, fv), "OFF": setstats(off, fv), "paired": paired(on, off, fv)}
if OPUS:
    import numpy as np
    ids = sorted(W)
    do = np.array([W[q]["s"] - N[q]["s"] for q in ids]); dh = np.array([WH[q]["s"] - NH[q]["s"] for q in ids])
    out["agreement"] = {"n": len(ids), "same_winner_X2b": [sum(W[q]["winner"] == WH[q]["winner"] for q in ids), len(ids)],
                        "same_winner_S": [sum(N[q]["winner"] == NH[q]["winner"] for q in ids), len(ids)],
                        "per_item_delta_r": round(float(np.corrcoef(do, dh)[0, 1]), 3), "haiku_pooled_d_raw": paired(WH, NH, ids)["d_raw"]}
json.dump(out, open(f"{H}/aggregates/{'l2-opus-x2b' if OPUS else 'agg-x2b'}.json", "w"), indent=1)
f = lambda pr: f"n={pr['n']:3d} d_raw {pr['d_raw']:+.3f} ({pr['d_raw_ci'][0]:+.3f}..{pr['d_raw_ci'][1]:+.3f}) b/w {pr['items_better_worse'][0]}/{pr['items_better_worse'][1]}"
for g, r in out["groups"].items():
    print(f"{g:24s} X2b {r['X2b']['raw']:.3f} S {r['S']['raw']:.3f} {f(r['paired'])}" + (f" | vs X1 {f(r['vsX1'])}" if "vsX1" in r else ""))
for p, r in out["packs"].items(): print(f"pack {p:20s} X2b {r['X2b']['raw']:.3f} S {r['S']['raw']:.3f} {f(r['paired'])}" + (f" | vs X1 {f(r['vsX1'])}" if "vsX1" in r else ""))
for g, r in (out.get("v01sw") or {}).items():
    if isinstance(r, dict): print(f"v01sw {g:6s} ON {r['ON']['raw']:.3f} OFF {r['OFF']['raw']:.3f} {f(r['paired'])}")
if OPUS: print("agreement", json.dumps(out["agreement"]))
