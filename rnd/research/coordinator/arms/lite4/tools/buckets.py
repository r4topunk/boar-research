#!/usr/bin/env python3
# LITE4 per-item / per-bucket ratios (LITE3 estimator: sum boar / sum ref over 3 dims x both orders). Numbers and ids only.
# Usage: buckets.py <on.judgments> <off.judgments> <c4b.judgments> <ids> <gate-ids.json> <out.json>
import json, sys, random, statistics as st
on, off, c4, idsf, gf, out = sys.argv[1:7]
ids = [l.strip() for l in open(idsf) if l.strip()]; G = json.load(open("<workspace>/rnd/research/coordinator/arms/lite3/aggregates/lite3.json"))
inv = set(G["slices"]["kit"]["buckets_L"]["table"]["invented"]["ids_below_4B"]); hs = set(G["slices"]["kit"]["health_safety_ids"])
def ratios(p):
    acc = {}
    for l in open(p):
        r = json.loads(l)
        if not r.get("ok") or r["queryId"] not in ids: continue
        b, f = acc.setdefault(r["queryId"], [0, 0, 0]), r["mapped"]
        b[0] += sum(f["boar"].values()); b[1] += sum(f["ref"].values()); b[2] += 1
    assert all(acc.get(i, [0, 0, 0])[2] == 2 for i in ids), p
    return {i: acc[i][0] / acc[i][1] for i in ids}
A, O, C = ratios(on), ratios(off), ratios(c4)
d = {i: A[i] - O[i] for i in ids}
def ci(sel):
    random.seed(42); x = [d[i] for i in sel]; bs = sorted(st.mean(random.choices(x, k=len(x))) for _ in range(2000)); return [round(bs[50], 4), round(bs[1949], 4)]
grp = {"all": ids, "invented": [i for i in ids if i in inv], "other": [i for i in ids if i not in inv], "other_core": [i for i in ids if i not in inv and i not in hs], "health_safety": [i for i in ids if i in hs]}
res = {g: {"n": len(s), "on": round(st.mean(A[i] for i in s), 4), "off": round(st.mean(O[i] for i in s), 4), "c4b": round(st.mean(C[i] for i in s), 4),
           "d_on_off": round(st.mean(d[i] for i in s), 4), "ci_item_mean": ci(s), "up/same/down": [sum(d[i] > 1e-9 for i in s), sum(abs(d[i]) <= 1e-9 for i in s), sum(d[i] < -1e-9 for i in s)]} for g, s in grp.items()}
order = sorted(ids, key=lambda i: d[i])
res["worst3"] = [[i, round(d[i], 3)] for i in order[:3]]; res["best3"] = [[i, round(d[i], 3)] for i in order[::-1][:3]]
res["perItem"] = {i: {"on": round(A[i], 3), "off": round(O[i], 3), "c4b": round(C[i], 3), "bucket": "invented" if i in inv else ("health_safety" if i in hs else "other")} for i in ids}
json.dump(res, open(out, "w"), indent=1)
for g in grp: print(g, res[g])
print("worst3", res["worst3"], "best3", res["best3"])
