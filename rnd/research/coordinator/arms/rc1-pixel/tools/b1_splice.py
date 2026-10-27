#!/usr/bin/env python3
"""B1-LAYER-SPLICE (0 LLM, 0 judge). Criterion ../B1-SPLICE-criterion.md. python3 -I b1_splice.py aggregates/B1-LAYER-SPLICE.json
Loads Opus judge.v1 rows exactly as a1_analyze.py (CV5 rungs via cv5_opus_pool; RC1 from a1/judgments), then replaces the RC1 (and, as a
sensitivity, the L0 1.5B closed-book) item values on the CV5 layer ids with the L3 cut-7 Pixel values when the L3 trace is a deterministic layer."""
import json, sys, collections, hashlib, numpy as np
C = "<workspace>/rnd/research/coordinator/"; A = C + "arms/"; W = C + "ruler/cv5-ladder/"; R = A + "rc1-pixel/"
sys.path.insert(0, C + "ruler/tools"); import cv5_opus_pool as CP
sys.path.insert(0, A + "null-cal/tools"); from labels import is_decline
outf = sys.argv[1]
crit = open(R + "B1-SPLICE-criterion.sha256").read().split()[0]
assert hashlib.sha256(open(R + "B1-SPLICE-criterion.md", "rb").read()).hexdigest() == crit, "criterion sha mismatch"
LAYER = ["lan-cmp-001", "lan-exp-006", "lan-ref-001", "lan-ref-004", "lan-ref-005", "lan-rsn-002", "lan-rsn-007", "trv-002"]
RC1_J = R + "a1/judgments/rc1-shipped.opus.judgments.jsonl"; RC1_ROWS = "<workspace>/handoff/pixel8-2026-10-20/bench/results/rc-cv5-51-15b/rows.jsonl"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
def sr(a, b): return {"s": (mr(a["boar"]) + mr(b["boar"])) / 2, "r": (mr(a["ref"]) + mr(b["ref"])) / 2,
                      "corr": (a["boar"]["correctness"] + b["boar"]["correctness"]) / 2, "wins": [a["winner"], b["winner"]]}
S_ = json.load(open(W + "in/set.json")); ids = S_["ids"]; RUNGS = S_["rungs"]
TR = {k: {(j := json.loads(l)).get("itemId") or j.get("queryId"): j for l in open(p)} for k, p in RUNGS.items()}
T = {k: {q: j["answer"]["text"] for q, j in v.items()} for k, v in TR.items()}
OP, SRC = {}, {}
for k in RUNGS:
    by = collections.defaultdict(dict)
    for l in open(W + f"out/{k}.judgments.jsonl"):
        r = json.loads(l)
        if r.get("ok") and not r.get("floorScored"): by[r["queryId"]].setdefault(r["order"], r)
    for q, v in by.items():
        if set(v) == {"boarA", "boarB"}:
            OP[CP.key(q, T[k][q])] = sr(v["boarA"]["mapped"], v["boarB"]["mapped"])
            SRC[(k, q)] = {"file": f"ruler/cv5-ladder/out/{k}.judgments.jsonl", "orders": ["boarA", "boarB"], "seed": v["boarA"].get("seed"),
                           "judgeModel": v["boarA"].get("judgeModel"), "judgeVersion": v["boarA"].get("judgeVersion"),
                           "createdAt": [v["boarA"].get("createdAt"), v["boarB"].get("createdAt")]}
P = CP.pool("bd235bb9811f6d1ae88ba2d2ae3973e3572d75b6c451ee4cdd3a2e7644db48b1", "568b3ececd8afe5cad63a7f39bffe414e6dd45bcef9d03ef112faecad2981b18",
            exclude_prefix=W)
for uk, u in S_["units"].items():
    if u["reuse"]: OP.setdefault(uk, sr(P[uk]["boarA"], P[uk]["boarB"]))
O = {k: {q: dict(OP[CP.key(q, T[k][q])], text=T[k][q]) for q in ids} for k in RUNGS}
RW = {(r := json.loads(l))["queryId"]: r for l in open(RC1_ROWS)}
by = collections.defaultdict(dict); calls_rc1 = 0
for l in open(RC1_J):
    r = json.loads(l); calls_rc1 += 0 if r.get("floorScored") else 1
    if r.get("ok"): by[r["queryId"]].setdefault(r["order"], r["mapped"])
O["RC1"] = {q: dict(sr(by[q]["boarA"], by[q]["boarB"]), text=(RW.get(q) or {}).get("answer") or "") for q in ids}
# ---- deterministic-layer check on L3
det = {}
for q in LAYER:
    j = TR["L3_4B_phone_cut7"][q]; codes = (j.get("route") or {}).get("reasonCodes") or []
    det[q] = {"outputTokens": (j.get("timing") or {}).get("outputTokens"), "reasonCodes": codes,
              "deterministic": (j.get("timing") or {}).get("outputTokens") == 0 and any(c.startswith("answer:") for c in codes),
              "same_text_L1_L2": T["L1_17B_K0_s42"].get(q) == T["L3_4B_phone_cut7"][q] == T["L2_GemmaE2B_desk_s42"].get(q),
              "judgment_source": SRC.get(("L3_4B_phone_cut7", q))}
SPL = [q for q in LAYER if det[q]["deterministic"]]
for base in ("RC1", "L0_15B_closedbook"):
    O[base + "_spliced"] = {q: (dict(O["L3_4B_phone_cut7"][q]) if q in SPL else dict(O[base][q])) for q in ids}
L = ["RC1", "RC1_spliced", "L0_15B_closedbook", "L0_15B_closedbook_spliced"]
for k in L:
    for q in ids: O[k][q]["dec"] = is_decline(O[k][q]["text"], False)
U = lambda s, r: (s - 1).sum() / (r - 1).sum(); RAW = lambda s, r: s.sum() / r.sum()
ci = lambda x: [round(float(v), 4) for v in np.percentile(x, [2.5, 97.5])]
n = len(ids); rng = np.random.default_rng(11); draws = [rng.integers(0, n, n) for _ in range(2000)]
def arrs(k, d2s=False):
    return (np.array([1.0 if (d2s and O[k][q]["dec"]) else O[k][q]["s"] for q in ids]), np.array([O[k][q]["r"] for q in ids]))
def cls(k):
    c = {"correct": [], "CE": [], "decline": [], "partial": []}
    for q in ids:
        x = O[k][q]; lab = "decline" if x["dec"] else "correct" if x["corr"] >= 4 else "CE" if x["corr"] <= 1.5 else "partial"
        for kk in c: c[kk].append(1.0 if kk == lab else 0.0)
    return {kk: np.array(v) for kk, v in c.items()}
lv, BS = {}, {}
for k in L:
    s, r = arrs(k); s2, _ = arrs(k, True); c = cls(k)
    w = np.array([all(x == "boar" for x in O[k][q]["wins"]) for q in ids], float); lo = np.array([all(x == "ref" for x in O[k][q]["wins"]) for q in ids], float)
    BS[k] = {"U": np.array([U(s[ii], r[ii]) for ii in draws]), "D2S": np.array([U(s2[ii], r[ii]) for ii in draws]),
             **{kk: np.array([v[ii].mean() * 100 for ii in draws]) for kk, v in c.items()}}
    lv[k] = {"U": round(U(s, r), 4), "U_ci": ci(BS[k]["U"]), "raw": round(RAW(s, r), 4), "U_D2S": round(U(s2, r), 4),
             "win": int(w.sum()), "loss": int(lo.sum()), "per100": {kk: round(v.mean() * 100, 1) for kk, v in c.items()}}
def pair(a, b):
    db = BS[a]["U"] - BS[b]["U"]
    return {"dU": round(lv[a]["U"] - lv[b]["U"], 4), "dU_ci": ci(db), "dU_D2S": round(lv[a]["U_D2S"] - lv[b]["U_D2S"], 4),
            "dU_D2S_ci": ci(BS[a]["D2S"] - BS[b]["D2S"]),
            "d_per100": {kk: [round(lv[a]["per100"][kk] - lv[b]["per100"][kk], 1), ci(BS[a][kk] - BS[b][kk])] for kk in ("correct", "CE", "decline")}}
PR = {"RC1_spliced-RC1": pair("RC1_spliced", "RC1"), "L0_spliced-L0": pair("L0_15B_closedbook_spliced", "L0_15B_closedbook")}
per_item = {q: {"RC1_s": round(O["RC1"][q]["s"], 3), "RC1_corr": O["RC1"][q]["corr"], "L0_s": round(O["L0_15B_closedbook"][q]["s"], 3),
                "layer_s": round(O["L3_4B_phone_cut7"][q]["s"], 3), "layer_corr": O["L3_4B_phone_cut7"][q]["corr"], "r": round(O["RC1"][q]["r"], 3)} for q in LAYER}
p = PR["RC1_spliced-RC1"]; nl = len(SPL)
rules = {"n_layer": nl, "dU_ge_0.04": bool(p["dU"] >= 0.04), "ci_low_gt_0": bool(p["dU_ci"][0] > 0), "dCE_le_-8": bool(p["d_per100"]["CE"][0] <= -8),
         "kill": bool(nl < 5 or p["dU"] < 0.02)}
rules["verdict"] = "KILL" if rules["kill"] else ("SUPPORTED" if all(rules[k] for k in ("dU_ge_0.04", "ci_low_gt_0", "dCE_le_-8")) else "MIXED")
out = {"criterion_sha256": crit, "n": n, "inputs": {"rc1_judgments_sha256": sha(RC1_J), "rc1_rows_sha256": sha(RC1_ROWS),
       "l3_traces_sha256": sha(RUNGS["L3_4B_phone_cut7"]), "l3_judgments_sha256": sha(W + "out/L3_4B_phone_cut7.judgments.jsonl"),
       "rc1_judge_rows_in_file": calls_rc1, "new_judge_calls": 0, "llm_calls": 0},
       "layer_check": det, "spliced_ids": SPL, "levels": lv, "pairs": PR, "per_item": per_item, "rules": rules}
js = json.dumps(out, indent=1); open(outf, "w").write(js + "\n"); print(js)
