#!/usr/bin/env python3
"""RV1-DECLINE-CU (criterion ruler/RV1-HON8-criterion.md, sha checked). 0 LLM. Usage: python3 -I rv1_cu.py <out.json>
U_full / U_CU / U_Z / U' on existing judge.v1 rows: decline validity, consistency 40, retest 20, gaps+ranks (ladder 51, MAIN 97), Spearman, Opus family check."""
import json, glob, sys, os, hashlib, collections, statistics as st, re, numpy as np
C0 = "<workspace>/rnd/research/coordinator"; A = C0 + "/arms/"; RU = C0 + "/ruler/"; RR = "<workspace>/boar-eval/runs/"
CRIT = open(RU + "RV1-HON8-criterion.sha256").read().split()[0]
assert hashlib.sha256(open(RU + "RV1-HON8-criterion.md", "rb").read()).hexdigest() == CRIT
sys.path.insert(0, A + "null-cal/tools"); from labels import ENGINE_DECLINE, is_decline  # noqa
D3 = ("correctness", "completeness", "usefulness"); D2 = ("completeness", "usefulness"); SUB = 0.058
def rows(*paths):  # floor_agg semantics: first ok row per (item, order) across files
    J = collections.defaultdict(dict)
    for p in paths:
        for l in open(p):
            r = json.loads(l)
            if r.get("ok") and r["order"] not in J[r["queryId"]]: J[r["queryId"]][r["order"]] = r["mapped"]
    return {q: v for q, v in J.items() if set(v) == {"boarA", "boarB"}}
def item(v, zero_corr=False):
    a, b = v["boarA"], v["boarB"]; dim = lambda side, k: (a[side][k] + b[side][k]) / 2
    corr = 1.0 if zero_corr else dim("boar", "correctness")
    sf = (corr + dim("boar", "completeness") + dim("boar", "usefulness")) / 3; rf = sum(dim("ref", k) for k in D3) / 3
    return dict(full=(sf, rf), cu=(sum(dim("boar", k) for k in D2) / 2, sum(dim("ref", k) for k in D2) / 2), corr=dim("boar", "correctness"), corr_z=corr)
def arm(J, decl=lambda q: False):  # -> {q: {"full":(s,r), "cu":(s,r), "z":(s,r), ...}}
    out = {}
    for q, v in J.items():
        it = item(v); it["z"] = item(v, zero_corr=decl(q))["full"]; out[q] = it
    return out
Uf = lambda S, R: (S - 1).sum() / (R - 1).sum()
ci = lambda x: [round(float(v), 4) for v in np.percentile(x, [2.5, 97.5])]
def draws(n): rng = np.random.default_rng(11); return [rng.integers(0, n, n) for _ in range(2000)]
def levels(X, ids, m):
    S = np.array([X[q][m][0] for q in ids]); R = np.array([X[q][m][1] for q in ids]); return S, R
def ustat(X, ids, m):
    S, R = levels(X, ids, m); b = np.array([Uf(S[ii], R[ii]) for ii in draws(len(ids))]); return round(float(Uf(S, R)), 4), ci(b)
out = {"criterion_sha256": CRIT, "script_sha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest()}
# ---- 1. decline validity
F = A + "floor-anchors/"; ids30 = open(F + "decline-30.ids").read().split(); dv = {}
TRD = {v: {json.loads(l)["itemId"]: json.loads(l) for l in open(F + f"traces/fa-decline-{v}.traces.jsonl")} for v in "abc"}
for v in "abc":
    eng = lambda q: bool(TRD[v][q]["answer"]["declined"]) or bool(ENGINE_DECLINE.search(TRD[v][q]["answer"]["text"]))
    lab = lambda q: is_decline(TRD[v][q]["answer"]["text"], TRD[v][q]["answer"]["declined"])
    X = arm(rows(F + f"judgments/fa-decline-{v}.judgments.jsonl"), eng); Xs = arm(rows(F + f"judgments/fa-decline-{v}.judgments.jsonl"), lab)
    ids = [q for q in ids30 if q in X]; r = {"n": len(ids), "engine_flagged": sum(eng(q) for q in ids), "labels_is_decline": sum(lab(q) for q in ids)}
    for m in ("full", "cu", "z"): u, c = ustat(X, ids, m); r[f"U_{m}"] = u; r[f"U_{m}_ci"] = c; r[f"pass_{m}"] = c[1] <= 0.05
    u, c = ustat(Xs, ids, "z"); r["U_zprime"] = u; r["U_zprime_ci"] = c; r["pass_zprime"] = c[1] <= 0.05
    u, c = ustat(X, ids, "full"); r["U_sub"] = round((u - SUB) / (1 - SUB), 4); r["U_sub_ci"] = [round((x - SUB) / (1 - SUB), 4) for x in c]; r["pass_sub"] = r["U_sub_ci"][1] <= 0.05
    r["items_cu_gt_1"] = sum(X[q]["cu"][0] > 1 for q in ids)
    dv[v] = r
out["1_decline"] = dv
out["1_pass"] = {m: all(dv[v][f"pass_{m}"] for v in "abc") for m in ("full", "cu", "z", "zprime", "sub")}
# ---- v1 repeats (lp-screens control = rep1, judge-v2/v1 rep2, rep3) for the 97 MAIN control answers
CJd = A + "lp-screens/control/judgments"; J2 = A + "judge-v2/v1"
REP = [arm(rows(*sorted(glob.glob(f"{CJd}/lpctl-K0-main-s42-*.judgments.jsonl"))))] + [arm(rows(*sorted(glob.glob(f"{J2}/rep{r}-*.judgments.jsonl")))) for r in (2, 3)]
n_ = lambda s: (s - 1) / 4
grp = {l.split("\t")[0]: l.split("\t")[2].strip() for l in open(A + "floor-anchors/v1_1/data/controls-40.tsv")}
ids40 = [q for q in grp if all(q in R_ for R_ in REP)]
nf = {q: st.mean(n_(R_[q]["full"][0]) for R_ in REP) for q in ids40}; nc = {q: st.mean(n_(R_[q]["cu"][0]) for R_ in REP) for q in ids40}
ce_full = {q: [R_[q]["corr"] <= 1.5 for R_ in REP] for q in ids40}; ce_cu = {q: [R_[q]["corr"] <= 1.5 for R_ in REP] for q in ids40}
flips = sum(a != b for q in ids40 for a, b in zip(ce_full[q], ce_cu[q])); assert flips == 0
proxy = [(R_[q]["corr"] <= 1.5, (R_[q]["cu"][0]) <= 1.5) for R_ in REP for q in ids40]
mad = st.mean(abs(nc[q] - nf[q]) for q in ids40)
out["2_consistency40"] = dict(n=len(ids40), mean_abs_dn=round(mad, 4), signed_mean_dn=round(st.mean(nc[q] - nf[q] for q in ids40), 4),
    mad_by_group={g: round(st.mean(abs(nc[q] - nf[q]) for q in ids40 if grp[q] == g), 4) for g in ("correct", "wrong")},
    mean_n_full_by_group={g: round(st.mean(nf[q] for q in ids40 if grp[q] == g), 4) for g in ("correct", "wrong")},
    mean_n_cu_by_group={g: round(st.mean(nc[q] for q in ids40 if grp[q] == g), 4) for g in ("correct", "wrong")},
    ce_flips=flips, ce_definition="CE = correctness (mean of both orders) <= 1.5, read from the same judge.v1 rows; unchanged under U_CU",
    cu_proxy_vs_ce=dict(rows=len(proxy), both=sum(a and b for a, b in proxy), ce_only=sum(a and not b for a, b in proxy), proxy_only=sum(b and not a for a, b in proxy), neither=sum(not a and not b for a, b in proxy)),
    U_full_rep1=ustat(REP[0], ids40, "full"), U_cu_rep1=ustat(REP[0], ids40, "cu"), ok=mad <= 0.05 and flips <= 2)
# ---- 3. retest (v1 repeats 1-2 on retest-20)
rt = open(A + "floor-anchors/v1_1/data/retest-20.ids").read().split()
det = set(open(RU + "ids/deterministic-pool.ids").read().split()) | set(open(RU + "ids/deterministic-v01.ids").read().split())
def sd(m, ids): return round(st.mean(st.stdev([n_(REP[0][q][m][0]), n_(REP[1][q][m][0])]) for q in ids), 4)
rtn = [q for q in rt if q not in det]
out["3_retest20"] = dict(n=len(rt), sd_full=sd("full", rt), sd_cu=sd("cu", rt), bar=0.0206, ok=sd("cu", rt) <= 0.0206,
    exact_same_cu=sum(abs(REP[0][q]["cu"][0] - REP[1][q]["cu"][0]) < 1e-9 for q in rt), exact_same_full=sum(abs(REP[0][q]["full"][0] - REP[1][q]["full"][0]) < 1e-9 for q in rt),
    sens_no_det=dict(n=len(rtn), sd_full=sd("full", rtn), sd_cu=sd("cu", rtn)),
    sens_3rep_all97=dict(sd_full=round(st.mean(st.stdev([n_(R_[q]["full"][0]) for R_ in REP]) for q in REP[0]), 4), sd_cu=round(st.mean(st.stdev([n_(R_[q]["cu"][0]) for R_ in REP]) for q in REP[0]), 4)))
# ---- 4. gaps and ranks
def txt(p): return {(j := json.loads(l)).get("itemId"): j for l in open(p) if l.strip()}
def eng_decl(T): return lambda q: q in T and (bool(T[q]["answer"].get("declined")) or bool(ENGINE_DECLINE.search(T[q]["answer"]["text"])))
CT = A + "lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl"; CTt = txt(CT); CJ = CJd + "/lpctl-K0-main-s42-v01.judgments.jsonl"
CJall = sorted(glob.glob(f"{CJd}/lpctl-K0-main-s42-*.judgments.jsonl"))
def reuse(tr, jfiles, ids, ctlfiles):
    T = txt(tr); own = rows(*jfiles)
    bad = [q for q in ids if q not in own and T[q]["answer"]["text"] != CTt[q]["answer"]["text"]]
    if bad: sys.exit(f"bad reuse {tr} {bad[:5]}")
    return arm(rows(*jfiles, *ctlfiles), eng_decl(T))
def mean2(a, b):
    o = {}
    for q in a:
        if q in b: o[q] = {m: ((a[q][m][0] + b[q][m][0]) / 2, (a[q][m][1] + b[q][m][1]) / 2) for m in ("full", "cu", "z")}
    return o
ids57 = open(A + "gemma4-e2b/phone/judge/v01-57.ids").read().split(); G = A + "gemma4-e2b-confirm/runs/"; FA = "floor-anchors-K0-main-sub3e6183-s42"
TR15 = txt(F + f"traces/{FA}.traces.jsonl")
L = {"L0_15B_closedbook": arm(rows(F + f"judgments/{FA}-v01.judgments.jsonl", CJ), eng_decl(TR15)),
     "L1_17B_K0_2seed": mean2(arm(rows(CJ), eng_decl(CTt)), reuse(G + "c43/traces/gemma4-e2b-confirm-c43-K0-main-s42.traces.jsonl", [G + "c43/judgments/gemma4-e2b-confirm-c43-K0-main-s42-v01.judgments.jsonl"], ids57, [CJ])),
     "L2_GemmaE2B_desk_2seed": mean2(reuse(A + "gemma4-e2b/stage2/traces/gemma4-e2b-eng-K0-main-s42.traces.jsonl", [A + "gemma4-e2b/stage2/judgments/gemma4-e2b-eng-K0-main-s42-v01.judgments.jsonl"], ids57, [CJ]),
                                     reuse(G + "g43/traces/gemma4-e2b-confirm-g43-K0-main-s42.traces.jsonl", [G + "g43/judgments/gemma4-e2b-confirm-g43-K0-main-s42-v01.judgments.jsonl"], ids57, [CJ])),
     "L3_4B_phone_cut7": arm(rows(RR + "device-pixel8a/final-cut7-v01/judgments.haiku.jsonl"))}
det6 = json.load(open(F + "aggregates/floor.json"))["nonmodel_path_items"]
def block(S, ids, pairs):
    n = len(ids); dr = draws(n); res = {"n": n, "levels": {}, "pairs": {}}
    M = {k: {m: levels(S[k], ids, m) for m in ("full", "cu", "z")} for k in S}
    pt = {k: {m: float(Uf(*M[k][m])) for m in M[k]} for k in S}; bs = {k: {m: np.array([Uf(M[k][m][0][ii], M[k][m][1][ii]) for ii in dr]) for m in M[k]} for k in S}
    for k in S: res["levels"][k] = {m: dict(U=round(pt[k][m], 4), ci=ci(bs[k][m])) for m in ("full", "cu", "z")} | {"U_sub": round((pt[k]["full"] - SUB) / (1 - SUB), 4)}
    for a, b in pairs:
        r = {}
        for m in ("full", "cu", "z"):
            d = pt[a][m] - pt[b][m]; db = bs[a][m] - bs[b][m]; lo = float(np.percentile(db, 2.5))
            r[m] = dict(dU=round(d, 4), ci=ci(db), separable=bool(d >= 0.05 and lo > 0))
        mv = (bs[a]["cu"] - bs[b]["cu"]) - (bs[a]["full"] - bs[b]["full"])
        r["move_cu_minus_full"] = round(r["cu"]["dU"] - r["full"]["dU"], 4); r["move_ci"] = ci(mv); r["move_ok"] = abs(r["move_cu_minus_full"]) < 0.03
        r["move_z_minus_full"] = round(r["z"]["dU"] - r["full"]["dU"], 4)
        res["pairs"][f"{a} - {b}"] = r
    for m in ("full", "cu", "z"): res[f"rank_{m}"] = sorted(S, key=lambda k: pt[k][m])
    res["rank_same_cu"] = res["rank_cu"] == res["rank_full"]; res["rank_same_z"] = res["rank_z"] == res["rank_full"]
    res["spearman_item"] = {}
    for k in S:
        f = np.array([S[k][q]["full"][0] for q in ids]); c = np.array([S[k][q]["cu"][0] for q in ids])
        rk = lambda x: np.argsort(np.argsort(x, kind="stable"), kind="stable").astype(float)
        def avg_rank(x):
            o = np.argsort(x, kind="stable"); rr = np.empty(len(x)); i = 0
            while i < len(x):
                j = i
                while j + 1 < len(x) and x[o[j + 1]] == x[o[i]]: j += 1
                rr[o[i:j + 1]] = (i + j) / 2; i = j + 1
            return rr
        res["spearman_item"][k] = round(float(np.corrcoef(avg_rank(f), avg_rank(c))[0, 1]), 4)
    return res
K = list(L); LP_ = [(K[i], K[j]) for i in range(4) for j in range(i)][::-1]
LP_ = [(K[1], K[0]), (K[2], K[1]), (K[3], K[2]), (K[2], K[0]), (K[3], K[1]), (K[3], K[0])]
ids51 = [q for q in ids57 if q not in det6 and all(q in L[k] for k in L)]
out["4_ladder51"] = block(L, ids51, LP_)
out["4_ladder57_sens"] = block(L, [q for q in ids57 if all(q in L[k] for k in L)], LP_)
# MAIN 97 K0 s42
T4 = A + "gemma4-e2b-vs4b/traces/gemma4-e2b-vs4b-K0-main-s42.traces.jsonl"; TG = A + "gemma4-e2b/stage2/traces/gemma4-e2b-eng-K0-main-s42.traces.jsonl"
ids97 = sorted(REP[0])
M97 = {"q42_17B": arm(rows(*CJall), eng_decl(CTt)),
       "g42_Gemma": reuse(TG, sorted(glob.glob(A + "gemma4-e2b/stage2/judgments/gemma4-e2b-eng-K0-main-s42-*.judgments.jsonl")), ids97, CJall),
       "b42_4B": reuse(T4, sorted(glob.glob(A + "gemma4-e2b-vs4b/judgments/gemma4-e2b-vs4b-K0-main-s42-*.judgments.jsonl")), ids97, CJall)}
mp = [("b42_4B", "q42_17B"), ("g42_Gemma", "q42_17B"), ("b42_4B", "g42_Gemma")]
ids97 = [q for q in ids97 if all(q in M97[k] for k in M97)]
out["4_main97"] = block(M97, ids97, mp)
out["4_main97_no_det_sens"] = block(M97, [q for q in ids97 if q not in det], mp)
out["4_engine_declines_main97"] = {k: sum(1 for q in ids97 if abs(M97[k][q]["z"][0] - M97[k][q]["full"][0]) > 1e-9) for k in M97}
gp = list(out["4_ladder51"]["pairs"].values()) + list(out["4_main97"]["pairs"].values())
out["4_pass"] = all(p["move_ok"] for p in gp) and out["4_ladder51"]["rank_same_cu"] and out["4_main97"]["rank_same_cu"]
out["4_max_abs_move"] = max(abs(p["move_cu_minus_full"]) for p in gp)
out["4_separability_changes"] = {k: [v["full"]["separable"], v["cu"]["separable"]] for blk in ("4_ladder51", "4_main97") for k, v in out[blk]["pairs"].items() if v["full"]["separable"] != v["cu"]["separable"]}
sp = {**out["4_ladder51"]["spearman_item"], **{f"main97:{k}": v for k, v in out["4_main97"]["spearman_item"].items()}}
out["5_spearman"] = dict(per_arm=sp, min=min(sp.values()), ok=min(sp.values()) >= 0.85)
# ---- 6. Opus family check (CE-OPUS-RU 38)
OJ = rows(*glob.glob(A + "refuse-unsupported/ce-opus-ru/out/*.judgments.jsonl")); O = arm(OJ); oi = sorted(O)
f = np.array([O[q]["full"][0] for q in oi]); c = np.array([O[q]["cu"][0] for q in oi])
def avg_rank(x):
    o = np.argsort(x, kind="stable"); rr = np.empty(len(x)); i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[o[j + 1]] == x[o[i]]: j += 1
        rr[o[i:j + 1]] = (i + j) / 2; i = j + 1
    return rr
out["6_opus_ceopusru"] = dict(n=len(oi), U_full=ustat(O, oi, "full"), U_cu=ustat(O, oi, "cu"), spearman=round(float(np.corrcoef(avg_rank(f), avg_rank(c))[0, 1]), 4),
    ce=sum(O[q]["corr"] <= 1.5 for q in oi), cu_proxy_le15=sum(O[q]["cu"][0] <= 1.5 for q in oi), ce_and_proxy=sum(O[q]["corr"] <= 1.5 and O[q]["cu"][0] <= 1.5 for q in oi),
    mean_cu_on_ce=round(float(np.mean([O[q]["cu"][0] for q in oi if O[q]["corr"] <= 1.5] or [0])), 3), mean_cu_on_correct=round(float(np.mean([O[q]["cu"][0] for q in oi if O[q]["corr"] >= 4] or [0])), 3))
# ---- CE visibility under U_CU (diagnostic, MAIN 97 q42 rep1): mean n by CE label
q = M97["q42_17B"]; out["diag_ce_visibility_q42"] = {lab: dict(n=len(ii), n_full=round(st.mean(n_(q[i]["full"][0]) for i in ii), 3), n_cu=round(st.mean(n_(q[i]["cu"][0]) for i in ii), 3))
    for lab, ii in (("CE", [i for i in ids97 if q[i]["corr"] <= 1.5]), ("partial", [i for i in ids97 if 1.5 < q[i]["corr"] < 4]), ("correct", [i for i in ids97 if q[i]["corr"] >= 4]))}
# ---- verdict
chk = dict(decline_cu=out["1_pass"]["cu"], consistency=out["2_consistency40"]["ok"], retest=out["3_retest20"]["ok"], gaps_ranks=out["4_pass"], spearman=out["5_spearman"]["ok"])
out["checks_cu"] = chk; out["verdict_cu"] = "ADOPT" if all(chk.values()) else "NO-ADOPT"
zg = all(abs(p["move_z_minus_full"]) < 0.03 for p in gp) and out["4_ladder51"]["rank_same_z"] and out["4_main97"]["rank_same_z"]
out["checks_z"] = dict(decline_z=out["1_pass"]["z"], gaps_ranks=zg); out["verdict_z"] = "ADOPT" if all(out["checks_z"].values()) else "NO-ADOPT"
js = json.dumps(out, indent=1); open(sys.argv[1], "w").write(js + "\n"); print(js)
