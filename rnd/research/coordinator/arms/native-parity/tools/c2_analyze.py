#!/usr/bin/env python3
"""C2-REPLICA-FIDELITY analysis (0 calls). Criterion ../C2-criterion.md. python3 -I c2_analyze.py <out.json>
Estimator copied unchanged from rc1-pixel/tools/a1_analyze.py (CV5 rungs loaded as there; RC1 = A1 Opus rows); adds N-D / N-S Opus rows,
per-item Spearman of s (average ranks), and the frozen C2 rules."""
import json, sys, os, collections, hashlib, statistics, numpy as np
C = "<workspace>/rnd/research/coordinator/"; A = C + "arms/"; W = C + "ruler/cv5-ladder/"; P = A + "native-parity/"
sys.path.insert(0, C + "ruler/tools"); import cv5_opus_pool as CP
sys.path.insert(0, A + "null-cal/tools"); from labels import is_decline
outf = sys.argv[1]
crit = open(P + "C2-criterion.sha256").read().split()[0]
assert hashlib.sha256(open(P + "C2-criterion.md", "rb").read()).hexdigest() == crit, "criterion sha mismatch"
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
def sr(a, b): return {"s": (mr(a["boar"]) + mr(b["boar"])) / 2, "r": (mr(a["ref"]) + mr(b["ref"])) / 2,
                      "corr": (a["boar"]["correctness"] + b["boar"]["correctness"]) / 2, "wins": [a["winner"], b["winner"]]}
S_ = json.load(open(W + "in/set.json")); ids = S_["ids"]; RUNGS = S_["rungs"]
assert sorted(ids) == sorted(l.strip() for l in open(P + "cv5-51.ids") if l.strip())
T = {k: {(j := json.loads(l)).get("itemId") or j.get("queryId"): j["answer"]["text"] for l in open(p)} for k, p in RUNGS.items()}
OP = {}
for k in RUNGS:
    by = collections.defaultdict(dict)
    for l in open(W + f"out/{k}.judgments.jsonl"):
        r = json.loads(l)
        if r.get("ok") and not r.get("floorScored"): by[r["queryId"]].setdefault(r["order"], r["mapped"])
    for q, v in by.items():
        if set(v) == {"boarA", "boarB"}: OP[CP.key(q, T[k][q])] = sr(v["boarA"], v["boarB"])
PL = CP.pool("bd235bb9811f6d1ae88ba2d2ae3973e3572d75b6c451ee4cdd3a2e7644db48b1", "568b3ececd8afe5cad63a7f39bffe414e6dd45bcef9d03ef112faecad2981b18",
             exclude_prefix=W)
for uk, u in S_["units"].items():
    if u["reuse"]: OP.setdefault(uk, sr(PL[uk]["boarA"], PL[uk]["boarB"]))
O = {k: {q: dict(OP[CP.key(q, T[k][q])], text=T[k][q]) for q in ids} for k in RUNGS}
calls = {}
def load(name, jf, texts):
    by = collections.defaultdict(dict); n_calls = 0
    for l in open(jf):
        r = json.loads(l)
        if not r.get("floorScored"): n_calls += 1
        if r.get("ok"): by[r["queryId"]].setdefault(r["order"], r["mapped"])
    miss = [q for q in ids if set(by[q]) != {"boarA", "boarB"}]
    assert not miss, (name, miss)
    O[name] = {q: dict(sr(by[q]["boarA"], by[q]["boarB"]), text=texts.get(q, "")) for q in ids}; calls[name] = n_calls
RCT = {json.loads(l)["itemId"]: json.loads(l)["answer"]["text"] for l in open(A + "rc1-pixel/a1/in/rc-cv5-51-15b.traces.jsonl")}
load("RC1_15B_shipped", A + "rc1-pixel/a1/judgments/rc1-shipped.opus.judgments.jsonl", RCT)
NT = {}
for arm in ("N-D", "N-S"):
    NT[arm] = {(j := json.loads(l))["itemId"]: j["answer"]["text"] for l in open(P + f"traces/native-{arm}-v01-s42.traces.jsonl")}
    jf = P + f"judgments/native-{arm}-v01-s42.opus.judgments.jsonl"
    if os.path.exists(jf): load(arm, jf, NT[arm])
L = [k for k in ("N-D", "N-S", "RC1_15B_shipped", "L0_15B_closedbook", "L1_17B_K0_s42", "L2_GemmaE2B_desk_s42", "L3_4B_phone_cut7") if k in O]
for k in L:
    for q in ids: O[k][q]["dec"] = is_decline(O[k][q]["text"], False)
U = lambda s, r: (s - 1).sum() / (r - 1).sum(); RAW = lambda s, r: s.sum() / r.sum(); NET = lambda u: (u - 0.058) / 0.942
ci = lambda x: [round(float(v), 4) for v in np.percentile(x, [2.5, 97.5])]
n = len(ids); rng = np.random.default_rng(11); draws = [rng.integers(0, n, n) for _ in range(2000)]
def arrs(k, d2s=False):
    s = np.array([1.0 if (d2s and O[k][q]["dec"]) else O[k][q]["s"] for q in ids]); r = np.array([O[k][q]["r"] for q in ids]); return s, r
def wtl(k):
    w = [all(x == "boar" for x in O[k][q]["wins"]) for q in ids]; lo = [all(x == "ref" for x in O[k][q]["wins"]) for q in ids]
    return np.array(w, float), np.array(lo, float)
def cls(k):
    c = {"correct": [], "CE": [], "decline": [], "partial": []}
    for q in ids:
        x = O[k][q]; lab = "decline" if x["dec"] else "correct" if x["corr"] >= 4 else "CE" if x["corr"] <= 1.5 else "partial"
        for kk in c: c[kk].append(1.0 if kk == lab else 0.0)
    return {kk: np.array(v) for kk, v in c.items()}
lv, BS = {}, {}
for k in L:
    s, r = arrs(k); s2, _ = arrs(k, True); w, lo = wtl(k); c = cls(k)
    bu = np.array([U(s[ii], r[ii]) for ii in draws]); b2 = np.array([U(s2[ii], r[ii]) for ii in draws]); bw = np.array([w[ii].mean() for ii in draws])
    braw = np.array([RAW(s[ii], r[ii]) for ii in draws])
    BS[k] = {"U": bu, "D2S": b2, "raw": braw, **{kk: np.array([v[ii].mean() * 100 for ii in draws]) for kk, v in c.items()}}
    lv[k] = {"U": round(U(s, r), 4), "U_ci": ci(bu), "raw": round(RAW(s, r), 4), "raw_ci": ci(braw),
             "U_net": round(NET(U(s, r)), 4), "U_D2S": round(U(s2, r), 4), "U_D2S_ci": ci(b2),
             "win": int(w.sum()), "loss": int(lo.sum()), "tie": int(n - w.sum() - lo.sum()), "win_rate": round(w.mean(), 4), "win_rate_ci": ci(bw),
             "per100": {kk: round(v.mean() * 100, 1) for kk, v in c.items()}, "per100_ci": {kk: ci(BS[k][kk]) for kk in c}}
def pair(a, b):
    d = lv[a]["U"] - lv[b]["U"]; db = BS[a]["U"] - BS[b]["U"]; d2 = lv[a]["U_D2S"] - lv[b]["U_D2S"]; db2 = BS[a]["D2S"] - BS[b]["D2S"]
    return {"dU": round(d, 4), "dU_ci": ci(db), "dU_D2S": round(d2, 4), "dU_D2S_ci": ci(db2),
            "draw": round(lv[a]["raw"] - lv[b]["raw"], 4), "draw_ci": ci(BS[a]["raw"] - BS[b]["raw"]),
            "better_worse": [int(sum(O[a][q]["s"] > O[b][q]["s"] for q in ids)), int(sum(O[a][q]["s"] < O[b][q]["s"] for q in ids))],
            "d_per100": {kk: [round(float((BS[a][kk] - BS[b][kk]).mean()), 1), ci(BS[a][kk] - BS[b][kk])] for kk in ("correct", "CE", "decline")}}
def rank(x):
    x = np.asarray(x); o = np.argsort(x, kind="mergesort"); rk = np.empty(len(x)); i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[o[j + 1]] == x[o[i]]: j += 1
        rk[o[i:j + 1]] = (i + j) / 2 + 1; i = j + 1
    return rk
def spearman(a, b):
    xa = rank([O[a][q]["s"] for q in ids]); xb = rank([O[b][q]["s"] for q in ids]); return round(float(np.corrcoef(xa, xb)[0, 1]), 4)
PR = {}
for a, b in (("N-D", "RC1_15B_shipped"), ("N-S", "N-D"), ("N-S", "RC1_15B_shipped"), ("L1_17B_K0_s42", "N-D"), ("L3_4B_phone_cut7", "N-D"),
             ("L1_17B_K0_s42", "N-S"), ("N-D", "L0_15B_closedbook"), ("N-S", "L0_15B_closedbook")):
    if a in O and b in O: PR[f"{a} - {b}"] = pair(a, b)
SP = {"N-D~RC1": spearman("N-D", "RC1_15B_shipped")} if "N-D" in O else {}
if "N-S" in O: SP["N-S~RC1"] = spearman("N-S", "RC1_15B_shipped"); SP["N-S~N-D"] = spearman("N-S", "N-D")
G = {}
for l in open(P + "runs/s3-gen.jsonl"):
    r = json.loads(l); G.setdefault(r["arm"], {})[r["id"]] = r
tok = {arm: statistics.median(G[arm][q]["tokens_predicted"] for q in ids) for arm in ("N-D", "N-S")}
pers = {arm: dict(collections.Counter(G[arm][q]["persona"] for q in ids)) for arm in ("N-D", "N-S")}
nonempty = {arm: sum(1 for q in ids if NT[arm].get(q, "").strip()) for arm in ("N-D", "N-S")}
fl = {}
if "N-D" in O:
    p = PR["N-D - RC1_15B_shipped"]
    fl["invalid"] = bool(nonempty["N-D"] < 49)
    fl["dU_le_0.05"] = bool(abs(p["dU"]) <= 0.05); fl["spearman_ge_0.6"] = bool(SP["N-D~RC1"] >= 0.6)
    fl["ci_includes_0"] = bool(p["dU_ci"][0] <= 0 <= p["dU_ci"][1])
    fl["fidelity"] = "INVALID" if fl["invalid"] else ("PASS" if fl["dU_le_0.05"] and fl["spearman_ge_0.6"] and fl["ci_includes_0"] else "FAIL")
    fl["equivalent"] = bool(-0.05 <= p["dU_ci"][0] and p["dU_ci"][1] <= 0.05); fl["ce_reproduced"] = bool(lv["N-D"]["per100"]["CE"] >= 55)
if "N-S" in O:
    q = PR["N-S - N-D"]; fl["persona_confirmed"] = bool(q["dU_ci"][0] > 0); fl["consistent_with_haiku_0.077"] = bool(q["draw_ci"][0] <= 0.077 <= q["draw_ci"][1])
out = {"criterion_sha256": crit, "n": n, "opus_calls_in_files": calls, "nonempty": nonempty, "tokens_p50": {**tok, "RC1": 384}, "personas": pers,
       "levels": lv, "pairs": PR, "spearman_s": SP, "rules": fl}
js = json.dumps(out, indent=1); open(outf, "w").write(js + "\n"); print(js)
