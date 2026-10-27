#!/usr/bin/env python3
"""HON-10 WARN-OPUS analysis (0 calls). python3 -I warn_opus_analyze.py [--haiku-only] -> ../warn-opus/warn-opus-{opus,haiku}.json (+ stdout)
Criterion ../WARN-OPUS-criterion.md (sha checked). Labels as the frozen WARNCAL/SHOWANYWAY script (labels.py thresholds): CE = corr <= 1.5, correct = corr >= 4,
corr = mean boar correctness of the 2 orders (judg_lp formula). Weighted estimators: stratum total of rows with a property = (M_s / n_s) * sum over sampled units of
(rows of the unit with the property); census strata exact. Haiku per unit = its own LP rows' Haiku labels; Opus per unit = one label for all its rows (same text)."""
import json, glob, math, random, hashlib, collections, sys
R0 = "<workspace>/rnd/research/coordinator"; OUT = f"{R0}/ruler/warn-opus"; A = f"{R0}/arms"
CRIT = open(f"{R0}/ruler/WARN-OPUS-criterion.sha256").read().split()[0]
assert hashlib.sha256(open(f"{R0}/ruler/WARN-OPUS-criterion.md", "rb").read()).hexdigest() == CRIT, "criterion sha mismatch"
HONLY = "--haiku-only" in sys.argv
D = json.load(open(f"{OUT}/in/set.json")); LPD = f"{A}/litepacks/traces"
def jload(files):
    by = collections.defaultdict(dict)
    for f in files:
        for l in open(f):
            x = json.loads(l)
            if x.get("ok") is True: by[x["queryId"]][x["order"]] = x["mapped"]
    return by
def score(v):
    ms = list(v.values()); mean = lambda d: sum(d.values()) / 3
    return dict(s=sum(mean(m["boar"]) for m in ms) / 2, sref=sum(mean(m["ref"]) for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2)
TX = {}
def text(arm, i):
    if arm not in TX:
        TX[arm] = {}
        for f in sorted(glob.glob(f"{LPD}/lp-{arm}-*-s42.traces.jsonl")):
            for l in open(f):
                if l.strip(): t = json.loads(l); TX[arm][t["itemId"]] = t["answer"]["text"]
    return TX[arm][i]
OP = {}
if not HONLY:
    ru = jload(glob.glob(f"{A}/refuse-unsupported/ce-opus-ru/out/*.judgments.jsonl"))
    for k, j in D["judge"].items():
        assert k.split("|")[1] == hashlib.sha256(text(j["arm"], j["id"]).encode()).hexdigest()[:16], k
        if j["reuse_ceopusru"]: v = ru[j["id"]]
        else:
            un = "v01" if not j["id"].startswith("st-") else j["id"][3:].rsplit("-", 1)[0]
            v = jload([f"{OUT}/out/{j['arm']}-{un}.judgments.jsonl"])[j["id"]]
        assert set(v) == {"boarA", "boarB"}, f"missing order {k}"
        OP[k] = score(v)
CE = lambda c: c <= 1.5; OK = lambda c: c >= 4
def unit_counts(u, judge):
    rows = u["rows"]; m = len(rows)
    if judge == "haiku": ce = sum(CE(r["haiku_corr"]) for r in rows); ok = sum(OK(r["haiku_corr"]) for r in rows)
    else: c = OP[u["key"]]["corr"]; ce = m * CE(c); ok = m * OK(c)
    return m, ce, ok
POP = D["population"]; SMP = D["sample"]
def totals(sample, judge):
    """judge: haiku | opus = expansion estimator; opus_diff = PRIMARY difference estimator (census Haiku total + expanded Opus-minus-Haiku on the sample)."""
    T = {}
    for s, us in sample.items():
        M, n = POP[s]["units"], len(us); f = M / n if n else 0
        if judge == "opus_diff":
            co = [unit_counts(u, "opus") for u in us]; ch = [unit_counts(u, "haiku") for u in us]
            T[s] = dict(N=POP[s]["rows"], ce=POP[s]["haiku_ce_rows"] + f * sum(a[1] - b[1] for a, b in zip(co, ch)),
                        ok=POP[s]["haiku_correct_rows"] + f * sum(a[2] - b[2] for a, b in zip(co, ch)))
            continue
        cnt = [unit_counts(u, judge) for u in us]
        T[s] = dict(N=POP[s]["rows"], ce=f * sum(c[1] for c in cnt), ok=f * sum(c[2] for c in cnt))
    return T
def haiku_census():
    return {s: dict(N=POP[s]["rows"], ce=POP[s]["haiku_ce_rows"], ok=POP[s]["haiku_correct_rows"]) for s in POP if s != "CAND-h"}
sd = lambda a, b: a / b if b else None
def metrics(T):
    W = ["W-nh", "W-h"]; H = ["H-nh", "H-h"]; U = ["S"] + H
    Nw = sum(T[s]["N"] for s in W); Nu = sum(T[s]["N"] for s in U)
    cw = sum(T[s]["ce"] for s in W); kw = sum(T[s]["ok"] for s in W); cu = sum(T[s]["ce"] for s in U); ku = sum(T[s]["ok"] for s in U)
    rc = cw + sum(T[s]["ce"] for s in H); rk = kw + sum(T[s]["ok"] for s in H); rn = Nw + sum(T[s]["N"] for s in H)
    return dict(precision=sd(cw, Nw), recall=sd(cw, cw + cu), p_corr_w=sd(kw, Nw), p_corr_u=sd(ku, Nu), p_ce_u=sd(cu, Nu), ratio_w_u=sd(sd(cw, Nw), sd(cu, Nu)) if cu else None,
                reveal_correct_to_ce=sd(rk, rc), reveal_correct_per100=sd(100 * rk, rn), reveal_ce_per100=sd(100 * rc, rn), reveal_net_per100=sd(100 * (rk - rc), rn),
                est_rows=dict(warned=Nw, unwarned=Nu, ce_w=cw, ce_u=cu, correct_w=kw, correct_u=ku, reveals=rn, reveal_correct=rk, reveal_ce=rc))
MS = {s: v for s, v in SMP.items() if s != "CAND-h"}
def boot(judge, B=2000, seed=11):
    rnd = random.Random(seed); xs = collections.defaultdict(list)
    for _ in range(B):
        bs = {s: [us[rnd.randrange(len(us))] for _ in us] if s in ("W-nh", "H-nh", "S") else us for s, us in MS.items()}
        for k, v in metrics(totals(bs, judge)).items():
            if v is not None and not isinstance(v, dict): xs[k].append(v)
    return {k: [round(sorted(v)[int(0.025 * len(v))], 3), round(sorted(v)[int(0.975 * len(v)) - 1], 3)] for k, v in xs.items()}
def cp(k, n, a=0.05):  # Clopper-Pearson exact (bisection on the binomial cdf)
    if n == 0: return None
    def cdf(x, p): return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, x + 1))
    def bis(f, lo=0.0, hi=1.0):
        for _ in range(60):
            mid = (lo + hi) / 2
            if f(mid): hi = mid
            else: lo = mid
        return (lo + hi) / 2
    lo = 0.0 if k == 0 else bis(lambda p: 1 - cdf(k - 1, p) >= a / 2)
    hi = 1.0 if k == n else bis(lambda p: cdf(k, p) <= a / 2)
    return [round(lo, 3), round(hi, 3)]
def unit_label(u, judge):
    c = OP[u["key"]]["corr"] if judge == "opus" else u["rows"][0]["haiku_corr"]  # haiku: representative (first) row
    return c
def strata_table(judge):
    out = {}
    for s, us in SMP.items():
        cs = [unit_label(u, judge) for u in us]; n = len(cs); k_ce = sum(CE(c) for c in cs); k_ok = sum(OK(c) for c in cs)
        out[s] = dict(pop_units=POP[s]["units"], pop_rows=POP[s]["rows"], n_units=n, ce=k_ce, ce_cp=cp(k_ce, n), correct=k_ok, correct_cp=cp(k_ok, n), mid=n - k_ce - k_ok)
    # unweighted pooled sample cells (exact): warned units, unwarned units, reveal units (MS)
    def pool(ss):
        cs = [unit_label(u, judge) for s in ss for u in SMP[s]]; n = len(cs); a = sum(CE(c) for c in cs); b = sum(OK(c) for c in cs)
        return dict(n=n, ce=a, ce_cp=cp(a, n), correct=b, correct_cp=cp(b, n), correct_among_correct_or_ce_cp=cp(b, a + b),
                    ratio_cp=[round(x / (1 - x), 3) if x < 1 else None for x in cp(b, a + b)] if a + b else None)
    out["pooled_unweighted"] = {"warned": pool(["W-nh", "W-h"]), "unwarned": pool(["S", "H-nh", "H-h"]), "reveal_MS": pool(["W-nh", "W-h", "H-nh", "H-h"]),
                                "health_reveal_all": pool(["W-h", "H-h", "CAND-h"])}
    return out
res = dict(criterion_sha256=CRIT, judge="opus judge.v1" if not HONLY else "haiku 5.5-low (existing LP rows)")
rnd4 = lambda m: {k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items() if k != "est_rows"}
mc = metrics(haiku_census()); res["haiku_census_MS"] = dict(weighted=rnd4(mc), est_rows=mc["est_rows"], note="Haiku labels on every MS LP row (the WARNCAL/SHOWANYWAY numbers restricted to MAIN + ST-SE)")
for judge in (["haiku"] if HONLY else ["haiku", "opus", "opus_diff"]):
    T = totals(MS, judge); m = metrics(T)
    res[judge] = dict(weighted=rnd4(m), est_rows={k: round(v, 2) for k, v in m["est_rows"].items()},
                      boot_ci=boot(judge), strata=strata_table("opus" if judge == "opus_diff" else judge))
if not HONLY:
    ks = list(D["judge"])
    hc = {}
    for s, us in SMP.items():
        for u in us: hc[u["key"]] = u["rows"][0]["haiku_corr"]
    pairs = [(hc[k], OP[k]["corr"]) for k in ks]
    def kappa(fn):
        a = [fn(h) for h, _ in pairs]; b = [fn(o) for _, o in pairs]; n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
        pa, pb = sum(a) / n, sum(b) / n; pe = pa * pb + (1 - pa) * (1 - pb); return dict(agree=sum(x == y for x, y in zip(a, b)), n=n, agree_cp=cp(sum(x == y for x, y in zip(a, b)), n),
                                                                                      haiku_pos=sum(a), opus_pos=sum(b), haiku_only=sum(x and not y for x, y in zip(a, b)), opus_only=sum(y and not x for x, y in zip(a, b)),
                                                                                      kappa=round((po - pe) / (1 - pe), 3) if pe < 1 else None)
    res["agreement"] = dict(CE=kappa(CE), correct=kappa(OK), corr_mae=round(sum(abs(h - o) for h, o in pairs) / len(pairs), 3), corr_signed_opus_minus_haiku=round(sum(o - h for h, o in pairs) / len(pairs), 3))
    res["agreement"]["haiku_only_CE"] = sorted(k.split("|")[0] for k in ks if CE(hc[k]) and not CE(OP[k]["corr"]))
    res["agreement"]["opus_only_CE"] = sorted(k.split("|")[0] for k in ks if CE(OP[k]["corr"]) and not CE(hc[k]))
    hl = []
    for s in ("W-h", "H-h", "CAND-h"):
        for u in SMP[s]:
            hl.append(dict(stratum=s, id=u["id"], arms=[r["arm"] for r in u["rows"]], tier=u["rows"][0]["tier"], haiku_corr=[r["haiku_corr"] for r in u["rows"]], opus_corr=OP[u["key"]]["corr"],
                           opus_CE=CE(OP[u["key"]]["corr"]), opus_correct=OK(OP[u["key"]]["corr"])))
    res["health_reveals"] = sorted(hl, key=lambda x: (not x["opus_CE"], x["id"]))
    res["health_opus_ce_units"] = sum(x["opus_CE"] for x in hl); res["health_opus_ce_rows"] = sum(len(x["arms"]) for x in hl if x["opus_CE"])
    res["health_opus_correct_units"] = sum(x["opus_correct"] for x in hl)
    res["health_se_019"] = [x for x in hl if x["id"] == "st-qa-health-se-019"]
    o = res["opus_diff"]; w = o["weighted"]; ci = o["boot_ci"]
    res["decisions"] = dict(
        D1_two_thirds_sentence="DROP" if (ci["precision"][1] < 0.30 or ci["recall"][1] < 0.50) else "KEEP",
        D2_five_percent_sentence="DROP" if w["p_corr_w"] > 0.15 else "KEEP",
        D3_reveal_ratio_sentence="DROP" if w["reveal_correct_to_ce"] >= 1.0 else "KEEP",
        D3b_liability_verdict="WITHDRAWN" if ci["reveal_correct_to_ce"][0] >= 1.0 else "STANDS",
        D4_safety_clause="STANDS" if res["health_opus_ce_units"] >= 1 else "WITHDRAWN",
        D4_health_se_019_example="KEEP" if any(x["opus_CE"] for x in res["health_se_019"]) else "WITHDRAW")
name = "haiku" if HONLY else "opus"
s = json.dumps(res, indent=1, ensure_ascii=False); open(f"{OUT}/warn-opus-{name}.json", "w").write(s)
print(json.dumps({k: res[k] for k in res if k in ("decisions", "agreement", "health_opus_ce_units", "health_opus_ce_rows")}, indent=0)[:3000])
print("haiku_census_MS", json.dumps(res["haiku_census_MS"]["weighted"]))
for j in ("haiku", "opus", "opus_diff"):
    if j in res: print(j, json.dumps(res[j]["weighted"]), json.dumps(res[j]["boot_ci"]))
