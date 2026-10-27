#!/usr/bin/env python3
"""Diagnostics, no rule (0 calls): (a) STYLE15B addendum 1: Opus vs Haiku S - D on the 11 1.7B ids; (b) context: P (1.5B + K1) vs the CV5 Opus
1.7B K0 rung (L1, same host, kit K0) on the 51, Opus judge.v1. python3 -I ship15b_diag.py <out.json>"""
import json, sys, os, collections, numpy as np
A = "<workspace>/rnd/research/coordinator/arms/"; RU = A + "../ruler/"; S = A + "ship15b/"
sys.path.insert(0, RU + "tools"); import cv5_opus_pool as CP
ids = json.load(open(RU + "cv5-ladder/in/set.json"))["ids"]
K = ("correctness", "completeness", "usefulness"); mr = lambda d: sum(d[k] for k in K) / 3
sr = lambda a, b: {"s": (mr(a["boar"]) + mr(b["boar"])) / 2, "r": (mr(a["ref"]) + mr(b["ref"])) / 2, "corr": (a["boar"]["correctness"] + b["boar"]["correctness"]) / 2}
def load(*ps):
    J = collections.defaultdict(dict)
    for p in ps:
        for l in open(p):
            r = json.loads(l)
            if r.get("ok") and not r.get("floorScored") and r["order"] not in J[r["queryId"]]: J[r["queryId"]][r["order"]] = r["mapped"]
    return {q: sr(v["boarA"], v["boarB"]) for q, v in J.items() if set(v) == {"boarA", "boarB"}}
T = lambda f: {(j := json.loads(l))["itemId"]: j["answer"]["text"] for l in open(f)}
P_ = CP.pool("bd235bb9811f6d1ae88ba2d2ae3973e3572d75b6c451ee4cdd3a2e7644db48b1", "568b3ececd8afe5cad63a7f39bffe414e6dd45bcef9d03ef112faecad2981b18")
po = lambda q, t: sr(P_[CP.key(q, t)]["boarA"], P_[CP.key(q, t)]["boarB"])
U = lambda s, r: (s - 1).sum() / (r - 1).sum()
out = {}
# (a)
d11 = open(S + "opus17/D17.ids").read().split()
S17 = T(A + "lp-screens/control/traces/lpctl-K1-main-s42.traces.jsonl"); D17 = T(A + "style17-detailed/traces/style17-detailed-K1-main-sub3e6183-s42.traces.jsonl")
OD = load(S + "opus17/D17.judgments.jsonl"); OS = {q: po(q, S17[q]) for q in d11}
K1C = load(A + "lp-screens/control/judgments/lpctl-K1-main-s42-v01.judgments.jsonl"); HD = load(A + "style17-detailed/judgments/style17-detailed-K1-main-sub3e6183-s42-v01.judgments.jsonl")
def blk(Sx, Dx):
    s1, r1 = np.array([Sx[q]["s"] for q in d11]), np.array([Sx[q]["r"] for q in d11]); s2, r2 = np.array([Dx[q]["s"] for q in d11]), np.array([Dx[q]["r"] for q in d11])
    return {"U_S": round(U(s1, r1), 4), "U_D": round(U(s2, r2), 4), "dU": round(U(s1, r1) - U(s2, r2), 4), "mean_ds": round(float((s1 - s2).mean()), 3),
            "better_worse": [int((s1 > s2).sum()), int((s1 < s2).sum())], "CE_S": sum(Sx[q]["corr"] <= 1.5 for q in d11), "CE_D": sum(Dx[q]["corr"] <= 1.5 for q in d11),
            "dlog2_words_mean": round(float(np.mean([np.log2(max(1, len(D17[q].split())) / max(1, len(S17[q].split()))) for q in d11])), 2)}
out["a_17B_style_11"] = {"n": len(d11), "opus": blk(OS, OD), "haiku": blk(K1C, HD)}
# (b)
L1 = T(A + "lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl"); PP = T(A + "ship15b-packs/traces/ship15b-packs-K1-main-sub3e6183-s42.traces.jsonl")
a = {q: po(q, PP[q]) for q in ids}; b = {q: po(q, L1[q]) for q in ids}
sa, ra = np.array([a[q]["s"] for q in ids]), np.array([a[q]["r"] for q in ids]); sb, rb = np.array([b[q]["s"] for q in ids]), np.array([b[q]["r"] for q in ids])
rng = np.random.default_rng(11); dr = [rng.integers(0, 51, 51) for _ in range(2000)]
db = [U(sa[i], ra[i]) - U(sb[i], rb[i]) for i in dr]
out["b_P_vs_17B_K0_opus_v1"] = {"U_P": round(U(sa, ra), 4), "U_17B_K0": round(U(sb, rb), 4), "dU": round(U(sa, ra) - U(sb, rb), 4),
    "ci": [round(float(x), 4) for x in np.percentile(db, [2.5, 97.5])], "CE_P": sum(a[q]["corr"] <= 1.5 for q in ids), "CE_17B": sum(b[q]["corr"] <= 1.5 for q in ids)}
js = json.dumps(out, indent=1); open(sys.argv[1], "w").write(js + "\n"); print(js)
