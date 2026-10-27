#!/usr/bin/env python3
"""SHIP15B prep (0 calls): (1) opus/P.ids = the 51 CV5 ids whose P (id, text) has no Opus judge.v1 pool row; (2) stage1/units.jsonl = unique
(id, text) of P and C for DECLINE2STAGE stage 1 (key = id|sha256(text), as cv5_opus_pool.key). python3 -I ship15b_prep.py"""
import json, sys, hashlib
A = "<workspace>/rnd/research/coordinator/arms/"; RU = A + "../ruler/"; S = A + "ship15b/"
sys.path.insert(0, RU + "tools"); import cv5_opus_pool as CP
ids = json.load(open(RU + "cv5-ladder/in/set.json"))["ids"]
TRF = {"C": A + "floor-anchors/traces/floor-anchors-K0-main-sub3e6183-s42.traces.jsonl", "P": A + "ship15b-packs/traces/ship15b-packs-K1-main-sub3e6183-s42.traces.jsonl"}
TR = {k: {(j := json.loads(l))["itemId"]: j for l in open(f)} for k, f in TRF.items()}
P_ = CP.pool("bd235bb9811f6d1ae88ba2d2ae3973e3572d75b6c451ee4cdd3a2e7644db48b1", "568b3ececd8afe5cad63a7f39bffe414e6dd45bcef9d03ef112faecad2981b18", exclude_prefix=S + "opus")
need = [q for q in ids if CP.key(q, TR["P"][q]["answer"]["text"]) not in P_]
open(S + "opus/P.ids", "w").write("\n".join(need) + "\n")
U = {}
for k in ("P", "C"):
    for q in ids:
        t = TR[k][q]["answer"]["text"]; key = CP.key(q, t)
        U.setdefault(key, {"key": key, "set": "SHIP15B-" + k, "id": q, "question": TR[k][q]["question"], "text": t, "text_sha256": hashlib.sha256(t.encode()).hexdigest()})
with open(S + "stage1/units.jsonl", "w") as f:
    for u in U.values(): f.write(json.dumps(u) + "\n")
print(f"opus P ids {len(need)} (reuse {len(ids) - len(need)}); stage1 units {len(U)}; identical P==C texts {sum(TR['P'][q]['answer']['text'] == TR['C'][q]['answer']['text'] for q in ids)}")
