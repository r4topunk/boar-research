#!/usr/bin/env python3
"""CV5-LADDER-OPUS analysis (0 calls). Criterion ../CV5-LADDER-OPUS-criterion.md. python3 -I cv5_ladder.py <out.json>
Opus judge.v1 rows (new: ../cv5-ladder/out/<rung>.judgments.jsonl; reused: rows indexed by cv5_opus_pool, unit list fixed in in/set.json) vs the
Haiku 5.5-low judge.v1 rows RV2 used, same single-seed rungs, RV2 primary 51 ids. U = sum(s-1)/sum(r-1); item-cluster bootstrap B 2000
numpy default_rng(11) (identical to rv2_ladder.py); U_net = (U-0.058)/0.942; Spearman per rung on per-item s."""
import json, sys, os, collections, hashlib, numpy as np
from scipy.stats import spearmanr
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import cv5_opus_pool as CP
A = "<workspace>/rnd/research/coordinator/arms/"; R = "<workspace>/boar-eval/runs/"; W = A + "../ruler/cv5-ladder/"
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
crit = open(A + "../ruler/CV5-LADDER-OPUS-criterion.sha256").read().split()[0]
assert hashlib.sha256(open(A + "../ruler/CV5-LADDER-OPUS-criterion.md", "rb").read()).hexdigest() == crit
S_ = json.load(open(W + "in/set.json")); ids = S_["ids"]; RUNGS = S_["rungs"]
def sr(a, b): return {"s": (mr(a["boar"]) + mr(b["boar"])) / 2, "r": (mr(a["ref"]) + mr(b["ref"])) / 2, "corr": (a["boar"]["correctness"] + b["boar"]["correctness"]) / 2}
# ---- Opus
T = {k: {(j := json.loads(l)).get("itemId") or j.get("queryId"): j["answer"]["text"] for l in open(p)} for k, p in RUNGS.items()}
OP = {}
for k in RUNGS:
    f = W + f"out/{k}.judgments.jsonl"
    if not os.path.exists(f): continue
    by = collections.defaultdict(dict)
    for l in open(f):
        r = json.loads(l)
        if r.get("ok") and not r.get("floorScored"): by[r["queryId"]].setdefault(r["order"], r["mapped"])
    for q, v in by.items():
        if set(v) == {"boarA", "boarB"}: OP[CP.key(q, T[k][q])] = sr(v["boarA"], v["boarB"])
need_reuse = {uk for uk, u in S_["units"].items() if u["reuse"]}
P = CP.pool("bd235bb9811f6d1ae88ba2d2ae3973e3572d75b6c451ee4cdd3a2e7644db48b1", "568b3ececd8afe5cad63a7f39bffe414e6dd45bcef9d03ef112faecad2981b18", exclude_prefix=W)
for uk in need_reuse:
    assert uk in P and P[uk]["src"] == S_["units"][uk]["reuse"], uk
    OP.setdefault(uk, sr(P[uk]["boarA"], P[uk]["boarB"]))
miss = [uk for uk in S_["units"] if uk not in OP]
assert not miss, f"{len(miss)} units without Opus rows"
O = {k: {q: OP[CP.key(q, T[k][q])] for q in ids} for k in RUNGS}
# ---- Haiku (rv2_ladder.py load/cand semantics, single seed)
def load(*paths):
    J = collections.defaultdict(dict)
    for p in paths:
        for l in open(p):
            r = json.loads(l)
            if r.get("ok") and r["order"] not in J[r["queryId"]]: J[r["queryId"]][r["order"]] = r["mapped"]
    return {q: sr(v["boarA"], v["boarB"]) for q, v in J.items() if set(v) == {"boarA", "boarB"}}
CJ = A + "lp-screens/control/judgments/lpctl-K0-main-s42-v01.judgments.jsonl"; ctl_t = T["L1_17B_K0_s42"]
def cand(tk, jf):
    t = T[tk]; j = load(jf); assert all(q in j or t[q] == ctl_t[q] for q in ids); return load(jf, CJ)
H = {"L0_15B_closedbook": load(A + "floor-anchors/judgments/floor-anchors-K0-main-sub3e6183-s42-v01.judgments.jsonl", CJ),
     "L1_17B_K0_s42": load(CJ),
     "L2_GemmaE2B_desk_s42": cand("L2_GemmaE2B_desk_s42", A + "gemma4-e2b/stage2/judgments/gemma4-e2b-eng-K0-main-s42-v01.judgments.jsonl"),
     "L3_4B_phone_cut7": load(R + "device-pixel8a/final-cut7-v01/judgments.haiku.jsonl")}
L = ["L0_15B_closedbook", "L1_17B_K0_s42", "L2_GemmaE2B_desk_s42", "L3_4B_phone_cut7"]
U = lambda s, r: (s - 1).sum() / (r - 1).sum(); NET = lambda u: (u - 0.058) / 0.942
ci = lambda x: [round(float(v), 4) for v in np.percentile(x, [2.5, 97.5])]
def block(S):
    n = len(ids); M = {k: (np.array([S[k][q]["s"] for q in ids]), np.array([S[k][q]["r"] for q in ids])) for k in L}
    rng = np.random.default_rng(11); draws = [rng.integers(0, n, n) for _ in range(2000)]
    pt = {k: U(*M[k]) for k in L}; bs = {k: np.array([U(M[k][0][ii], M[k][1][ii]) for ii in draws]) for k in L}
    lv = {k: {"U": round(pt[k], 4), "U_ci": ci(bs[k]), "U_net": round(NET(pt[k]), 4)} for k in L}
    def pair(a, b):
        d = pt[a] - pt[b]; db = bs[a] - bs[b]; lo = float(np.percentile(db, 2.5))
        return {"dU": round(d, 4), "dU_ci": ci(db), "dU_net": round(d / 0.942, 4), "dU_net_ci": ci(db / 0.942),
                "better_worse": [int(sum(S[a][q]["s"] > S[b][q]["s"] for q in ids)), int(sum(S[a][q]["s"] < S[b][q]["s"] for q in ids))],
                "separable": bool(d >= 0.05 and lo > 0), "mde_n75": round(2.8 * float(db.std()) * (n / 75) ** 0.5, 4)}
    P = {"1.7B-1.5B": pair(L[1], L[0]), "Gemma-1.7B": pair(L[2], L[1]), "4B-Gemma": pair(L[3], L[2]), "Gemma-1.5B": pair(L[2], L[0]),
         "4B-1.7B": pair(L[3], L[1]), "4B-1.5B": pair(L[3], L[0])}
    return {"n": n, "levels": lv, "pairs": P}
out = {"criterion_sha256": crit, "n_units": len(S_["units"]), "reused_units": len(need_reuse), "opus": block(O), "haiku_same_frame": block(H)}
# Opus - Haiku per rung (offset) and the judge difference of each delta, paired bootstrap on the same draws
n = len(ids); rng = np.random.default_rng(11); draws = [rng.integers(0, n, n) for _ in range(2000)]
arr = lambda S, k: (np.array([S[k][q]["s"] for q in ids]), np.array([S[k][q]["r"] for q in ids]))
off = {}
for k in L:
    (so, ro), (sh, rh) = arr(O, k), arr(H, k)
    b = np.array([U(so[ii], ro[ii]) - U(sh[ii], rh[ii]) for ii in draws]); off[k] = {"opus_minus_haiku": round(U(so, ro) - U(sh, rh), 4), "ci": ci(b)}
    rho = spearmanr([O[k][q]["s"] for q in ids], [H[k][q]["s"] for q in ids]).statistic
    off[k]["spearman_s"] = round(float(rho), 3)
    off[k]["ce_agree"] = int(sum((O[k][q]["corr"] <= 1.5) == (H[k][q]["corr"] <= 1.5) for q in ids)); off[k]["correct_agree"] = int(sum((O[k][q]["corr"] >= 4) == (H[k][q]["corr"] >= 4) for q in ids))
out["per_rung"] = off
out["offset_spread"] = round(max(v["opus_minus_haiku"] for v in off.values()) - min(v["opus_minus_haiku"] for v in off.values()), 4)
p = out["opus"]["pairs"]
inc0 = lambda c: c[0] <= 0 <= c[1]
r = {}
r["support_4B_17B"] = bool(p["4B-1.7B"]["dU"] >= 0.05 and p["4B-1.7B"]["dU_ci"][0] > 0)
r["support_level"] = bool(inc0(p["1.7B-1.5B"]["dU_ci"]))
r["kill_sep"] = bool(inc0(p["4B-1.7B"]["dU_ci"]) or inc0(p["4B-Gemma"]["dU_ci"]))
r["sep_below_threshold"] = bool(not r["kill_sep"] and (p["4B-1.7B"]["dU"] < 0.05 or p["4B-Gemma"]["dU"] < 0.05))
r["kill_level"] = bool(p["1.7B-1.5B"]["dU_ci"][0] > 0)
r["level_below"] = bool(p["1.7B-1.5B"]["dU_ci"][1] < 0)
r["kill_haiku_rows"] = bool(min(v["spearman_s"] for v in off.values()) < 0.7)
r["verdict"] = "SUPPORTED" if (r["support_4B_17B"] and r["support_level"] and not r["kill_sep"] and not r["kill_level"] and not r["kill_haiku_rows"]) else ("KILLED" if (r["kill_sep"] or r["kill_level"] or r["kill_haiku_rows"]) else "MIXED")
out["rules"] = r
js = json.dumps(out, indent=1); open(sys.argv[1], "w").write(js + "\n"); print(js)
