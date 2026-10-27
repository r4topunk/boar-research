#!/usr/bin/env python3
"""REVEAL-CENSUS analysis (0 calls). python3 -I reveal_census.py -> ../REVEAL-CENSUS-2026-10-21.json (+ stdout). Criterion ../REVEAL-CENSUS-criterion.md (sha checked)."""
import json, os, glob, math, random, hashlib, collections
HERE = os.path.dirname(os.path.abspath(__file__)); RUL = os.path.dirname(HERE); W = f"{RUL}/reveal-census"
CRIT = open(f"{RUL}/REVEAL-CENSUS-criterion.sha256").read().split()[0]
assert hashlib.sha256(open(f"{RUL}/REVEAL-CENSUS-criterion.md", "rb").read()).hexdigest() == CRIT, "criterion sha mismatch"
S = json.load(open(f"{W}/in/set.json"))
TR = {}
for p, f in S["traces"].items():
    for l in open(f):
        if l.strip(): t = json.loads(l); TR[t["itemId"]] = t["answer"]["text"]
new = collections.defaultdict(dict)
for f in glob.glob(f"{W}/out/*.judgments.jsonl"):
    for l in open(f):
        x = json.loads(l)
        if x.get("ok") is True: new[(x["queryId"], x["refsSha256"][:16])][x["order"]] = x["mapped"]
OP = {}
for k, u in S["units"].items():
    i, th, rs = k.split("|"); assert hashlib.sha256(TR[i].encode()).hexdigest()[:16] == th, k
    pairs = S["reuse_mapped"].get(k) or ([new[(i, rs)]] if set(new.get((i, rs), {})) == {"boarA", "boarB"} else [])
    if not pairs: continue
    OP[(u["pop"], i)] = sum(m[o]["boar"]["correctness"] for m in pairs for o in ("boarA", "boarB")) / (2 * len(pairs))
CE = lambda c: c <= 1.5; OK = lambda c: c >= 4
def cp(k, n, a=0.05):
    if n == 0: return None
    cdf = lambda x, p: sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(0, x + 1))
    def bis(f):
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if f(mid): hi = mid
            else: lo = mid
        return (lo + hi) / 2
    return [0.0 if k == 0 else bis(lambda p: 1 - cdf(k - 1, p) >= a / 2), 1.0 if k == n else bis(lambda p: cdf(k, p) <= a / 2)]
def ratio_ci(kc, ke):
    c = cp(kc, kc + ke)
    if c is None: return None
    f = lambda p: None if p >= 1 else round(p / (1 - p), 3)
    return [f(c[0]), f(c[1])]
r3 = lambda x: None if x is None else round(x, 3)
def cell(rows, judge):
    lab = [(OP[(r["pop"], r["id"])] if judge == "opus" else r["corr"]) for r in rows]; n = len(lab)
    kc = sum(map(OK, lab)); ke = sum(map(CE, lab))
    return dict(n=n, correct=kc, CE=ke, partial=n - kc - ke, per100_correct=r3(100 * kc / n) if n else None, per100_CE=r3(100 * ke / n) if n else None,
                ratio=r3(kc / ke) if ke else None, ratio_cp=ratio_ci(kc, ke), net_per100=r3(100 * (kc - ke) / n) if n else None)
res = dict(criterion_sha256=CRIT, units_labelled=len(OP), units_total=len(S["units"]))
M = [dict(r, pop="MAIN") for r in S["pop"]["MAIN"]]
assert all(("MAIN", r["id"]) in OP for r in M), "MAIN census incomplete"
res["MAIN"] = {}
for name, sel in (("all", lambda r: True), ("nonhealth", lambda r: not r["health"]), ("health", lambda r: r["health"]),
                  ("warned", lambda r: r["w"]), ("unwarned_nokept", lambda r: not r["w"])):
    rows = [r for r in M if sel(r)]; res["MAIN"][name] = {"opus": cell(rows, "opus"), "haiku": cell(rows, "haiku")}
res["MAIN_by_bucket"] = {b: {"opus": cell([r for r in M if r["bucket"] == b], "opus"), "haiku": cell([r for r in M if r["bucket"] == b], "haiku")}
                         for b in sorted({r["bucket"] for r in M})}
res["MAIN_by_bucket_nonhealth"] = {b: cell([r for r in M if r["bucket"] == b and not r["health"]], "opus") for b in sorted({r["bucket"] for r in M})}
res["MAIN_health_rows"] = [dict(id=r["id"], bucket=r["bucket"], tier=r["tier"], haiku=r["corr"], opus=OP[("MAIN", r["id"])], text=r["text200"]) for r in M if r["health"]]
res["MAIN_opus_CE_rows"] = [dict(id=r["id"], bucket=r["bucket"], health=r["health"], haiku=r["corr"], opus=OP[("MAIN", r["id"])]) for r in M if CE(OP[("MAIN", r["id"])])]
# ST: stratified sample
SAMP = {i: k for k, ids in S["st_sample"].items() for i in ids}; POPN = S["st_strata"]
ST = [dict(r, pop="ST", stratum=SAMP[r["id"]]) for r in S["pop"]["ST"] if r["id"] in SAMP]
STL = [r for r in ST if ("ST", r["id"]) in OP]; res["ST_labelled"] = len(STL); res["ST_sample"] = len(ST)
def wexp(rows, judge, strata=None):
    by = collections.defaultdict(list)
    for r in rows: by[r["stratum"]].append(r)
    tot = dict(N=0, c=0.0, e=0.0)
    for s, rs in by.items():
        if strata and s not in strata: continue
        f = POPN[s] / len(rs); lab = [(OP[("ST", r["id"])] if judge == "opus" else r["corr"]) for r in rs]
        tot["N"] += POPN[s]; tot["c"] += f * sum(map(OK, lab)); tot["e"] += f * sum(map(CE, lab))
    return dict(pop_rows=tot["N"], est_correct=r3(tot["c"]), est_CE=r3(tot["e"]), per100_correct=r3(100 * tot["c"] / tot["N"]) if tot["N"] else None,
                per100_CE=r3(100 * tot["e"] / tot["N"]) if tot["N"] else None, ratio=r3(tot["c"] / tot["e"]) if tot["e"] else None)
def sboot(rows, judge, strata=None, B=2000, seed=11):
    by = collections.defaultdict(list)
    for r in rows: by[r["stratum"]].append(r)
    rnd = random.Random(seed); xs = []
    for _ in range(B):
        bs = [rs[rnd.randrange(len(rs))] for s, rs in by.items() for _ in rs]
        v = wexp(bs, judge, strata)["ratio"]
        if v is not None: xs.append(v)
    xs.sort(); return [round(xs[int(0.025 * len(xs))], 3), round(xs[int(0.975 * len(xs)) - 1], 3)] if xs else None
NH = [k for k in POPN if k.endswith("|nh")]; HH = [k for k in POPN if k.endswith("|h")]
res["ST"] = {}
for name, strata in (("all", None), ("nonhealth", NH), ("health", HH)):
    rows = [r for r in STL if strata is None or r["stratum"] in strata]
    res["ST"][name] = {"opus_weighted": wexp(STL, "opus", strata), "opus_weighted_boot_ratio": sboot(STL, "opus", strata),
                       "opus_unweighted": cell(rows, "opus"), "haiku_weighted_same_sample": wexp(STL, "haiku", strata), "haiku_unweighted": cell(rows, "haiku")}
res["ST_haiku_census"] = {n: cell([dict(r, pop="ST") for r in S["pop"]["ST"] if sel(r)], "haiku") for n, sel in (("all", lambda r: True), ("nonhealth", lambda r: not r["health"]), ("health", lambda r: r["health"]))}
res["ST_by_stratum"] = {s: cell([r for r in STL if r["stratum"] == s], "opus") for s in sorted(POPN)}
res["ST_by_bucket_unweighted"] = {b: cell([r for r in STL if r["bucket"] == b], "opus") for b in sorted({r["bucket"] for r in STL})}
res["ST_opus_CE_health"] = [dict(id=r["id"], haiku=r["corr"], opus=OP[("ST", r["id"])], text=r["text200"]) for r in STL if r["health"] and CE(OP[("ST", r["id"])])]
# rules
mn = res["MAIN"]["nonhealth"]["opus"]; lo = (mn["ratio_cp"] or [0])[0] or 0
res["rule2_reopen_nonhealth_show_anyway"] = bool(mn["ratio"] is not None and mn["ratio"] >= 1.0 and lo > 0.7)
res["rule3_health_opus_CE"] = dict(MAIN=res["MAIN"]["health"]["opus"]["CE"], ST_sample=len(res["ST_opus_CE_health"]))
res["script_sha256"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
json.dump(res, open(f"{RUL}/REVEAL-CENSUS-2026-10-21.json", "w"), indent=1)
print(json.dumps({k: res[k] for k in ("units_labelled", "MAIN", "MAIN_by_bucket", "MAIN_by_bucket_nonhealth", "MAIN_health_rows", "ST_labelled", "rule2_reopen_nonhealth_show_anyway", "rule3_health_opus_CE")}, indent=0)[:6000])
