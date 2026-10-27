#!/usr/bin/env python3
"""JUDGE-V2 analysis (0 LLM). Test-retest of judge.v1 (3 repeats) and judge.v2 (3 repeats) on the cached mini K0 MAIN control answers (n 97, dev),
v1-vs-v2 CE agreement, MDE for a paired U difference, and the frozen GO rule (JUDGEV2-criterion.md). Writes aggregates/judgev2.json and prints a summary.
Usage: python3 -I analyze.py [--examples N]
Definitions (frozen in the criterion):
- v1 item score per repeat: s1 = mean over both orders of the mean of the 3 boar dims (1-5); normalised n1 = (s1 - 1) / 4; CE1 = not declined and correctness
  averaged over both orders <= 1.5 (agg_run.py). v1 U_r = sum s1 / sum sref1 (pairwise reference scores of the same repeat).
- v2 item score per repeat: s2 = #PRESENT / K (in [0, 1]); CE2 = row.score.ce (judge-v2.mjs scoreRepeat). v2 U_r = sum s2 / sum s2(ref, repeat 1).
- Pairwise agreement = mean over the 3 repeat pairs of the share of items with equal label/score. Unanimity = share of items equal in all 3 repeats.
- Item-score SD = mean over items of the sample SD (ddof 1) of the normalised score over the 3 repeats.
- MDE (80 % power, two-sided alpha 0.05): two arms with identical answers, each judged once -> per-item difference variance 2 sigma_i^2 (sigma_i^2 = sample
  variance of the raw score over repeats); SE(dU) = sqrt(sum 2 sigma_i^2) / D (D = mean over repeats of the U denominator); MDE = 2.80 SE. Judge noise only;
  generation noise and true between-item variation of an arm effect are NOT included (they add to both judges alike). R = 3 aggregated: SE / sqrt(3) (approximation)."""
import json, glob, math, os, sys, itertools, hashlib, statistics as st
A = "<workspace>/rnd/research/coordinator/arms"; J = f"{A}/judge-v2"; C = f"{A}/lp-screens/control"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ids = open(f"{A}/lp-screens/main-97.ids").read().split()
T = {t["itemId"]: t for t in rd(f"{C}/traces/lpctl-K0-main-s42.traces.jsonl")}
items = {r["id"]: r for r in rd(f"{J}/data/items-dev97.jsonl")}
kp = {r["id"]: r for r in rd(f"{J}/data/kp-dev97.jsonl") if r.get("ok")}

def v1_rep(files):
    by = {}
    for f in files:
        for r in rd(f):
            if r.get("ok"): by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    out = {}
    for i in ids:
        ms = list(by[i].values()); assert len(ms) == 2, (i, files[0])
        mean = lambda x: sum(x.values()) / 3
        s = sum(mean(m["boar"]) for m in ms) / 2; sref = sum(mean(m["ref"]) for m in ms) / 2
        corr = sum(m["boar"]["correctness"] for m in ms) / 2; d = bool(T[i]["answer"].get("declined"))
        out[i] = dict(s=0.0 if d else s, raw=s, sref=sref, n=(s - 1) / 4, ce=(not d and corr <= 1.5), corr=corr)
    return out

V1 = [v1_rep(sorted(glob.glob(f"{C}/judgments/lpctl-K0-main-s42-*.judgments.jsonl")))]
for r in (2, 3): V1.append(v1_rep(sorted(glob.glob(f"{J}/v1/rep{r}-*.judgments.jsonl"))))

def v2_rep(f):
    rows = {r["id"]: r for r in rd(f) if r.get("ok")}
    assert all(i in rows for i in ids), (f, [i for i in ids if i not in rows])
    return {i: dict(s=rows[i]["score"]["s"] if not rows[i].get("overridden") else 0.0, n=rows[i]["score"]["s"] if not rows[i].get("overridden") else 0.0,
                    ce=rows[i]["score"]["ce"] if not rows[i].get("overridden") else False, row=rows[i]) for i in ids}
V2 = [v2_rep(f"{J}/v2/app-r{r}.jsonl") for r in (1, 2, 3)]
REF2 = {r["id"]: r for r in rd(f"{J}/v2/ref-r1.jsonl") if r.get("ok")}
for X in V2:
    for i in ids: X[i]["sref"] = REF2[i]["score"]["s"]

def fleiss(labels):  # labels: list over items of list of R category labels
    R = len(labels[0]); N = len(labels); cats = sorted({c for l in labels for c in l})
    P = [(sum(l.count(c) ** 2 for c in cats) - R) / (R * (R - 1)) for l in labels]
    p = [sum(l.count(c) for l in labels) / (N * R) for c in cats]; Pe = sum(x * x for x in p); Pb = sum(P) / N
    return float("nan") if Pe == 1 else (Pb - Pe) / (1 - Pe)
def kappa(a, b):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n; cats = set(a) | set(b)
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats); return float("nan") if pe == 1 else (po - pe) / (1 - pe)

def stats(REPS, name):
    pairs = list(itertools.combinations(range(len(REPS)), 2))
    pa = lambda key, tol=1e-9: sum(sum(abs(REPS[a][i][key] - REPS[b][i][key]) < tol if not isinstance(REPS[a][i][key], bool) else REPS[a][i][key] == REPS[b][i][key] for i in ids) / len(ids) for a, b in pairs) / len(pairs)
    un = lambda key: sum(len({round(float(R[i][key]), 9) for R in REPS}) == 1 for i in ids) / len(ids)
    sd = [st.stdev([R[i]["n"] for R in REPS]) for i in ids]; var_raw = [st.variance([R[i]["s"] for R in REPS]) for i in ids]
    U = [sum(R[i]["s"] for i in ids) / sum(R[i]["sref"] for i in ids) for R in REPS]; D = st.mean(sum(R[i]["sref"] for i in ids) for R in REPS)
    se = math.sqrt(sum(2 * v for v in var_raw)) / D
    return dict(judge=name, n=len(ids), repeats=len(REPS), ce_count_per_repeat=[sum(R[i]["ce"] for i in ids) for R in REPS],
                score_pairwise_exact=round(pa("s"), 4), score_unanimous=round(un("s"), 4),
                ce_pairwise_agreement=round(pa("ce"), 4), ce_unanimous=round(un("ce"), 4), ce_fleiss_kappa=round(fleiss([[R[i]["ce"] for R in REPS] for i in ids]), 4),
                item_score_sd_mean=round(st.mean(sd), 4), item_score_sd_median=round(st.median(sd), 4), items_sd_zero=sum(x == 0 for x in sd),
                U_per_repeat=[round(u, 4) for u in U], U_sd=round(st.stdev(U), 4), U_mean=round(st.mean(U), 4),
                mde_single=round(2.80 * se, 4), mde_single_rel=round(2.80 * se / st.mean(U), 4), mde_r3=round(2.80 * se / math.sqrt(3), 4),
                mde_r3_rel=round(2.80 * se / math.sqrt(3) / st.mean(U), 4))

s1, s2 = stats(V1, "judge.v1-low (Haiku 5.5, pairwise both orders, 1-5)"), stats(V2, "judge.v2 (Haiku 5.5-low, pointwise checklist)")
# v2 diagnostics
pf = [(i, k) for i in ids for k in range(len(V2[0][i]["row"]["verdicts"])) if len({R[i]["row"]["verdicts"][k] for R in V2}) > 1]
npts = sum(len(V2[0][i]["row"]["verdicts"]) for i in ids)
qf = [q for R in V2 for i in ids for q in R[i]["row"]["quoteFound"] if q is not None]
cls = {}
for R in V2:
    for i in ids: c = R[i]["row"]["judgment"]["answer_class"]; cls[c] = cls.get(c, 0) + 1
ffr = [sum(R[i]["row"]["score"]["ff"] for i in ids) for R in V2]
qd = sum(R[i]["row"]["quoteDowngrade"] for R in V2 for i in ids); nonabs = sum(sum(v != "ABSENT" for v in R[i]["row"]["verdictsRaw"]) for R in V2 for i in ids)
cm = sum(R[i]["row"]["classMismatch"] for R in V2 for i in ids)
imp = sum(bool(t) for i in ids for t in kp[i].get("imported", []))
contr = [sum(R[i]["row"]["score"]["contradicted"] > 0 for i in ids) for R in V2]
# aggregate (strict majority) v2 vs v1 majority CE
agg = {}
for i in ids:
    rows = [R[i]["row"] for R in V2]; Rn = 3; maj = lambda n: n > Rn / 2; K = len(rows[0]["verdicts"])
    v = []
    for k in range(K):
        c = next((c for c in ("PRESENT", "CONTRADICTED") if maj(sum(r["verdicts"][k] == c for r in rows))), "ABSENT"); v.append(c)
    ff = maj(sum(r["score"]["ff"] for r in rows))
    agg[i] = dict(s=v.count("PRESENT") / K, ce=("CONTRADICTED" in v) and not T[i]["answer"].get("declined"), ff=ff, verdicts=v)
v1maj = {i: sum(R[i]["ce"] for R in V1) >= 2 for i in ids}
tab = {f"v1{a}_v2{b}": sum(v1maj[i] == a and agg[i]["ce"] == b for i in ids) for a in (True, False) for b in (True, False)}
cross = dict(table=tab, agreement=round(sum(v1maj[i] == agg[i]["ce"] for i in ids) / len(ids), 4),
             kappa=round(kappa([v1maj[i] for i in ids], [agg[i]["ce"] for i in ids]), 4),
             v1_majority_ce=sum(v1maj.values()), v2_aggregate_ce=sum(a["ce"] for a in agg.values()))
# verbosity diagnostic: Spearman(answer length, score) per judge (repeat-mean scores)
def spearman(x, y):
    rk = lambda v: [sorted(v).index(a) + (sorted(v).count(a) - 1) / 2 for a in v]; a, b = rk(x), rk(y)
    ma, mb = st.mean(a), st.mean(b); num = sum((p - ma) * (q - mb) for p, q in zip(a, b))
    return num / math.sqrt(sum((p - ma) ** 2 for p in a) * sum((q - mb) ** 2 for q in b))
L = [V2[0][i]["row"]["answerChars"] for i in ids]
verb = dict(spearman_len_v1=round(spearman(L, [st.mean(R[i]["n"] for R in V1) for i in ids]), 3), spearman_len_v2=round(spearman(L, [st.mean(R[i]["n"] for R in V2) for i in ids]), 3))
diag = dict(point_flip_rate=round(len(pf) / npts, 4), points=npts, mean_K=round(npts / len(ids), 2), R_rule="R = 3 if point flip rate <= 0.10 else 5 (RULER-SPEC §6)",
            quote_found_rate=round(sum(qf) / len(qf), 4) if qf else None, quote_downgrades=qd, non_absent_raw_verdicts=nonabs, class_mismatch_rows=cm,
            kp_points_with_imported_terms=imp, ff_aggregate_items=sum(a["ff"] for a in agg.values()), answer_class_counts=cls, false_fact_items_per_repeat=ffr, contradicted_items_per_repeat=contr,
            ce_prevalence_v2=round(st.mean(s2["ce_count_per_repeat"]) / len(ids), 4), ref_mean_s=round(st.mean(REF2[i]["score"]["s"] for i in ids), 4),
            ref_items_s0=sum(REF2[i]["score"]["s"] == 0 for i in ids), v2_aggregate_U=round(sum(agg[i]["s"] for i in ids) / sum(REF2[i]["score"]["s"] for i in ids), 4))
# GO rule (frozen)
c1 = s2["ce_pairwise_agreement"] >= s1["ce_pairwise_agreement"] + 0.05
c2 = s2["item_score_sd_mean"] <= 0.6 * s1["item_score_sd_mean"]
sanity = diag["ce_prevalence_v2"] >= 0.05
verdict = "GO" if (c1 and c2 and sanity) else ("VOID (v2 CE prevalence < 5 %: agreement degenerate)" if not sanity else "NO-GO")
res = dict(v1=s1, v2=s2, cross_ce=cross, v2_diagnostics=diag, verbosity=verb,
           go=dict(ce_agreement_clause=dict(v2=s2["ce_pairwise_agreement"], v1=s1["ce_pairwise_agreement"], need=round(s1["ce_pairwise_agreement"] + 0.05, 4), ok=c1),
                   sd_clause=dict(v2=s2["item_score_sd_mean"], v1=s1["item_score_sd_mean"], need=round(0.6 * s1["item_score_sd_mean"], 4), ok=c2),
                   sanity_ce_prevalence=dict(v2=diag["ce_prevalence_v2"], need=0.05, ok=sanity), verdict=verdict))
# disagreement examples (v1 majority CE != v2 aggregate CE), deterministic order by sha256(id)
dis = sorted([i for i in ids if v1maj[i] != agg[i]["ce"]], key=lambda i: hashlib.sha256(i.encode()).hexdigest())
ex = []
for i in dis:
    r1 = V2[0][i]["row"]
    ex.append(dict(id=i, answer=T[i]["answer"]["text"][:700], v1_corr_per_repeat=[R[i]["corr"] for R in V1], v1_ce=[R[i]["ce"] for R in V1],
                   v2_ce=[R[i]["ce"] for R in V2], v2_s=[R[i]["s"] for R in V2], key_points=kp[i]["points"], v2_majority_verdicts=agg[i]["verdicts"],
                   v2_false_facts=[R[i]["row"]["judgment"]["false_facts"] for R in V2], v2_evidence=V2[0][i]["row"]["evidence"], v2_verdicts_per_repeat=[R[i]["row"]["verdicts"] for R in V2], v2_class=[R[i]["row"]["judgment"]["answer_class"] for R in V2]))
res["disagreements"] = ex
os.makedirs(f"{J}/aggregates", exist_ok=True); json.dump(res, open(f"{J}/aggregates/judgev2.json", "w"), indent=1, ensure_ascii=False)
for k in ("v1", "v2"): print(k, json.dumps(res[k]))
print("cross", json.dumps(cross)); print("diag", json.dumps(diag)); print("verbosity", json.dumps(verb)); print("GO", json.dumps(res["go"])); print("disagreements", len(dis), dis)
