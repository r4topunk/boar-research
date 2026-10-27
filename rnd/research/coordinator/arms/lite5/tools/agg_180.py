#!/usr/bin/env python3
"""LITE5-180 stage 4-5 aggregation (0 LLM). Estimator = packs-l2/tools/l2_agg.py (load/setstats/paired unchanged: per-item bootstrap of the
ratio-of-sums difference, B 2000, seed 11, paired on queryId), as in headpass-st/tools/agg_x2b.py. Haiku 5.5-low rows only.
Arms: ON (1.7B X2b) and OFF (1.7B plain) = runs/180; C4B = 4B plain (packs/selftest-runs); X4B = 4B X2b (headpass-st/gen-x2b).
Writes aggregates/lite5-180.json; prints the table + frozen verdict (LITE5-180-criterion.md)."""
import json, collections
A = "<workspace>/rnd/research/coordinator/arms"; H = f"{A}/lite5"; R = f"{H}/runs/180"
src = open(f"{A}/packs-l2/tools/l2_agg.py").read().split("cell = sys.argv[1]")[0]; ns = {"__file__": f"{A}/packs-l2/tools/l2_agg.py"}; exec(src, ns)
load, setstats, paired, SE, TOPIC = ns["load"], ns["setstats"], ns["paired"], ns["SE"], ns["TOPIC"]
PATH = {"ON": lambda p: f"{R}/lite5-180-on-{p}-s42.judgments.haiku55-low.jsonl", "OFF": lambda p: f"{R}/lite5-180-off-{p}-s42.judgments.haiku55-low.jsonl",
        "C4B": lambda p: f"{A}/packs/selftest-runs/st-{p}-cut7-s42.judgments.jsonl", "X4B": lambda p: f"{A}/headpass-st/gen-x2b/st-{p}-cut7-headpassx2b-s42.judgments.jsonl"}
J = {k: {} for k in PATH}; fam = {}; pk = {}
for p in SE + TOPIC:
    d = {k: load(f(p)) for k, f in PATH.items()}; ids = set.intersection(*(set(v) for v in d.values()))
    assert len(ids) == 20, (p, {k: len(v) for k, v in d.items()})
    for k in d: J[k].update({q: d[k][q] for q in ids})
    for q in ids: fam[q] = "SE" if p in SE else "topic"; pk[q] = p
F = json.load(open(f"{H}/aggregates/fic-180.json")); ALL = sorted(J["ON"]); assert len(ALL) == 180
groups = {"pooled": ALL, "SE": [q for q in ALL if fam[q] == "SE"], "topic": [q for q in ALL if fam[q] == "topic"]}
for c in ("newly_present", "present_off", "absent"): groups[f"reach:{c}"] = [q for q in ALL if F[q]["reach"] == c]
groups["fic:gained"] = groups["reach:newly_present"]; groups["fic:not_gained"] = [q for q in ALL if F[q]["reach"] != "newly_present"]
groups["fired"] = [q for q in ALL if F[q]["n_appended"] > 0]; groups["not_fired"] = [q for q in ALL if F[q]["n_appended"] == 0]
for p in SE + TOPIC: groups[f"pack:{p}"] = [q for q in ALL if pk[q] == p]
CMP = {"ON-OFF": ("ON", "OFF"), "ON-C4B": ("ON", "C4B"), "ON-X4B": ("ON", "X4B"), "OFF-C4B": ("OFF", "C4B"), "X4B-C4B": ("X4B", "C4B")}
out = {"criterion_sha256": open(f"{H}/LITE5-180-criterion.sha256").read().split()[0], "estimator": "l2_agg.py per-item bootstrap ratio-of-sums diff, B 2000, seed 11, paired on queryId",
       "judge": "claude-haiku-5-5 effort low, N=4 shards, both orders", "groups": {}}
for g, ids in groups.items():
    if not ids: continue
    r = {"n": len(ids), "stats": {k: setstats(J[k], ids) for k in J}}
    r["paired"] = {c: paired(J[a], J[b], ids) for c, (a, b) in CMP.items()} if g in ("pooled", "SE", "topic") else {"ON-OFF": paired(J["ON"], J["OFF"], ids), "X4B-C4B": paired(J["X4B"], J["C4B"], ids)}
    out["groups"][g] = r
po = out["groups"]["pooled"]["paired"]["ON-OFF"]; d, lo = po["d_raw"], po["d_raw_ci"][0]
out["verdict"] = "LEVER (Haiku, dev 180)" if d >= 0.03 and lo > 0 else "SMALL (Haiku, dev 180)" if lo > 0 else "NO (Haiku, dev 180)"
json.dump(out, open(f"{H}/aggregates/lite5-180.json", "w"), indent=1)
f = lambda pr: f"{pr['d_raw']:+.3f} ({pr['d_raw_ci'][0]:+.3f}..{pr['d_raw_ci'][1]:+.3f}) b/w {pr['items_better_worse'][0]}/{pr['items_better_worse'][1]}"
for g, r in out["groups"].items():
    s = r["stats"]; print(f"{g:28s} n={r['n']:3d} ON {s['ON']['raw']:.3f} OFF {s['OFF']['raw']:.3f} C4B {s['C4B']['raw']:.3f} X4B {s['X4B']['raw']:.3f} | " + " | ".join(f"{c} {f(pr)}" for c, pr in r["paired"].items()))
print("VERDICT", out["verdict"])
