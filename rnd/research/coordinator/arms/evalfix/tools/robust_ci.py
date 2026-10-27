"""EVALFIX parts 2+3: robust CIs side by side + power numbers. python3 -I robust_ci.py -> aggregates/robust_ci.json, aggregates/power.json
Reads existing judgment rows only (0 judge calls); prints/stores numbers and ids only.
Per item: boar_i / ref_i = rubric mean (3 criteria) averaged over the two orders (combineOrders averaging) and over seeds.
Headline estimand R = sum(boar)/sum(ref) (ratio of sums, as judge-core/paired.mjs). Intervals:
 (a) existing percentile / stratified two-level bootstrap: CITED from aggregates (not recomputed).
 (b) logit-t: per-item ratio b_i/r_i clipped to [0.02,0.98], logit, t-interval, back-transform. Level: CI of the MEAN per-item ratio (different
     estimand from R, point shown). Delta: t-interval on the paired logit differences theta, mapped as expit(logit(mB)+theta)-mB.
 (c) paired t on delta-method influence values u_i=(b_i-R r_i)/mean(r); delta v_i=uA_i-uB_i; plain paired t (Bonett 2006 correction not applied:
     it is for variances/binary contrasts, not available in closed form for this ratio-of-sums statistic)."""
import json, math, os
B = "<private held-out dir>"; VP = B + "V-para/"; V2 = B + "bench-v02/"
IDS = {"vpara": VP + "runs-cut6/judged.ids", "v02": V2 + "runs-deepvpara/judged.ids"}
F = {
 "H": {"vpara": [VP+"runs-dt512/dh-H-vpara-s42.judgments.jsonl", VP+"runs-dt512/dh-H-vpara-s43.judgments.jsonl"],
       "v02": [V2+"runs-dt512v02/dhv-H-v02-s42.judgments.jsonl"]},
 "H3": {"vpara": [VP+"runs-dt512/dh-H-vpara-s4%d.judgments.jsonl" % i for i in (2, 3, 4)]},
 "T": {"vpara": [VP+"runs-deepthink/dt-T-vpara-s42.judgments.jsonl", VP+"runs-deepthink/dt-T-vpara-s43.judgments.jsonl"]},
 "D": {"vpara": [VP+"runs-deepvpara/dv-D-vpara-s42.judgments.jsonl", VP+"runs-deepvpara/dv-D-vpara-s43.judgments.jsonl"]},
 "Q": {"vpara": [VP+"runs-quantceil/qc-Q-vpara-s42.judgments.jsonl", VP+"runs-quantceil/qc-Q-vpara-s43.judgments.jsonl"],
       "v02": [V2+"runs-quantceil/qc-Q-v02-s42.judgments.jsonl"]},
 "K": {"vpara": [VP+"runs-cut6/cut6-vpara-s42.judgments.jsonl", VP+"runs-cut6/cut6-vpara-s43.judgments.jsonl"],
       "v02": [V2+"runs-cut6/cut6-v02-s42.judgments.jsonl", V2+"runs-cut6/cut6-v02-s43.judgments.jsonl"]},
}
KEYS = ("correctness", "completeness", "usefulness")
def load(path, want):
    by = {}
    for l in open(path):
        if not l.strip(): continue
        r = json.loads(l)
        if r.get("ok") and r["queryId"] in want:
            m = r["mapped"]; by.setdefault(r["queryId"], {})[r["order"]] = (sum(m["boar"][k] for k in KEYS)/3, sum(m["ref"][k] for k in KEYS)/3)
    return {i: ((o["boarA"][0]+o["boarB"][0])/2, (o["boarA"][1]+o["boarB"][1])/2) for i, o in by.items() if len(o) == 2}
def arm(label, ds):  # -> {id: (b, r)} averaged over seeds; only ids present in every seed
    want = set(x for x in open(IDS[ds]).read().split("\n") if x)
    S = [load(p, want) for p in F[label][ds]]
    ids = sorted(set.intersection(*[set(s) for s in S]))
    return {i: (sum(s[i][0] for s in S)/len(S), sum(s[i][1] for s in S)/len(S)) for i in ids}, S
# ---- stats helpers (stdlib)
def betacf(a, b, x):
    qab, qap, qam = a+b, a+1, a-1; c = 1.0; d = 1-qab*x/qap; d = 1/(d if abs(d) > 1e-300 else 1e-300); h = d
    for m in range(1, 300):
        m2 = 2*m; aa = m*(b-m)*x/((qam+m2)*(a+m2)); d = 1+aa*d; d = d if abs(d) > 1e-300 else 1e-300; c = 1+aa/c; c = c if abs(c) > 1e-300 else 1e-300; d = 1/d; h *= d*c
        aa = -(a+m)*(qab+m)*x/((a+m2)*(qap+m2)); d = 1+aa*d; d = d if abs(d) > 1e-300 else 1e-300; c = 1+aa/c; c = c if abs(c) > 1e-300 else 1e-300; d = 1/d; de = d*c; h *= de
        if abs(de-1) < 3e-14: break
    return h
def ibeta(a, b, x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    bt = math.exp(math.lgamma(a+b)-math.lgamma(a)-math.lgamma(b)+a*math.log(x)+b*math.log(1-x))
    return bt*betacf(a, b, x)/a if x < (a+1)/(a+b+2) else 1-bt*betacf(b, a, 1-x)/b
def tcdf(t, df):
    p = 0.5*ibeta(df/2, 0.5, df/(df+t*t)); return 1-p if t > 0 else p
def tq(p, df):
    lo, hi = 0.0, 50.0
    for _ in range(80):
        mid = (lo+hi)/2
        if tcdf(mid, df) < p: lo = mid
        else: hi = mid
    return (lo+hi)/2
def mean(x): return sum(x)/len(x)
def sd(x): m = mean(x); return math.sqrt(sum((v-m)**2 for v in x)/(len(x)-1))
def tci(x, level=0.95):
    n = len(x); h = tq(1-(1-level)/2, n-1)*sd(x)/math.sqrt(n); return mean(x), mean(x)-h, mean(x)+h
logit = lambda p: math.log(p/(1-p)); expit = lambda z: 1/(1+math.exp(-z)); clip = lambda p: min(0.98, max(0.02, p))
def R(A, ids): return sum(A[i][0] for i in ids)/sum(A[i][1] for i in ids)
def infl(A, ids):
    r = R(A, ids); rb = mean([A[i][1] for i in ids]); return [(A[i][0]-r*A[i][1])/rb for i in ids]
def level_row(A):
    ids = sorted(A); u = infl(A, ids); r = R(A, ids); se = sd(u)/math.sqrt(len(ids)); h = tq(0.975, len(ids)-1)*se
    L = [logit(clip(A[i][0]/A[i][1])) for i in ids]; m, lo, hi = tci(L)
    return {"n": len(ids), "R": round(r, 4), "c_delta_t": [round(r-h, 4), round(r+h, 4)],
            "b_logit_t_meanratio": [round(expit(m), 4), round(expit(lo), 4), round(expit(hi), 4)],
            "mean_item_ratio_unclipped": round(mean([A[i][0]/A[i][1] for i in ids]), 4), "item_sd_u": round(sd(u), 4)}
def delta_row(A, Bm):
    ids = sorted(set(A) & set(Bm)); n = len(ids)
    v = [a-b for a, b in zip(infl(A, ids), infl(Bm, ids))]; d = R(A, ids)-R(Bm, ids); h = tq(0.975, n-1)*sd(v)/math.sqrt(n)
    th = [logit(clip(A[i][0]/A[i][1]))-logit(clip(Bm[i][0]/Bm[i][1])) for i in ids]; tm, tlo, thi = tci(th)
    mB = mean([clip(Bm[i][0]/Bm[i][1]) for i in ids]); f = lambda z: expit(logit(mB)+z)-mB
    return {"n": n, "delta": round(d, 4), "c_paired_t": [round(d-h, 4), round(d+h, 4)], "b_logit_t": [round(f(tm), 4), round(f(tlo), 4), round(f(thi), 4)],
            "s_d_linearized": round(sd(v), 4), "s_d_item_ratio_diff": round(sd([A[i][0]/A[i][1]-Bm[i][0]/Bm[i][1] for i in ids]), 4)}
CITED = {  # (a) from existing aggregates, raw-ratio scale
 "DT512 H-T V-para 2seed": ([0.0109, -0.0096, 0.0306], "arms/dt512/aggregates/paired_gap-HvsT-2seed.json (stratified two-level bootstrap)"),
 "DEEPTHINK T-D V-para 2seed": ([0.0746, 0.0398, 0.1099], "arms/deepthink/aggregates/L2-TvsD-2seed.paired_gap.json"),
 "QUANTCEIL Q-H V-para 2seed": ([0.0041, -0.0240, 0.0325], "arms/quantceil/aggregates/paired_gap-QvsH-2seed.json"),
 "QUANTCEIL Q-H v0.2 s42": ([0.0083, -0.0109, 0.0282], "arms/quantceil/aggregates/paired_gap-QvsH-1seed.json"),
 "SEEDVAR H 3-seed mean V-para": ([0.5497, None, None], "arms/seedvar/aggregates/seedvar-H-3seed.opus.json (per-seed percentile CIs 0.500-0.563 / 0.538-0.607 / 0.509-0.579; seed-level SD 0.0202, k=3 -> t-CI of the seed mean 0.5497 +/- 0.0501)"),
}
out = {"notes": __doc__, "rows": {}}
arms = {}
for lab, ds in [("H", "vpara"), ("T", "vpara"), ("D", "vpara"), ("Q", "vpara"), ("K", "vpara"), ("H3", "vpara"), ("H", "v02"), ("Q", "v02"), ("K", "v02")]:
    arms[(lab, ds)] = arm(lab, ds)[0]
pairs = [("DT512 H-T V-para 2seed", ("H", "vpara"), ("T", "vpara")), ("DEEPTHINK T-D V-para 2seed", ("T", "vpara"), ("D", "vpara")),
         ("QUANTCEIL Q-H V-para 2seed", ("Q", "vpara"), ("H", "vpara")), ("QUANTCEIL Q-H v0.2 s42", ("Q", "v02"), ("H", "v02"))]
for name, a, b in pairs:
    r = delta_row(arms[a], arms[b]); pt, lo, hi = CITED[name][0]; r["a_cited_bootstrap"] = [pt, lo, hi]; r["a_source"] = CITED[name][1]
    out["rows"][name] = r
r = level_row(arms[("H3", "vpara")]); r["a_cited_bootstrap"] = CITED["SEEDVAR H 3-seed mean V-para"][0]; r["a_source"] = CITED["SEEDVAR H 3-seed mean V-para"][1]
r["a_seed_level_t"] = [0.5497, round(0.5497-0.0501, 4), round(0.5497+0.0501, 4)]
out["rows"]["SEEDVAR H 3-seed mean V-para"] = r
# disagreement flags (> 0.01 at either end) between a, b, c where a has bounds
for name, r in out["rows"].items():
    a = r["a_cited_bootstrap"] if r["a_cited_bootstrap"][1] is not None else r.get("a_seed_level_t")
    b = r.get("b_logit_t", r.get("b_logit_t_meanratio"))[1:]; c = r.get("c_paired_t", r.get("c_delta_t"))
    r["max_end_gap"] = {"a_vs_b": round(max(abs(a[1]-b[0]), abs(a[2]-b[1])), 4), "a_vs_c": round(max(abs(a[1]-c[0]), abs(a[2]-c[1])), 4), "b_vs_c": round(max(abs(b[0]-c[0]), abs(b[1]-c[1])), 4)}
    r["disagree_gt_0.01"] = [k for k, v in r["max_end_gap"].items() if v > 0.01]
json.dump(out, open(os.path.join(os.path.dirname(__file__), "..", "aggregates", "robust_ci.json"), "w"), indent=1)
# ---- part 3: power
def zq(p): return tq(p, 100000)
def n_needed(sdv, delta=0.03, alpha=0.05, power=0.8, two=True):
    z = zq(1-alpha/2 if two else 1-alpha)+zq(power); n = math.ceil(z*z*sdv*sdv/delta**2)
    for _ in range(5):  # t correction
        t = tq(1-alpha/2 if two else 1-alpha, n-1)+zq(power); n = math.ceil(t*t*sdv*sdv/delta**2)
    return n
def paired_sd_per_seed(la, lb, ds):  # s_d per single seed (linearized), for matched seed index
    want = set(x for x in open(IDS[ds]).read().split("\n") if x)
    SA = [load(p, want) for p in F[la][ds]]; SB = [load(p, want) for p in F[lb][ds]]; res = []
    for a, b in zip(SA, SB):
        ids = sorted(set(a) & set(b)); res.append(round(sd([x-y for x, y in zip(infl(a, ids), infl(b, ids))]), 4))
    return res
power = {"deep_arm_deltas_vpara": {}}
for la, lb in [("H", "T"), ("T", "D"), ("Q", "H")]:
    per = paired_sd_per_seed(la, lb, "vpara"); two = out["rows"][{"H": "DT512 H-T V-para 2seed", "T": "DEEPTHINK T-D V-para 2seed", "Q": "QUANTCEIL Q-H V-para 2seed"}[la]]["s_d_linearized"]
    power["deep_arm_deltas_vpara"][la+"-"+lb] = {"s_d_per_seed": per, "s_d_2seed_avg": two}
# 4B seed-vs-seed on v0.2 (same config, pure seed noise) and K vs H v0.2 s42 (4B vs deep)
want = set(x for x in open(IDS["v02"]).read().split("\n") if x)
k42, k43 = [load(p, want) for p in F["K"]["v02"]]; ids = sorted(set(k42) & set(k43))
sd_4b_seed = round(sd([x-y for x, y in zip(infl(k42, ids), infl(k43, ids))]), 4)
kh = delta_row(arms[("H", "v02")], arms[("K", "v02")]) if False else None
power["fourB_v02_seed_vs_seed_s_d"] = sd_4b_seed
cands = {"4B v0.2 seed-vs-seed (K s42-s43)": sd_4b_seed, "notes 4B v0.2 (back-solved)": 0.094}
for k, v in power["deep_arm_deltas_vpara"].items():
    cands["deep %s V-para 1 seed (mean of seeds)" % k] = round(mean(v["s_d_per_seed"]), 4); cands["deep %s V-para 2-seed avg" % k] = v["s_d_2seed_avg"]
power["n_for_delta_0.03_two_sided_80pct"] = {k: n_needed(v) for k, v in cands.items()}
power["s_d_used"] = cands
# absolute bar: mean raw ratio > 0.50 at n=110 one-sided alpha 0.05, sigma = observed per-item SD of linearized ratio (+ sigma_run common mode)
bar = {}
for lab, ds in [("H", "v02"), ("K", "v02"), ("H", "vpara"), ("H3", "vpara")]:
    A = arms[(lab, ds)]; s_item = sd(infl(A, sorted(A))); n = 110
    for s_run in (0.0, 0.020):
        se = math.sqrt(s_item**2/n+s_run**2); crit = tq(0.95, n-1); need = 0.5+crit*se
        bar["%s %s s_item=%.3f s_run=%.3f" % (lab, ds, s_item, s_run)] = {"se": round(se, 4), "required_point": round(need, 4),
            "power_if_truth_0.53": round(1-tcdf(crit-(0.53-0.5)/se, n-1), 3), "n_for_80pct_at_0.53": math.ceil(((zq(0.95)+zq(0.8))*s_item/0.03)**2) if s_run == 0 else None}
power["bar_test_n110_onesided_0.05"] = bar
json.dump(power, open(os.path.join(os.path.dirname(__file__), "..", "aggregates", "power.json"), "w"), indent=1)
print(json.dumps({k: {x: y for x, y in v.items() if x in ("n","delta","R","a_cited_bootstrap","a_seed_level_t","b_logit_t","b_logit_t_meanratio","c_paired_t","c_delta_t","disagree_gt_0.01","max_end_gap","s_d_linearized","mean_item_ratio_unclipped")} for k, v in out["rows"].items()}, indent=0))
print(json.dumps(power, indent=0))
