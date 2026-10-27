#!/usr/bin/env python3
"""HAIKU-CAL step 2 (0 calls): Haiku 5.5-low -> Opus judge.v1 calibration map on the double-labelled pool (../haiku-cal/units.json from haiku_cal_index.py).
Spec ../HAIKU-CAL-criterion.md (sha checked). python3 -I haiku_cal.py -> ../HAIKU-CAL-2026-10-21.json (+ stdout)."""
import json, os, math, random, hashlib, collections
HERE = os.path.dirname(os.path.abspath(__file__)); RUL = os.path.dirname(HERE)
CRIT = open(f"{RUL}/HAIKU-CAL-criterion.sha256").read().split()[0]
assert hashlib.sha256(open(f"{RUL}/HAIKU-CAL-criterion.md", "rb").read()).hexdigest() == CRIT, "criterion sha mismatch"
D = json.load(open(f"{RUL}/haiku-cal/units.json"))
SRC = [("CE-OPUS", "arms/ce-opus-check/"), ("CE-OPUS-RU", "ce-opus-ru/"), ("WARN-OPUS", "ruler/warn-opus/"), ("CV5-LADDER", "ruler/cv5-ladder/"),
       ("CV5-PER100", "ruler/cv5-per100/"), ("GEMMA-OPUS-MAIN", "ruler/gemma-opus-main/")]
V01 = set(l.strip() for l in open(f"{RUL}/../arms/litepacks/data/v01-57.ids") if l.strip())
def setof(i):
    if i in V01 or i.startswith("st-qa-cooking-se") or i.startswith("st-qa-money-se"): return "MAIN"
    if i.startswith("st-boar-"): return "ST-cand"
    if i.startswith("st-qa-"): return "ST-SE"
    return "v01-other"
def tier(u):
    r = " ".join(u["runIds"]); m = str(u["tier"])
    if "gemma4-e2b-confirm-g43" in r or "gemma4-e2b-eng" in r or "GemmaE2B" in r or "gemma-4-e2b" in m: return "Gemma-E2B"
    if "gemma4-e2b-vs4b" in r: return "4B"
    if "floor-anchors" in r or "qwen2.5-1.5b" in m: return "1.5B"
    if "gemma4-e2b-confirm-c43" in r or "1.7b" in m: return "1.7B"
    if "deep35" in m: return "deep35"
    if "4b" in m or "pixel8a" in r or "cut7" in r: return "4B"
    return "other"
mean = lambda xs: sum(xs) / len(xs) if xs else None
U = []
for k, u in D["units"].items():
    if u["declined"]: continue
    src = next((t for t, p in SRC if any(p in f for f in u["files"]["opus"])), "OTHER")
    h = {d: mean([x[d] for x in u["haiku"]]) for d in ("correctness", "completeness", "usefulness", "sref")}
    o = {d: mean([x[d] for x in u["opus"]]) for d in ("correctness", "completeness", "usefulness", "sref")}
    for x in (h, o): x["s"] = (x["correctness"] + x["completeness"] + x["usefulness"]) / 3
    U.append(dict(key=k, id=u["id"], src=src, set=setof(u["id"]), tier=tier(u), warned=u["warned"], kept=u["kept"], nh=len(u["haiku"]), no=len(u["opus"]), H=h, O=o))
ndecl = sum(1 for u in D["units"].values() if u["declined"])
CE = lambda c: c <= 1.5; OK = lambda c: c >= 4
cls = lambda c: "CE" if CE(c) else ("correct" if OK(c) else "partial")
def bin4(c): return "1-1.5" if c <= 1.5 else ("2-2.5" if c <= 2.5 else ("3-3.5" if c < 4 else "4-5"))
def wilson(k, n, z=1.96):
    if n == 0: return None
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]
def kappa(a, b):
    n = len(a)
    if n == 0: return None
    cats = sorted(set(a) | set(b)); po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return round((po - pe) / (1 - pe), 3) if pe < 1 else None
r3 = lambda x: None if x is None else round(x, 3)
def cboot(rows, fn, B=2000, seed=11):
    by = collections.defaultdict(list)
    for r in rows: by[r["id"]].append(r)
    ids = sorted(by); rnd = random.Random(seed); xs = []
    for _ in range(B):
        s = [x for _ in ids for x in by[ids[rnd.randrange(len(ids))]]]; v = fn(s)
        if v is not None: xs.append(v)
    xs.sort(); return [round(xs[int(0.025 * len(xs))], 3), round(xs[int(0.975 * len(xs)) - 1], 3)] if xs else None
def agree(rows, boot=False):
    if not rows: return dict(n=0)
    hc = [r["H"]["correctness"] for r in rows]; oc = [r["O"]["correctness"] for r in rows]
    o = dict(n=len(rows), items=len({r["id"] for r in rows}),
             kappa_CE=kappa([CE(x) for x in hc], [CE(x) for x in oc]), kappa_correct=kappa([OK(x) for x in hc], [OK(x) for x in oc]),
             kappa_3class=kappa([cls(x) for x in hc], [cls(x) for x in oc]),
             agree_CE=sum(CE(a) == CE(b) for a, b in zip(hc, oc)), haiku_only_CE=sum(CE(a) and not CE(b) for a, b in zip(hc, oc)), opus_only_CE=sum(CE(b) and not CE(a) for a, b in zip(hc, oc)),
             haiku_only_correct=sum(OK(a) and not OK(b) for a, b in zip(hc, oc)), opus_only_correct=sum(OK(b) and not OK(a) for a, b in zip(hc, oc)),
             haiku_CE=sum(map(CE, hc)), opus_CE=sum(map(CE, oc)), haiku_correct=sum(map(OK, hc)), opus_correct=sum(map(OK, oc)))
    for d in ("correctness", "completeness", "usefulness", "s", "sref"):
        dd = [r["O"][d] - r["H"][d] for r in rows]; o[f"shift_{d}"] = r3(mean(dd)); o[f"mae_{d}"] = r3(mean([abs(x) for x in dd]))
    o["U_haiku"] = r3(sum(r["H"]["s"] for r in rows) / sum(r["H"]["sref"] for r in rows)); o["U_opus"] = r3(sum(r["O"]["s"] for r in rows) / sum(r["O"]["sref"] for r in rows))
    o["dU"] = r3(o["U_opus"] - o["U_haiku"])
    if boot:
        o["dU_ci"] = cboot(rows, lambda s: sum(r["O"]["s"] for r in s) / sum(r["O"]["sref"] for r in s) - sum(r["H"]["s"] for r in s) / sum(r["H"]["sref"] for r in s))
        o["shift_corr_ci"] = cboot(rows, lambda s: mean([r["O"]["correctness"] - r["H"]["correctness"] for r in s]))
    return o
def curve(rows, grid=False):
    by = collections.defaultdict(list)
    for r in rows: by[(math.floor(r["H"]["correctness"] * 2) / 2) if grid else bin4(r["H"]["correctness"])].append(r)
    out = {}
    for b in sorted(by, key=lambda x: float(str(x).split("-")[0])):
        rs = by[b]; n = len(rs); kc = sum(OK(r["O"]["correctness"]) for r in rs); ke = sum(CE(r["O"]["correctness"]) for r in rs)
        out[str(b)] = dict(n=n, opus_corr_mean=r3(mean([r["O"]["correctness"] for r in rs])), p_opus_correct=r3(kc / n), p_opus_correct_ci=wilson(kc, n),
                           p_opus_CE=r3(ke / n), p_opus_CE_ci=wilson(ke, n), opus_s_mean=r3(mean([r["O"]["s"] for r in rs])), haiku_s_mean=r3(mean([r["H"]["s"] for r in rs])))
    return out
LISTED = [u for u in U if u["src"] != "OTHER"]
res = dict(criterion_sha256=CRIT, units_total=len(U), declines_excluded=ndecl, index=dict(n_traces_files=D["n_traces_files"], n_judgment_files=D["n_judgment_files"], unresolved_rows=D["unresolved_rows"]))
res["agreement"] = {"listed": agree(LISTED, True), "other": agree([u for u in U if u["src"] == "OTHER"], True), "all": agree(U, True)}
res["by_source"] = {s: agree([u for u in U if u["src"] == s], True) for s in [t for t, _ in SRC] + ["OTHER"]}
res["by_tier_listed"] = {t: agree([u for u in LISTED if u["tier"] == t], True) for t in sorted({u["tier"] for u in LISTED})}
res["by_tier_all"] = {t: agree([u for u in U if u["tier"] == t], True) for t in sorted({u["tier"] for u in U})}
res["by_warned_listed"] = {str(w): agree([u for u in LISTED if u["warned"] == w], True) for w in (True, False)}
res["by_set_listed"] = {s: agree([u for u in LISTED if u["set"] == s], True) for s in sorted({u["set"] for u in LISTED})}
res["curve"] = {"listed": curve(LISTED), "listed_grid": curve(LISTED, True), "listed_warned": curve([u for u in LISTED if u["warned"]]),
                "listed_unwarned": curve([u for u in LISTED if not u["warned"]]), "other": curve([u for u in U if u["src"] == "OTHER"]),
                "all_1.7B": curve([u for u in U if u["tier"] == "1.7B"]), "all_4B": curve([u for u in U if u["tier"] == "4B"])}
res["curve_by_source"] = {s: curve([u for u in U if u["src"] == s]) for s in [t for t, _ in SRC] + ["OTHER"]}
# implied correction map: cell = (Haiku bin, warned); fallback to the bin pooled over warned when n < 5 (spec)
def cmap(rows):
    m = {}
    for b in ("1-1.5", "2-2.5", "3-3.5", "4-5"):
        pool = [r for r in rows if bin4(r["H"]["correctness"]) == b]
        for w in (True, False):
            c = [r for r in pool if r["warned"] == w]; use = c if len(c) >= 5 else pool
            m[(b, w)] = (sum(OK(r["O"]["correctness"]) for r in use) / len(use) if use else 0, sum(CE(r["O"]["correctness"]) for r in use) / len(use) if use else 0, len(use), len(c) >= 5)
    return m
M17 = cmap([u for u in LISTED if u["tier"] == "1.7B"]); MALL = cmap(LISTED)
res["correction_map_1.7B_listed"] = {f"{b}|warned={w}": dict(p_correct=r3(v[0]), p_CE=r3(v[1]), n=v[2], own_cell=v[3]) for (b, w), v in M17.items()}
res["correction_map_listed"] = {f"{b}|warned={w}": dict(p_correct=r3(v[0]), p_CE=r3(v[1]), n=v[2], own_cell=v[3]) for (b, w), v in MALL.items()}
# demonstration on Haiku-only numbers: SHOWANYWAY LP revealable rows (exec warncal_showanyway.py data section unchanged)
WC = f"{HERE}/warncal_showanyway.py"; src = open(WC).read(); G = {"__file__": WC, "__name__": "warncal_defs"}
exec(src[:src.index("def wilson")], G)
LP = [r for r in G["R"] if r["src"] == "LP"]
def implied(rows, M):
    n = len(rows); kc = sum(M[(bin4(r["corr"]), r["w"])][0] for r in rows); ke = sum(M[(bin4(r["corr"]), r["w"])][1] for r in rows)
    return dict(n=n, haiku_correct=sum(r["correct"] for r in rows), haiku_CE=sum(r["CE"] for r in rows), implied_opus_correct=r3(kc), implied_opus_CE=r3(ke),
                implied_per100_correct=r3(100 * kc / n) if n else None, implied_per100_CE=r3(100 * ke / n) if n else None, implied_ratio=r3(kc / ke) if ke else None)
rev = [r for r in LP if r["revealable"]]
res["implied_SHOWANYWAY_LP"] = {"all_revealable": implied(rev, M17), "MAIN": implied([r for r in rev if r["set"] == "MAIN"], M17),
                                "ST-SE": implied([r for r in rev if r["set"] == "ST-SE"], M17), "ST-cand": implied([r for r in rev if r["set"] == "ST-cand"], M17),
                                "nonhealth": implied([r for r in rev if not r["health"]], M17), "health": implied([r for r in rev if r["health"]], M17),
                                "warned": implied([r for r in rev if r["w"]], M17), "unwarned_hidden": implied([r for r in rev if not r["w"]], M17),
                                "note": "map = 1.7B listed units (cell = Haiku corr bin x warned); rows are LITEPACKS K0/K1/K3 revealable (SHOWANYWAY definition)"}
res["implied_SHOWANYWAY_LP"]["boot_ratio_ci_all"] = cboot(rev, lambda s: (lambda a, b: a / b if b else None)(sum(M17[(bin4(r["corr"]), r["w"])][0] for r in s), sum(M17[(bin4(r["corr"]), r["w"])][1] for r in s)))
# differential shift between tiers, paired on queryIds with both tiers on the same refs (MAIN K0 family)
def diff(t1, t2, rows):
    a = collections.defaultdict(list); b = collections.defaultdict(list)
    for r in rows:
        if r["tier"] == t1: a[(r["id"], r["key"].split("|")[2])].append(r)
        if r["tier"] == t2: b[(r["id"], r["key"].split("|")[2])].append(r)
    common = sorted(set(a) & set(b))
    if len(common) < 10: return dict(n_common=len(common))
    pairs = [dict(id=c[0], A=a[c], B=b[c]) for c in common]
    def dU(rs):
        f = lambda L, fam: sum(x[fam]["s"] for x in L) / sum(x[fam]["sref"] for x in L)
        A = [x for p in rs for x in p["A"]]; B = [x for p in rs for x in p["B"]]
        return (f(A, "O") - f(A, "H")) - (f(B, "O") - f(B, "H"))
    def gap(rs, fam):
        A = [x for p in rs for x in p["A"]]; B = [x for p in rs for x in p["B"]]
        return sum(x[fam]["s"] for x in A) / sum(x[fam]["sref"] for x in A) - sum(x[fam]["s"] for x in B) / sum(x[fam]["sref"] for x in B)
    return dict(n_common=len(common), gap_haiku=r3(gap(pairs, "H")), gap_opus=r3(gap(pairs, "O")), differential_shift=r3(dU(pairs)), differential_shift_ci=cboot(pairs, dU))
res["differential_shift"] = {f"{a}-{b}": diff(a, b, U) for a, b in (("4B", "1.7B"), ("Gemma-E2B", "1.7B"), ("4B", "Gemma-E2B"), ("1.7B", "1.5B"), ("4B", "1.5B"), ("deep35", "4B"))}
ds = [v["differential_shift"] for v in res["differential_shift"].values() if "differential_shift" in v]
res["kill_differential_below_0.01_all_pairs"] = all(abs(x) < 0.01 for x in ds)
res["script_sha256"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
json.dump(res, open(f"{RUL}/HAIKU-CAL-2026-10-21.json", "w"), indent=1)
pp = lambda k: print(k, json.dumps(res[k])[:1500])
for k in ("units_total", "declines_excluded", "agreement", "by_source", "by_tier_listed", "by_warned_listed", "by_set_listed", "curve", "correction_map_1.7B_listed", "implied_SHOWANYWAY_LP", "differential_shift", "kill_differential_below_0.01_all_pairs"): pp(k)
