#!/usr/bin/env python3
"""TK2FIX-L1 aggregation (0 LLM). Estimator = packs-l2/tools/l2_agg.py load/setstats/paired unchanged (per-item bootstrap of the ratio-of-sums
difference, B 2000, seed 11, paired on queryId). ON = l1/runs Haiku rows; OFF = packs/selftest-runs/st-<pack>-cut7-s42.judgments.jsonl (SELFTEST-SCORES Haiku rows).
Groups: pooled, SE, topic, per pack, fact-kept-gained (9) vs rest (171), kept-diff vs kept-same (gate.json). Writes aggregates/tk2fix-l1.json; prints table + frozen verdict."""
import json
A = "<workspace>/rnd/research/coordinator/arms"; H = f"{A}/tk2fix"; R = f"{H}/l1/runs"
src = open(f"{A}/packs-l2/tools/l2_agg.py").read().split("cell = sys.argv[1]")[0]; ns = {"__file__": f"{A}/packs-l2/tools/l2_agg.py"}; exec(src, ns)
load, setstats, paired, SE, TOPIC = ns["load"], ns["setstats"], ns["paired"], ns["SE"], ns["TOPIC"]
ON, OFF, pk = {}, {}, {}
for p in SE + TOPIC:
    a, b = load(f"{R}/tk2fix-l1-{p}-s42.judgments.haiku55-low.jsonl"), load(f"{A}/packs/selftest-runs/st-{p}-cut7-s42.judgments.jsonl")
    ids = set(a) & set(b); assert len(ids) == 20, (p, len(a), len(b))
    for q in ids: ON[q] = a[q]; OFF[q] = b[q]; pk[q] = p
ALL = sorted(ON); assert len(ALL) == 180
SP = json.load(open(f"{H}/l1/splits.json")); G = json.load(open(f"{H}/l1/gate.json")); gain = set(SP["fact_gained"]); kd = set(G["kept_diff_ids"])
groups = {"pooled": ALL, "SE": [q for q in ALL if pk[q] in SE], "topic": [q for q in ALL if pk[q] in TOPIC],
          "fact_gained": [q for q in ALL if q in gain], "rest": [q for q in ALL if q not in gain],
          "kept_diff": [q for q in ALL if q in kd], "kept_same": [q for q in ALL if q not in kd]}
for p in SE + TOPIC: groups[f"pack:{p}"] = [q for q in ALL if pk[q] == p]
out = {"criterion_sha256": open(f"{H}/TK2FIX-L1-criterion.md.sha256").read().split()[0], "estimator": "l2_agg.py per-item bootstrap ratio-of-sums diff, B 2000, seed 11, paired on queryId",
       "judge": "claude-haiku-5-5 effort low, N=4 shards, both orders; OFF rows reused from SELFTEST-SCORES", "groups": {}}
for g, ids in groups.items():
    if not ids: continue
    h2h = [sum(ON[q]["s"] > OFF[q]["s"] for q in ids), sum(ON[q]["s"] == OFF[q]["s"] for q in ids), sum(ON[q]["s"] < OFF[q]["s"] for q in ids)]
    out["groups"][g] = {"n": len(ids), "ON": setstats(ON, ids), "OFF": setstats(OFF, ids), "paired": paired(ON, OFF, ids), "h2h_better_tie_worse": h2h}
po = out["groups"]["pooled"]["paired"]; d, lo, hi = po["d_raw"], po["d_raw_ci"][0], po["d_raw_ci"][1]
out["verdict"] = "LEVER (Haiku, dev 180)" if d >= 0.03 and lo > 0 else "SMALL (Haiku, dev 180)" if lo > 0 else "NO (Haiku, dev 180)"
k = out["groups"]["kept_diff"]["paired"]["d_raw_ci"][1] if "kept_diff" in out["groups"] else 1
out["harm_flag"] = bool(hi < 0 or k < 0); out["latency_p50"] = G["latency_p50"]
json.dump(out, open(f"{H}/aggregates/tk2fix-l1.json", "w"), indent=1)
for g, r in out["groups"].items():
    pr = r["paired"]; print(f"{g:28s} n={r['n']:3d} ON {r['ON']['raw']:.3f} OFF {r['OFF']['raw']:.3f} d {pr['d_raw']:+.3f} ({pr['d_raw_ci'][0]:+.3f}..{pr['d_raw_ci'][1]:+.3f}) am {pr['d_above_min']:+.3f} ({pr['d_above_min_ci'][0]:+.3f}..{pr['d_above_min_ci'][1]:+.3f}) h2h {r['h2h_better_tie_worse']} wtl ON {r['ON']['win_tie_loss']} OFF {r['OFF']['win_tie_loss']}")
print("VERDICT", out["verdict"], "harm_flag", out["harm_flag"])
