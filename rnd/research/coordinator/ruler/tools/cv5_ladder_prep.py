#!/usr/bin/env python3
"""CV5-LADDER-OPUS prep (0 calls). python3 -I cv5_ladder_prep.py -> ../cv5-ladder/in/{set.json,<rung>.ids}
Units = unique (item, answer text) over the four single-seed rung traces on the RV2 primary 51 ids. Existing Opus judge.v1 rows of the identical
unit and frame (v0.1 refs/questions sha, seed 7, both orders) are reused (0 calls). New units are judged on the first rung trace carrying them
(order L3, L1, L2, L0)."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import cv5_opus_pool as CP
A = "<workspace>/rnd/research/coordinator/arms/"; R = "<workspace>/boar-eval/runs/"; OUT = A + "../ruler/cv5-ladder/in/"
RUNGS = {"L3_4B_phone_cut7": R + "device-pixel8a/final-cut7-v01/traces.jsonl",
         "L1_17B_K0_s42": A + "lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl",
         "L2_GemmaE2B_desk_s42": A + "gemma4-e2b/stage2/traces/gemma4-e2b-eng-K0-main-s42.traces.jsonl",
         "L0_15B_closedbook": A + "floor-anchors/traces/floor-anchors-K0-main-sub3e6183-s42.traces.jsonl"}
FR, FQ = "bd235bb9811f6d1ae88ba2d2ae3973e3572d75b6c451ee4cdd3a2e7644db48b1", "568b3ececd8afe5cad63a7f39bffe414e6dd45bcef9d03ef112faecad2981b18"
ids57 = open(A + "gemma4-e2b/phone/judge/v01-57.ids").read().split()
det6 = json.load(open(A + "floor-anchors/aggregates/floor.json"))["nonmodel_path_items"]
ids = [q for q in ids57 if q not in det6]; assert len(ids) == 51
def tr(p): return {(j := json.loads(l)).get("itemId") or j.get("queryId"): j for l in open(p)}
T = {k: tr(p) for k, p in RUNGS.items()}
for k in T:
    for q in ids: assert q in T[k] and not T[k][q].get("error"), (k, q)
P = CP.pool(FR, FQ, exclude_prefix=A + "../ruler/cv5-ladder/")
units = {}
for k in RUNGS:
    for q in ids:
        u = units.setdefault(CP.key(q, T[k][q]["answer"]["text"]), {"id": q, "rungs": [], "judge_on": k})
        u["rungs"].append(k)
for uk, u in units.items():
    u["reuse"] = P[uk]["src"] if uk in P else None
files = {k: [u["id"] for u in units.values() if u["judge_on"] == k and not u["reuse"]] for k in RUNGS}
for k, v in files.items():
    assert len(v) == len(set(v)); open(OUT + f"{k}.ids", "w").write("".join(i + "\n" for i in v))
new = sum(len(v) for v in files.values())
doc = dict(rungs=RUNGS, ids=ids, units=units, n_units=len(units), reused=sum(1 for u in units.values() if u["reuse"]), new_units=new, planned_calls=2 * new,
           files={k: len(v) for k, v in files.items()})
json.dump(doc, open(OUT + "set.json", "w"), indent=1)
print(json.dumps({k: doc[k] for k in ("n_units", "reused", "new_units", "planned_calls", "files")}))
