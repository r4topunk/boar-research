#!/usr/bin/env python3
"""Opus slice plan (0 calls). python3 -I opus_plan.py -> b/opus/plan.json, b/opus/{C,X}.ids
Slice = CV5 51 (ruler/cv5-ladder/in/set.json) intersect delivered (chunk-level, adopted-kit replay flag). Units = (id, seed-42 text) for the control and for the arm, deduplicated by (id, sha256 text).
Existing Opus judge.v1 rows (frame refs bd235bb9.. / questions 568b3ece.., seed 7) are reused by (id, sha256(text)) via ruler/tools/cv5_opus_pool.
Cap 60 calls = 30 units x 2 orders. Outcome-blind priority when over the cap: items whose arm text differs from the control first (both units), then identical-text items, each by CV5 order; whole items only."""
import json, sys, hashlib, os
A = "<workspace>/rnd/research/coordinator"; B = A + "/arms/night-1023/b"; SF = A + "/arms/coverage-map/sefix"
sys.path.insert(0, A + "/ruler/tools"); import cv5_opus_pool as CP
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ids = json.load(open(A + "/ruler/cv5-ladder/in/set.json"))["ids"]
CLF = json.load(open(SF + "/chunklevel-124.json"))["per_item"]["sefix F1F2F4"]
sl = [i for i in ids if CLF.get(i) and CLF[i]["chunk"]]
X = {t["itemId"]: t for t in rd(B + "/traces/b124-main-s42.traces.jsonl")}
C = {}
import glob
for f in glob.glob(A + "/arms/litepacks/traces/mini/lp-K1-*-s42.mini.traces.jsonl"): C.update({t["itemId"]: t for t in rd(f)})
pool42 = json.load(open(A + "/arms/null-cal/control/pool-K1.json"))["items"]
P = CP.pool("bd235bb9811f6d1ae88ba2d2ae3973e3572d75b6c451ee4cdd3a2e7644db48b1", "568b3ececd8afe5cad63a7f39bffe414e6dd45bcef9d03ef112faecad2981b18")
key = CP.key
notes = {i: "pool-K1 text differs from the mini K1 trace; the trace text is judged/used" for i in sl if pool42[i]["text"] != C[i]["answer"]["text"]}
unit = {}   # key -> dict(id, arm(s), have)
for i in sl:
    for arm, D in (("C", C), ("X", X)):
        k = key(i, D[i]["answer"]["text"]); u = unit.setdefault(k, dict(id=i, arms=[], have=k in P, src=P[k]["src"] if k in P else None)); u["arms"].append(arm)
diff = [i for i in sl if X[i]["answer"]["text"] != C[i]["answer"]["text"]]; same = [i for i in sl if i not in diff]
order = diff + same; need = []
for i in order:
    ks = {key(i, D[i]["answer"]["text"]) for D in (C, X)}; nk = [k for k in ks if not unit[k]["have"]]
    if 2 * (len(need) + len(nk)) <= 60: need += nk
    else: print("OVER CAP, item left unjudged:", i)
judged = {k for k in need}
left = [i for i in sl if any(not unit[key(i, D[i]["answer"]["text"])]["have"] and key(i, D[i]["answer"]["text"]) not in judged for D in (C, X))]
os.makedirs(B + "/opus", exist_ok=True)
for arm in ("C", "X"):
    D = C if arm == "C" else X
    open(f"{B}/opus/{arm}.ids", "w").write("".join(i + "\n" for i in sl if key(i, D[i]["answer"]["text"]) in judged and not (arm == "C" and key(i, C[i]["answer"]["text"]) == key(i, X[i]["answer"]["text"]))))
plan = dict(slice=sl, n_slice=len(sl), text_differs=diff, n_units=len(unit), reused=sum(u["have"] for u in unit.values()), new_units=len(need), calls=2 * len(need), items_left_unjudged=left, notes=notes)
json.dump(plan, open(B + "/opus/plan.json", "w"), indent=1); print(json.dumps(plan, indent=1))
