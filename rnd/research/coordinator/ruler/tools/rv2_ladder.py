#!/usr/bin/env python3
"""RV2-SEP-LADDER (criterion ruler/RV24-criterion.md). 0 LLM. Usage: python3 -I rv2_ladder.py <out.json>
Rungs on v0.1 57 minus FLOOR's 6 deterministic items: 1.5B closed-book < 1.7B K0 (2 seeds) < Gemma E2B desktop (2 seeds) < 4B phone cut 7.
U = sum(s-1)/sum(r-1) (judge.v1 Haiku), item-cluster bootstrap B 2000 seed 11; U_net = (U-0.058)/0.942."""
import json, sys, collections, numpy as np
A = "<workspace>/rnd/research/coordinator/arms/"; R = "<workspace>/boar-eval/runs/"
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
CAT = {}
def load(*paths):  # floor_agg.py semantics: first ok row per (item, order) wins across files
    J = collections.defaultdict(dict)
    for p in paths:
        for l in open(p):
            r = json.loads(l)
            if r.get("category"): CAT.setdefault(r["queryId"], r["category"])
            if r.get("ok") and r["order"] not in J[r["queryId"]]: J[r["queryId"]][r["order"]] = r["mapped"]
    return {q: {"s": (mr(v["boarA"]["boar"]) + mr(v["boarB"]["boar"])) / 2, "r": (mr(v["boarA"]["ref"]) + mr(v["boarB"]["ref"])) / 2}
            for q, v in J.items() if set(v) == {"boarA", "boarB"}}
def txt(p): return {(j := json.loads(l)).get("itemId") or j.get("queryId"): j["answer"]["text"] for l in open(p)}
CT = A + "lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl"; CJ = A + "lp-screens/control/judgments/lpctl-K0-main-s42-v01.judgments.jsonl"
ids57 = open(A + "gemma4-e2b/phone/judge/v01-57.ids").read().split()
ctl_t = txt(CT)
def cand(tr, jf):  # unjudged answers byte-identical to the control reuse its rows (run_arm.sh rule)
    t = txt(tr); return load(jf, CJ) if all(q in load(jf) or t[q] == ctl_t[q] for q in ids57) else sys.exit(f"bad reuse {tr}")
def mean2(a, b): return {q: {"s": (a[q]["s"] + b[q]["s"]) / 2, "r": (a[q]["r"] + b[q]["r"]) / 2} for q in a if q in b}
G = A + "gemma4-e2b-confirm/runs/"; F = A + "floor-anchors/"
run = "floor-anchors-K0-main-sub3e6183-s42"
S = {"L0_15B_closedbook": load(F + f"judgments/{run}-v01.judgments.jsonl", CJ),
     "L1_17B_K0_2seed": mean2(load(CJ), cand(G + "c43/traces/gemma4-e2b-confirm-c43-K0-main-s42.traces.jsonl", G + "c43/judgments/gemma4-e2b-confirm-c43-K0-main-s42-v01.judgments.jsonl")),
     "L2_GemmaE2B_desk_2seed": mean2(cand(A + "gemma4-e2b/stage2/traces/gemma4-e2b-eng-K0-main-s42.traces.jsonl", A + "gemma4-e2b/stage2/judgments/gemma4-e2b-eng-K0-main-s42-v01.judgments.jsonl"),
                                     cand(G + "g43/traces/gemma4-e2b-confirm-g43-K0-main-s42.traces.jsonl", G + "g43/judgments/gemma4-e2b-confirm-g43-K0-main-s42-v01.judgments.jsonl")),
     "L3_4B_phone_cut7": load(R + "device-pixel8a/final-cut7-v01/judgments.haiku.jsonl"),
     "sens_17B_s42": load(CJ), "sens_Gemma_phone": load(R + "device-pixel8a/gemma73-a/judgments.haiku.jsonl"),
     "sens_4B_desk_cut7_s42": load(A + "stack/runs/v01-cut7-stack-off-s42.judgments.jsonl")}
det6 = json.load(open(F + "aggregates/floor.json"))["nonmodel_path_items"]
det15 = [q for q in open(A + "../ruler/ids/deterministic-v01.ids").read().split() if q in ids57]
kept = {(j := json.loads(l))["itemId"]: len(j["retrieval"]["kept"]) > 0 for l in open(CT)}
U = lambda S_, R_: (S_ - 1).sum() / (R_ - 1).sum()
ci = lambda x: [round(float(v), 4) for v in np.percentile(x, [2.5, 97.5])]
NET = lambda u: (u - 0.058) / (1 - 0.058)
def block(ids, keys):
    n = len(ids); M = {k: (np.array([S[k][q]["s"] for q in ids]), np.array([S[k][q]["r"] for q in ids])) for k in keys}
    rng = np.random.default_rng(11); draws = [rng.integers(0, n, n) for _ in range(2000)]
    pt = {k: U(*M[k]) for k in keys}; bs = {k: np.array([U(M[k][0][ii], M[k][1][ii]) for ii in draws]) for k in keys}
    lv = {k: {"U": round(pt[k], 4), "U_ci": ci(bs[k]), "U_net": round(NET(pt[k]), 4), "U_net_ci": ci(NET(bs[k]))} for k in keys}
    def pair(a, b):
        d = pt[a] - pt[b]; db = bs[a] - bs[b]; lo = float(np.percentile(db, 2.5))
        return {"dU": round(d, 4), "dU_ci": ci(db), "dU_net": round(d / 0.942, 4), "dU_net_ci": ci(db / 0.942),
                "better_worse": [int(sum(S[a][q]["s"] > S[b][q]["s"] for q in ids)), int(sum(S[a][q]["s"] < S[b][q]["s"] for q in ids))],
                "separable": bool(d >= 0.05 and lo > 0), "separable_net": bool(d / 0.942 >= 0.05 and lo > 0),
                "se": round(float(db.std()), 4), "mde_n75": round(2.8 * float(db.std()) * (n / 75) ** 0.5, 4)}
    return n, lv, pair
out = {"criterion_sha256": open(A + "../ruler/RV24-criterion.sha256").read().split()[0], "det6": det6, "det15_in57": det15}
L = ["L0_15B_closedbook", "L1_17B_K0_2seed", "L2_GemmaE2B_desk_2seed", "L3_4B_phone_cut7"]
for name, ids in (("primary_51", [q for q in ids57 if q not in det6]), ("sens_42_no_det15", [q for q in ids57 if q not in det15]), ("sens_all57", ids57)):
    ids = [q for q in ids if all(q in S[k] for k in S)]
    n, lv, pair = block(ids, list(S))
    P = {"L1-L0": pair(L[1], L[0]), "L2-L1": pair(L[2], L[1]), "L3-L2": pair(L[3], L[2]), "L2-L0": pair(L[2], L[0]), "L3-L1": pair(L[3], L[1]), "L3-L0 (4B-1.5B)": pair(L[3], L[0]),
         "sens Gphone-L1": pair("sens_Gemma_phone", L[1]), "sens L3-Gphone": pair(L[3], "sens_Gemma_phone"), "sens 4Bdesk-L0": pair("sens_4B_desk_cut7_s42", L[0]),
         "sens 17s42-L0": pair("sens_17B_s42", L[0])}
    out[name] = {"n": n, "levels": lv, "pairs": P}
ids = [q for q in ids57 if q not in det6 and all(q in S[k] for k in S)]
cov = [q for q in ids if kept[q]]; unc = [q for q in ids if not kept[q]]
def gap(ii): return U(np.array([S[L[1]][q]["s"] for q in ii]), np.array([S[L[1]][q]["r"] for q in ii])) - U(np.array([S[L[0]][q]["s"] for q in ii]), np.array([S[L[0]][q]["r"] for q in ii]))
rng = np.random.default_rng(11); bc, bu = [], []
for _ in range(2000):
    c = [cov[i] for i in rng.integers(0, len(cov), len(cov))]; u = [unc[i] for i in rng.integers(0, len(unc), len(unc))]; bc.append(gap(c)); bu.append(gap(u))
bc, bu = np.array(bc), np.array(bu)
out["did_17_vs_15"] = {"n_covered": len(cov), "n_uncovered": len(unc), "gap_covered": round(gap(cov), 4), "gap_covered_ci": ci(bc),
                       "gap_uncovered": round(gap(unc), 4), "gap_uncovered_ci": ci(bu), "DiD": round(gap(cov) - gap(unc), 4), "DiD_ci": ci(bc - bu)}
p = out["primary_51"]["pairs"]; d = out["did_17_vs_15"]
out["rules"] = {"H-a 4B-1.5B >= 0.08 and CI low > 0.03": bool(p["L3-L0 (4B-1.5B)"]["dU"] >= 0.08 and p["L3-L0 (4B-1.5B)"]["dU_ci"][0] > 0.03),
                "H-b 1.7B-1.5B < 0.05": bool(p["L1-L0"]["dU"] < 0.05),
                "H-c DiD > 0 with CI low > 0": bool(d["DiD"] > 0 and d["DiD_ci"][0] > 0),
                "kill-1 CI low 4B-1.5B <= 0": bool(p["L3-L0 (4B-1.5B)"]["dU_ci"][0] <= 0),
                "kill-2 covered gap <= 0.05 or DiD CI includes 0": bool(d["gap_covered"] <= 0.05 or d["DiD_ci"][0] <= 0 <= d["DiD_ci"][1])}
js = json.dumps(out, indent=1); open(sys.argv[1], "w").write(js + "\n"); print(js)
