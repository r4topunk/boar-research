#!/usr/bin/env python3
"""LITEREADERS aggregation (0 LLM). Estimator = packs-l2/tools/l2_agg.py load/setstats/paired unchanged (per-item bootstrap of the
ratio-of-sums difference, B 2000, seed 11, paired on queryId). Haiku 5.5-low rows only.
Readers: runs/lr-<k>-r20-<pack>-s42.judgments.haiku55-low.jsonl; reference 4B-ADD = oracle-st/runs/st-<pack>-cut7-oracleadd-s42.judgments.jsonl (Haiku).
Writes aggregates/litereaders.json; prints table + frozen verdict (LITEREADERS-criterion.md)."""
import json, glob
A = "<workspace>/rnd/research/coordinator/arms"; H = f"{A}/litereaders"; R = f"{H}/runs"
src = open(f"{A}/packs-l2/tools/l2_agg.py").read().split("cell = sys.argv[1]")[0]; ns = {"__file__": f"{A}/packs-l2/tools/l2_agg.py"}; exec(src, ns)
load, setstats, paired = ns["load"], ns["setstats"], ns["paired"]
ids = open(f"{H}/random20.ids").read().split(); SIZE = {"q17": 1.107, "lfm": 0.731, "g1": 0.806, "4B": 2.5}
J = {"4B": {}}
for f in glob.glob(f"{A}/oracle-st/runs/st-*-cut7-oracleadd-s42.judgments.jsonl"): J["4B"].update(load(f))
for k in ("q17", "lfm", "g1"):
    J[k] = {}
    for f in glob.glob(f"{R}/lr-{k}-r20-*-s42.judgments.haiku55-low.jsonl"): J[k].update(load(f))
for k, d in J.items(): assert all(i in d for i in ids), (k, [i for i in ids if i not in d])
out = {"criterion_sha256": open(f"{H}/LITEREADERS-criterion.sha256").read().split()[0], "n": len(ids), "stats": {k: setstats(J[k], ids) for k in J},
       "paired": {f"{k}-4B": paired(J[k], J["4B"], ids) for k in ("q17", "lfm", "g1")} | {f"{k}-q17": paired(J[k], J["q17"], ids) for k in ("lfm", "g1")}}
ties = lambda a, b: int(sum(J[a][q]["s"] == J[b][q]["s"] for q in ids))
for c, pr in out["paired"].items(): a, b = c.split("-"); pr["h2h_better_tie_worse"] = [pr["items_better_worse"][0], ties(a, b), pr["items_better_worse"][1]]
G = json.load(open(f"{H}/aggregates/gate-r20.json")); dd = set(G["readers"]["q17"]["device_date_line_only_diff"]); ids18 = [q for q in ids if q not in dd]
out["sensitivity_no_date_diff"] = {"n": len(ids18), "excluded": sorted(dd)} | {f"{k}-4B": paired(J[k], J["4B"], ids18) for k in ("q17", "lfm", "g1")}
REFT = {}
for f in glob.glob(f"{A}/oracle-st/runs/st-*-cut7-oracleadd-s42.traces.jsonl"):
    pq = {json.loads(l)["query"] for l in open(f.replace(".traces.jsonl", ".prompts.jsonl"))}
    for l in open(f): t = json.loads(l); REFT[t["itemId"]] = t["question"] in pq
SPL = {"SE": [q for q in ids if q.startswith("st-qa-")], "topic": [q for q in ids if not q.startswith("st-qa-")], "llm_items": [q for q in ids if REFT[q]]}
out["splits"] = {g: {"n": len(v)} | {c: paired(J[c.split("-")[0]], J[c.split("-")[1]], v) for c in ("q17-4B", "lfm-4B", "g1-4B", "lfm-q17", "g1-q17")} for g, v in SPL.items()}
out["ranking"] = sorted(J, key=lambda k: -out["stats"][k]["raw"])
lever = [k for k in ("lfm", "g1") if SIZE[k] <= 1.2 and out["paired"][f"{k}-q17"]["d_raw"] >= 0.03 and out["paired"][f"{k}-q17"]["d_raw_ci"][0] > 0]
out["verdict"] = {"lever_shaped": lever, "rule": "LEVER-shaped if a reader <= 1.2 GB beats the 1.7B by >= +0.03 raw with CI low > 0 (measurement arm otherwise)",
                  "label": ("LEVER-shaped: " + ",".join(lever)) if lever else "MEASUREMENT (no reader <= 1.2 GB beats the 1.7B by the rule)"}
json.dump(out, open(f"{H}/aggregates/litereaders.json", "w"), indent=1)
for k, s in out["stats"].items(): print(f"{k:4s} raw {s['raw']:.3f} {s['raw_ci']} above_min {s['above_min']:.3f} W/T/L vs gold {s['win_tie_loss']} pos {s['pos_consistency']}")
for c, pr in out["paired"].items(): print(f"{c:8s} d_raw {pr['d_raw']:+.3f} ({pr['d_raw_ci'][0]:+.3f}..{pr['d_raw_ci'][1]:+.3f}) above_min {pr['d_above_min']:+.3f} h2h b/t/w {pr['h2h_better_tie_worse']}")
print("sens n18", {c: (v["d_raw"], v["d_raw_ci"]) for c, v in out["sensitivity_no_date_diff"].items() if c.endswith("4B")})
for g, v in out["splits"].items(): print("split", g, v["n"], {c: (x["d_raw"], x["d_raw_ci"]) for c, x in v.items() if c != "n"})
print("ranking", out["ranking"]); print("VERDICT", out["verdict"]["label"])
