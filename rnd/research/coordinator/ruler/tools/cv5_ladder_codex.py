#!/usr/bin/env python3
"""CV5-LADDER-CODEX scorer (criterion ruler/CV5-LADDER-CODEX-criterion.md). 0 LLM. Usage:
  python3 -I cv5_ladder_codex.py <out.json> [--codex-dir ruler/codex-ladder/out]
Reads the Codex judge.v1 rows r4to produced (<rung>.codex.judgments.jsonl), the Haiku rows of the identical single-seed frame
(same files and load semantics as rv2_ladder.py / CV5-LADDER-OPUS) and, if present, the CV5-LADDER-OPUS rows. Per judge: U per rung,
the six adjacent/skip pairs (dU, bootstrap CI, SEPARABLE iff dU >= 0.05 and CI low > 0). Codex vs Haiku: per-rung offset U_codex - U_haiku
with CI, offset spread (max - min over rungs), per-item Spearman of s. Verdict by the frozen kill rules."""
import json, sys, collections, numpy as np
from pathlib import Path
A = "<workspace>/rnd/research/coordinator/arms/"; R = "<workspace>/boar-eval/runs/"
RU = "<workspace>/rnd/research/coordinator/ruler/"
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
def load(*paths):  # rv2_ladder.py semantics: first ok row per (item, order) wins across files
    J = collections.defaultdict(dict)
    for p in paths:
        if not Path(p).exists(): continue
        for l in open(p):
            r = json.loads(l)
            if r.get("ok") and r["order"] not in J[r["queryId"]]: J[r["queryId"]][r["order"]] = r["mapped"]
    return {q: {"s": (mr(v["boarA"]["boar"]) + mr(v["boarB"]["boar"])) / 2, "r": (mr(v["boarA"]["ref"]) + mr(v["boarB"]["ref"])) / 2}
            for q, v in J.items() if set(v) == {"boarA", "boarB"}}
a = sys.argv[1:]; outp = a[0]; cdir = Path(a[a.index("--codex-dir") + 1]) if "--codex-dir" in a else Path(RU + "codex-ladder/out")
ids = json.load(open(RU + "cv5-ladder/in/set.json"))["ids"]; assert len(ids) == 51
RUNGS = ["L0_15B_closedbook", "L1_17B_K0_s42", "L2_GemmaE2B_desk_s42", "L3_4B_phone_cut7"]
CJ = A + "lp-screens/control/judgments/lpctl-K0-main-s42-v01.judgments.jsonl"
HAIKU = {"L0_15B_closedbook": load(A + "floor-anchors/judgments/floor-anchors-K0-main-sub3e6183-s42-v01.judgments.jsonl", CJ),
         "L1_17B_K0_s42": load(CJ),
         "L2_GemmaE2B_desk_s42": load(A + "gemma4-e2b/stage2/judgments/gemma4-e2b-eng-K0-main-s42-v01.judgments.jsonl", CJ),
         "L3_4B_phone_cut7": load(R + "device-pixel8a/final-cut7-v01/judgments.haiku.jsonl")}
CODEX = {k: load(cdir / f"{k}.codex.judgments.jsonl") for k in RUNGS}
OPUS = {k: load(RU + f"cv5-ladder/out/{k}.judgments.jsonl") for k in RUNGS}
U = lambda S_, R_: (S_ - 1).sum() / (R_ - 1).sum()
ci = lambda x: [round(float(v), 4) for v in np.percentile(x, [2.5, 97.5])]
n = len(ids); rng = np.random.default_rng(11); draws = [rng.integers(0, n, n) for _ in range(2000)]
PAIRS = [("L1_17B_K0_s42", "L0_15B_closedbook"), ("L2_GemmaE2B_desk_s42", "L1_17B_K0_s42"), ("L3_4B_phone_cut7", "L2_GemmaE2B_desk_s42"),
         ("L2_GemmaE2B_desk_s42", "L0_15B_closedbook"), ("L3_4B_phone_cut7", "L1_17B_K0_s42"), ("L3_4B_phone_cut7", "L0_15B_closedbook")]
def judge_block(J):
    miss = {k: [q for q in ids if q not in J[k]] for k in RUNGS}
    if any(miss.values()): return {"complete": False, "missing": {k: len(v) for k, v in miss.items()}}
    M = {k: (np.array([J[k][q]["s"] for q in ids]), np.array([J[k][q]["r"] for q in ids])) for k in RUNGS}
    pt = {k: U(*M[k]) for k in RUNGS}; bs = {k: np.array([U(M[k][0][ii], M[k][1][ii]) for ii in draws]) for k in RUNGS}
    lv = {k: {"U": round(pt[k], 4), "U_ci": ci(bs[k])} for k in RUNGS}
    pr = {}
    for x, y in PAIRS:
        d = pt[x] - pt[y]; db = bs[x] - bs[y]; lo = float(np.percentile(db, 2.5))
        pr[f"{x} - {y}"] = {"dU": round(d, 4), "dU_ci": ci(db), "separable": bool(d >= 0.05 and lo > 0)}
    return {"complete": True, "levels": lv, "pairs": pr, "_bs": bs, "_pt": pt, "_M": M}
def spearman(x, y):
    def avg(v):  # average ranks for ties
        v = np.asarray(v); r = np.empty(len(v)); s = np.argsort(v, kind="stable"); i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[s[j + 1]] == v[s[i]]: j += 1
            r[s[i:j + 1]] = (i + j) / 2; i = j + 1
        return r
    return round(float(np.corrcoef(avg(x), avg(y))[0, 1]), 3)
out = {"criterion_sha256": open(RU + "CV5-LADDER-CODEX-criterion.sha256").read().split()[0], "n": n, "codex_dir": str(cdir)}
blocks = {"haiku": judge_block(HAIKU), "codex": judge_block(CODEX), "opus": judge_block(OPUS)}
for k, b in blocks.items(): out[k] = {kk: vv for kk, vv in b.items() if not kk.startswith("_")}
c, h = blocks["codex"], blocks["haiku"]
if c["complete"] and h["complete"]:
    off = {k: (c["_pt"][k] - h["_pt"][k], c["_bs"][k] - h["_bs"][k]) for k in RUNGS}
    out["offset_codex_minus_haiku"] = {k: {"dU": round(v[0], 4), "ci": ci(v[1])} for k, v in off.items()}
    sp = max(v[0] for v in off.values()) - min(v[0] for v in off.values())
    spb = np.max(np.array([off[k][1] for k in RUNGS]), axis=0) - np.min(np.array([off[k][1] for k in RUNGS]), axis=0)
    out["offset_spread"] = {"point": round(sp, 4), "ci": ci(spb)}
    out["spearman_codex_vs_haiku_s"] = {k: spearman(c["_M"][k][0], h["_M"][k][0]) for k in RUNGS}
    p = c["pairs"]; g = p["L3_4B_phone_cut7 - L1_17B_K0_s42"]
    kill_ci0 = bool(g["dU_ci"][0] <= 0 <= g["dU_ci"][1]); kill_spread = bool(sp > 0.03)
    support = bool(not kill_ci0) and g["dU"] >= 0.05 and p["L3_4B_phone_cut7 - L2_GemmaE2B_desk_s42"]["separable"] \
        and not p["L1_17B_K0_s42 - L0_15B_closedbook"]["separable"] and not kill_spread
    out["verdict"] = {"kill_4B_minus_17B_ci_includes_0": kill_ci0, "kill_offset_spread_gt_0.03": kill_spread, "support": support,
                      "same_separability_as_haiku": {kk: p[kk]["separable"] == h["pairs"][kk]["separable"] for kk in p}}
else:
    out["verdict"] = "INCOMPLETE: Codex rows missing (r4to has not run, or a rung stopped); NOT RUN after 10-23 18:00"
js = json.dumps(out, indent=1); open(outp, "w").write(js + "\n"); print(js)
