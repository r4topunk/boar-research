#!/usr/bin/env python3
"""Opus slice aggregate (0 calls). python3 -I opus_agg.py -> b/opus/opus-slice.json. Rows: existing Opus judge.v1 pool (id|sha256 text) + b/opus/{C,X}.judgments.jsonl. U = ratio of sums (declined -> 0); bootstrap items B 2000 Random(11)."""
import json, sys, random, glob
A = "<workspace>/rnd/research/coordinator"; B = A + "/arms/night-1023/b"
sys.path.insert(0, A + "/ruler/tools"); import cv5_opus_pool as CP
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
plan = json.load(open(B + "/opus/plan.json")); sl = plan["slice"]
X = {t["itemId"]: t for t in rd(B + "/traces/b124-main-s42.traces.jsonl")}; C = {}
for f in glob.glob(A + "/arms/litepacks/traces/mini/lp-K1-*-s42.mini.traces.jsonl"): C.update({t["itemId"]: t for t in rd(f)})
P = CP.pool("bd235bb9811f6d1ae88ba2d2ae3973e3572d75b6c451ee4cdd3a2e7644db48b1", "568b3ececd8afe5cad63a7f39bffe414e6dd45bcef9d03ef112faecad2981b18")
new = {}
for arm, D in (("C", C), ("X", X)):
    for r in rd(f"{B}/opus/{arm}.judgments.jsonl"):
        if r.get("ok") is True: new.setdefault(CP.key(r["queryId"], D[r["queryId"]]["answer"]["text"]), {})[r["order"]] = r["mapped"]
dim = lambda m, k: sum(m[k].values()) / 3
def row(D, i):
    k = CP.key(i, D[i]["answer"]["text"]); ms = [P[k]["boarA"], P[k]["boarB"]] if k in P else [new[k]["boarA"], new[k]["boarB"]] if k in new and len(new[k]) == 2 else None
    assert ms, (i, k); return dict(s=sum(dim(m, "boar") for m in ms) / 2, sref=sum(dim(m, "ref") for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2, declined=bool(D[i]["answer"].get("declined")), reused=k in P)
RC = {i: row(C, i) for i in sl}; RX = {i: row(X, i) for i in sl}
U = lambda R, xs: sum(0 if R[i]["declined"] else R[i]["s"] for i in xs) / sum(R[i]["sref"] for i in xs)
def boot(xs, f, Bn=2000):
    r = random.Random(11); v = sorted(f([r.choice(xs) for _ in xs]) for _ in range(Bn)); return [round(v[int(.025 * Bn)], 4), round(v[int(.975 * Bn) - 1], 4)]
dU = lambda xs: dict(n=len(xs), d=round(U(RX, xs) - U(RC, xs), 4), ci=boot(xs, lambda s: U(RX, s) - U(RC, s)), U_ctl=round(U(RC, xs), 4), U_arm=round(U(RX, xs), 4),
                     corr_ctl=round(sum(RC[i]["corr"] for i in xs) / len(xs), 3), corr_arm=round(sum(RX[i]["corr"] for i in xs) / len(xs), 3), CE_ctl=sum(1 for i in xs if not RC[i]["declined"] and RC[i]["corr"] <= 1.5), CE_arm=sum(1 for i in xs if not RX[i]["declined"] and RX[i]["corr"] <= 1.5))
chg = [i for i in sl if C[i]["answer"]["text"] != X[i]["answer"]["text"]]
out = dict(slice_n=len(sl), all=dU(sl), text_differs_only=dU(chg), units_reused=sum(RC[i]["reused"] for i in sl) + sum(RX[i]["reused"] for i in sl), opus_calls=sum(1 for _ in rd(B + "/opus/C.judgments.jsonl")) + sum(1 for _ in rd(B + "/opus/X.judgments.jsonl")), band_ge35=dict(ctl=sum(RC[i]["corr"] >= 3.5 for i in sl), arm=sum(RX[i]["corr"] >= 3.5 for i in sl)))
json.dump(out, open(B + "/opus/opus-slice.json", "w"), indent=1); print(json.dumps(out, indent=1))
