#!/usr/bin/env python3
"""CE-OPUS-RU analysis (0 calls). python3 -I analyze.py [--haiku-only]
Runs the frozen RU analysis code (../../tools/analyze.py, unchanged, imported) with one substitution: for the CE-OPUS-RU set (in/set.json union),
the judge values (s, sref, corr) come from the Opus judge.v1 judgments in out/*.judgments.jsonl (both orders required) instead of the Haiku ones.
Items outside the set keep their Haiku values (not re-judged). Gate scores and Haiku support labels are unchanged.
--haiku-only: no substitution (sanity: must reproduce RU's 10 -> 4 and 0/15).
Clauses (pooled 177, t = 0.919): (a) ceu_C >= 6 AND ceu_R <= ceu_C / 2; (b) fr_k == 0. Exact (Clopper-Pearson) 95 % CIs on counts."""
import json, sys, glob, io, contextlib, importlib.util, math
A = "<workspace>/rnd/research/coordinator/arms"; H = f"{A}/refuse-unsupported"; C = f"{H}/ce-opus-ru"
spec = importlib.util.spec_from_file_location("ru", f"{H}/tools/analyze.py"); ru = importlib.util.module_from_spec(spec); spec.loader.exec_module(ru)
S = json.load(open(f"{C}/in/set.json")); U = S["union"]; HO = "--haiku-only" in sys.argv


def opus():
    by = {}
    for f in glob.glob(f"{C}/out/*.judgments.jsonl"):
        for r in ru.rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    out = {}
    for q, v in by.items():
        if len(v) != 2: continue
        ms = list(v.values()); mean = lambda d: sum(d.values()) / 3
        out[q] = dict(s=sum(mean(m["boar"]) for m in ms) / 2, sref=sum(mean(m["ref"]) for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2)
    return out


def cp(k, n, a=0.05):
    def bcdf(k, n, p): return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))
    def solve(f, lo=0.0, hi=1.0):
        for _ in range(100):
            m = (lo + hi) / 2
            if f(m): lo = m
            else: hi = m
        return (lo + hi) / 2
    lo = 0.0 if k == 0 else solve(lambda p: 1 - bcdf(k - 1, n, p) < a / 2)
    hi = 1.0 if k == n else solve(lambda p: bcdf(k, n, p) > a / 2)
    return [round(lo, 4), round(hi, 4)]


HJ0, HJ3 = ru.judg("K0"), ru.judg("K3"); T3, T0 = ru.traces("K3"), ru.traces("K0")
hai = {k: (HJ0[k] if T3[k]["answer"]["text"] == T0[k]["answer"]["text"] else HJ3[k]) for k in U}
OP = {} if HO else opus()
miss = [k for k in U if k not in OP]
if not HO and miss: sys.exit(f"Opus judgments missing (both orders) for {len(miss)}: {miss}")
orig = ru.judg
def judg(arm):
    d = dict(orig(arm))
    for k, v in OP.items():
        if k in U: d[k] = v
    return d
ru.judg = judg
tag = "haiku" if HO else "opus"; outp = f"{C}/analysis-{tag}.json"
sys.argv = ["analyze.py", f"{H}/gate/items.json", f"{H}/gate/boar.outputs.jsonl", f"{H}/labels/labels.jsonl", outp]
buf = io.StringIO()
with contextlib.redirect_stdout(buf): ru.main()
res = json.load(open(outp)); p = res["thresholds"]["0.919"]["pooled"]; n = p["n"]
rows = {r["key"]: r for r in res["rows"]}
cl_a = p["ceu_C"] >= 6 and p["ceu_R"] <= p["ceu_C"] / 2; cl_b = p["fr_k"] == 0
rep = dict(labels=tag, n=n, ceu_C=p["ceu_C"], ceu_C_cp=cp(p["ceu_C"], n), ceu_R=p["ceu_R"], ceu_R_cp=cp(p["ceu_R"], n),
           rel_drop=p["rel_drop"], ceu_diff_boot_ci=p["ceu_diff_ci"], removed_by_gate=p["ceu_C"] - p["ceu_R"],
           sign_test_p_one_sided=0.5 ** (p["ceu_C"] - p["ceu_R"]) if p["ceu_C"] > p["ceu_R"] else 1.0,
           fr_k=p["fr_k"], fr_n=p["fr_n"], fr_cp=cp(p["fr_k"], p["fr_n"]) if p["fr_n"] else None,
           refused_by_gate=p["refused_by_gate"], refused_corr_ge4=p["refused_by_gate_correct"], U_C=p["U_C"], U_R=p["U_R"],
           cov_C=p["cov_C"], cov_R=p["cov_R"], ru_rule_verdict_t0919=res["thresholds"]["0.919"]["verdict"],
           t05=dict(ceu_C=res["thresholds"]["0.5"]["pooled"]["ceu_C"], ceu_R=res["thresholds"]["0.5"]["pooled"]["ceu_R"], fr=f'{res["thresholds"]["0.5"]["pooled"]["fr_k"]}/{res["thresholds"]["0.5"]["pooled"]["fr_n"]}'),
           by_set={s: dict(ceu_C=res["thresholds"]["0.919"][s]["ceu_C"], ceu_R=res["thresholds"]["0.919"][s]["ceu_R"], fr=f'{res["thresholds"]["0.919"][s]["fr_k"]}/{res["thresholds"]["0.919"][s]["fr_n"]}') for s in ("MAIN", "CAND")},
           clause_a=cl_a, clause_b=cl_b, verdict="PASS" if cl_a and cl_b else "FAIL (kill rule)",
           hon3_secondary=dict(ceu_C_ge7=p["ceu_C"] >= 7, rel_drop_ge40=(p["rel_drop"] or 0) >= 0.40),
           ce_unwarned_C=sorted(k for k, r in rows.items() if r["shownC"] and r["corr"] <= 1.5),
           ce_unwarned_R=sorted(k for k, r in rows.items() if r["shownC"] and r["corr"] <= 1.5 and not (r["gated"] and r["s_gate"] >= 0.919)))
if not HO:
    ag = [(k, hai[k]["corr"] <= 1.5, OP[k]["corr"] <= 1.5) for k in U]
    a = sum(h == o for _, h, o in ag); m = len(ag); ph = sum(h for _, h, _ in ag) / m; po = sum(o for *_, o in ag) / m; pe = ph * po + (1 - ph) * (1 - po)
    rep["agreement"] = dict(n=m, agree=a, agree_cp=cp(a, m), kappa=round((a / m - pe) / (1 - pe), 3) if pe < 1 else None, haiku_CE=sum(h for _, h, _ in ag),
                            opus_CE=sum(o for *_, o in ag), haiku_only=[k for k, h, o in ag if h and not o], opus_only=[k for k, h, o in ag if o and not h],
                            corr_MAE=round(sum(abs(hai[k]["corr"] - OP[k]["corr"]) for k in U) / m, 3),
                            mean_opus_minus_haiku=round(sum(OP[k]["corr"] - hai[k]["corr"] for k in U) / m, 3))
    rep["per_item"] = {k: dict(haiku=hai[k]["corr"], opus=OP[k]["corr"], groups=[g for g in ("control_ce_unwarned", "gate_refused", "supported_correct", "ce_unwarned_still_shown_R") if k in S[g]]) for k in U}
json.dump(rep, open(f"{C}/ceopusru-{tag}.json", "w"), indent=1)
print(json.dumps({k: v for k, v in rep.items() if k != "per_item"}, indent=1))
