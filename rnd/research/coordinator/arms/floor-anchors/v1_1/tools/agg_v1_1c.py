#!/usr/bin/env python3
"""JUDGE-V1_1 aggregation (0 LLM; rules of ../JUDGE-V1_1-criterion.md). Usage: python3 -I agg_v1_1.py <W1|W2|W3>  -> aggregates/<W>.json
Validity: floor_agg estimator (U = sum(s-1)/sum(r-1), CI 2.5/97.5 of 2000 item bootstraps, default_rng(11)) per decline variant; VALID iff every U_ci high <= 0.05.
Consistency: n = (s-1)/4 per item (s = mean over both orders of the mean of the 3 dims). v1 reference = mean n over the 3 existing v1 repeats; CE v1 = majority
(>= 2 of 3) of correctness-avg <= 1.5; CE v1.1 = correctness-avg <= 1.5 (one judgment). PASS iff mean |n_v11 - n_v1| <= 0.05 AND CE flips <= 2.
Test-retest: mean over the retest ids of the sample SD (ddof 1) of n over the two v1.1 judgments (controls + retest) <= V1_SD (v1 repeats 1-2, same ids)."""
import json, glob, sys, os, statistics as st, collections, numpy as np
V = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); H = os.path.dirname(V); A = os.path.dirname(H)
W = sys.argv[1]; V1_SD = 0.0206; K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
def load(paths):
    J = collections.defaultdict(dict)
    for p in paths:
        for l in open(p):
            r = json.loads(l)
            if r.get("ok") and r["order"] not in J[r["queryId"]]: J[r["queryId"]][r["order"]] = r["mapped"]
    out = {}
    for q, v in J.items():
        if set(v) != {"boarA", "boarB"}: continue
        a, b = v["boarA"], v["boarB"]; s = (mr(a["boar"]) + mr(b["boar"])) / 2
        out[q] = dict(s=s, r=(mr(a["ref"]) + mr(b["ref"])) / 2, n=(s - 1) / 4, corr=(a["boar"]["correctness"] + b["boar"]["correctness"]) / 2,
                      dims={k: (a["boar"][k] + b["boar"][k]) / 2 for k in K}, w=a["winner"] if a["winner"] == b["winner"] else "tie")
    return out
ci = lambda x: [round(float(v), 4) for v in np.percentile(x, [2.5, 97.5])]
def Ustat(d, ids):
    S = np.array([d[q]["s"] for q in ids]); R = np.array([d[q]["r"] for q in ids]); f = lambda ii: (S[ii] - 1).sum() / (R[ii] - 1).sum()
    rng = np.random.default_rng(11); b = [f(rng.integers(0, len(ids), len(ids))) for _ in range(2000)]
    return round(float(f(np.arange(len(ids)))), 4), ci(b)
res = {"wording": W, "criterion_sha256": open(f"{H}/JUDGE-V1_1B-criterion.sha256").read().split()[0]}
ids30 = open(f"{H}/decline-30.ids").read().split(); val = {}
for v in "abc":
    p = f"{V}/judgments/{W}-decline-{v}.judgments.jsonl"
    if not os.path.exists(p): continue
    d = load([p]); ids = [q for q in ids30 if q in d]; U, Uci = Ustat(d, ids)
    w = collections.Counter(d[q]["w"] for q in ids)
    val[v] = dict(n=len(ids), U=U, U_ci=Uci, raw=round(sum(d[q]["s"] for q in ids) / sum(d[q]["r"] for q in ids), 3), wtl=[w["boar"], w["tie"], w["ref"]],
                  mean_dims={k: round(float(np.mean([d[q]["dims"][k] for q in ids])), 3) for k in K}, items_s_gt_1=sum(d[q]["s"] > 1 for q in ids),
                  nonzero=sorted([(q, round(d[q]["s"], 3)) for q in ids if d[q]["s"] > 1], key=lambda x: -x[1]), ok=Uci[1] <= 0.05)
res["validity"] = val; res["validity_pass"] = len(val) == 3 and all(x["ok"] for x in val.values())
# v1 reference (3 existing repeats)
C = f"{A}/lp-screens/control/judgments"; J2 = f"{A}/judge-v2/v1"
R = [load(sorted(glob.glob(f"{C}/lpctl-K0-main-s42-*.judgments.jsonl")))] + [load(sorted(glob.glob(f"{J2}/rep{r}-*.judgments.jsonl"))) for r in (2, 3)]
grp = {l.split("\t")[0]: l.split("\t")[2].strip() for l in open(f"{V}/data/controls-40.tsv")}
c11 = load(sorted(glob.glob(f"{V}/judgments/{W}-ctl-*.judgments.jsonl")))
if c11:
    ids = [q for q in grp if q in c11]
    nv1 = {q: st.mean(Rr[q]["n"] for Rr in R) for q in ids}; cev1 = {q: sum(Rr[q]["corr"] <= 1.5 for Rr in R) >= 2 for q in ids}
    ce11 = {q: c11[q]["corr"] <= 1.5 for q in ids}; flips = [q for q in ids if ce11[q] != cev1[q]]
    mad = st.mean(abs(c11[q]["n"] - nv1[q]) for q in ids)
    ctx_v1_flips = [sum((Rr[q]["corr"] <= 1.5) != cev1[q] for q in ids) for Rr in R]
    ctx_v1_mad = [round(st.mean(abs(Rr[q]["n"] - nv1[q]) for q in ids), 4) for Rr in R]
    res["consistency"] = dict(n=len(ids), mad=round(mad, 4), ce_flips=flips, n_flips=len(flips),
        mad_by_group={g: round(st.mean(abs(c11[q]["n"] - nv1[q]) for q in ids if grp[q] == g), 4) for g in ("correct", "wrong")},
        mean_n_v1=round(st.mean(nv1.values()), 4), mean_n_v11=round(st.mean(c11[q]["n"] for q in ids), 4),
        signed_mean_diff=round(st.mean(c11[q]["n"] - nv1[q] for q in ids), 4),
        mean_corr_v1=round(st.mean(st.mean(Rr[q]["corr"] for Rr in R) for q in ids), 3), mean_corr_v11=round(st.mean(c11[q]["corr"] for q in ids), 3),
        U_v1_rep1=Ustat(R[0], ids), U_v11=Ustat(c11, ids),
        context_v1_single_repeat_vs_majority_flips=ctx_v1_flips, context_v1_single_repeat_vs_mean_mad=ctx_v1_mad,
        moved_items=sorted([(q, grp[q], round(nv1[q], 3), round(c11[q]["n"], 3)) for q in ids if abs(c11[q]["n"] - nv1[q]) > 0.1], key=lambda x: x[0]),
        ok=mad <= 0.05 and len(flips) <= (2 if W in ("W1", "W3") else 1))  # W2 = 20 items (cap): flips <= 1
rt = load(sorted(glob.glob(f"{V}/judgments/{W}-rt-*.judgments.jsonl")))
if rt and c11:
    ids = [q for q in open(f"{V}/data/retest-20.ids").read().split() if q in rt and q in c11]
    sd = st.mean(st.stdev([c11[q]["n"], rt[q]["n"]]) for q in ids)
    res["retest"] = dict(n=len(ids), mean_item_sd=round(sd, 4), need=V1_SD, exact_same=sum(abs(c11[q]["s"] - rt[q]["s"]) < 1e-9 for q in ids),
                         ce_same=sum((c11[q]["corr"] <= 1.5) == (rt[q]["corr"] <= 1.5) for q in ids), context_v1_full97_sd=0.0286, ok=sd <= V1_SD)
parts = [res["validity_pass"], res.get("consistency", {}).get("ok")] + ([res.get("retest", {}).get("ok")] if W in ("W1", "W3") else [])  # W2: no retest (cap)
res["verdict"] = ("ADOPT" if all(parts) else "NO-ADOPT") if None not in parts else ("NO-ADOPT (validity failed)" if not res["validity_pass"] else "INCOMPLETE")
js = json.dumps(res, indent=1); print(js); os.makedirs(f"{V}/aggregates", exist_ok=True); open(f"{V}/aggregates/{W}.json", "w").write(js + "\n")
