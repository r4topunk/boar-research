#!/usr/bin/env python3 -I
"""LENGTH-SLOPE analysis (0 LLM, 0 judge). python3 -I length_slope.py <dataset.json from length_slope_build.py> <out.json> [<out.md-table>]
Length = whitespace-split words of answer.text (heuristic; ~1.3 tokens/word for English). s = judge.v1 mean(correctness, completeness, usefulness) of the boar answer,
averaged over both orders (1-5 scale). Fits (OLS, per tier x judge family): s ~ a + b*log2(words+1) [b = score per doubling] and s ~ a + b*words/100.
Variants: all rows; partial (+ declined/warned dummies); shown-only (declined and warned rows excluded); within-item (item fixed effects, items with >=2 distinct
answers in the cell). CI = 95 % percentile bootstrap resampling item ids (B 1000, seed 11). Paired contrasts: X2b ON vs OFF, literal vs succinct persona."""
import json, sys, random, math, collections
import numpy as np
D = json.load(open(sys.argv[1]))
def tier(m):
    m = str(m).lower()
    if "claude" in m or m in ("none", "null"): return None
    if "1.5b" in m: return "Qwen2.5-1.5B"
    if "qwen3-1.7b" in m: return "Qwen3-1.7B"
    if "qwen3-4b" in m or "qwen3 4b" in m: return "Qwen3-4B"
    if "gemma-4-e" in m: return "Gemma-4-E2B/E4B"
    if any(x in m for x in ("deep35", "35b", "gemma4-26b", "llama-omni", "bmoe")): return "Deep 26-35B"
    return None
rows = []
for u in D:
    t = tier(u["model"])
    if t: rows.append(dict(t=t, j=u["judge"], id=u["id"], x=math.log2(u["words"] + 1), w=u["words"], s=u["s"], bad=bool(u["declined"] or u["warned"]), dec=bool(u["declined"]), wr=bool(u["warned"]), run=u["run"], per=u["persona"]))
def ols(X, y):
    X = np.column_stack([np.ones(len(y))] + X); b, *_ = np.linalg.lstsq(X, y, rcond=None); return b
def fit(R, kind, var):
    if var in ("shown", "within_shown"): R = [r for r in R if not r["bad"]]
    if len(R) < 15: return None
    y = np.array([r["s"] for r in R]); x = np.array([r["x"] if kind == "log2" else r["w"] / 100 for r in R])
    if var == "partial": return ols([x, np.array([r["dec"] for r in R], float), np.array([r["wr"] for r in R], float)], y)[1]
    if var in ("within", "within_shown"):
        g = collections.defaultdict(list)
        for i, r in enumerate(R): g[r["id"]].append(i)
        xs, ys = [], []
        for ix in g.values():
            if len(ix) < 2 or len(set(round(x[i], 6) for i in ix)) < 2 and len(set(y[i] for i in ix)) < 2: continue
            xs += list(x[ix] - x[ix].mean()); ys += list(y[ix] - y[ix].mean())
        xs, ys = np.array(xs), np.array(ys)
        return float((xs @ ys) / (xs @ xs)) if len(xs) > 10 and xs @ xs > 0 else None
    return ols([x], y)[1]
def boot(R, kind, var, B=1000):
    est = fit(R, kind, var)
    if est is None: return None
    g = collections.defaultdict(list)
    for r in R: g[r["id"]].append(r)
    ids = list(g); rnd = random.Random(11); bs = []
    for _ in range(B):
        S = [r for i in (rnd.choice(ids) for _ in ids) for r in g[i]]
        try:
            v = fit(S, kind, var)
            if v is not None and np.isfinite(v): bs.append(v)
        except Exception: pass
    bs.sort(); lo, hi = (bs[int(.025 * len(bs))], bs[int(.975 * len(bs)) - 1]) if len(bs) > 50 else (None, None)
    return dict(b=round(float(est), 4), lo=None if lo is None else round(float(lo), 4), hi=None if hi is None else round(float(hi), 4))
out = {"length_unit": "whitespace words", "cells": {}, "pairs": {}}
cells = collections.defaultdict(list)
for r in rows: cells[(r["t"], r["j"])].append(r)
for (t, j), R in sorted(cells.items()):
    c = dict(n=len(R), items=len({r["id"] for r in R}), median_words=float(np.median([r["w"] for r in R])), bad_share=round(sum(r["bad"] for r in R) / len(R), 3), mean_s=round(float(np.mean([r["s"] for r in R])), 3))
    for var in ("all", "partial", "shown", "within", "within_shown"):
        c[var] = boot(R, "log2", var)
    c["all_per100w"] = boot(R, "w", "all"); c["shown_per100w"] = boot(R, "w", "shown")
    out["cells"][f"{t}|{j}"] = c
# paired contrasts
def pairs(name, pa, pb, sel):
    g = collections.defaultdict(lambda: ([], []))
    for r in rows:
        if not sel(r): continue
        k = (r["t"], r["j"], r["id"])
        if pa(r): g[k][0].append(r)
        if pb(r): g[k][1].append(r)
    res = {}
    for jt in sorted({(k[0], k[1]) for k in g}):
        P = []
        for k, (A, B) in g.items():
            if (k[0], k[1]) == jt and A and B:
                m = lambda L, f: float(np.mean([f(r) for r in L]))
                P.append(dict(id=k[2], dS=m(A, lambda r: r["s"]) - m(B, lambda r: r["s"]), dX=m(A, lambda r: r["x"]) - m(B, lambda r: r["x"]), bad=any(r["bad"] for r in A + B)))
        if len(P) < 8: continue
        def f(Q, shown=False):
            Q = [q for q in Q if not (shown and q["bad"])]
            if len(Q) < 8: return None
            dx = np.array([q["dX"] for q in Q]); ds = np.array([q["dS"] for q in Q])
            return float(((dx - dx.mean()) @ (ds - ds.mean())) / ((dx - dx.mean()) @ (dx - dx.mean()))) if ((dx - dx.mean()) @ (dx - dx.mean())) > 1e-9 else None
        rnd = random.Random(11); bs = []
        for _ in range(1000):
            v = f([rnd.choice(P) for _ in P])
            if v is not None: bs.append(v)
        bs.sort()
        cell = dict(n=len(P), mean_dU=round(float(np.mean([q["dS"] for q in P])), 4), mean_dlog2w=round(float(np.mean([q["dX"] for q in P])), 3),
                    slope=None if f(P) is None else round(f(P), 4), slope_ci=[round(bs[int(.025 * len(bs))], 4), round(bs[int(.975 * len(bs)) - 1], 4)] if len(bs) > 50 else None,
                    n_shown=len([q for q in P if not q["bad"]]), slope_shown=None if f(P, True) is None else round(f(P, True), 4))
        res[f"{jt[0]}|{jt[1]}"] = cell
    out["pairs"][name] = res
on = lambda r: any(k in r["run"] for k in ("x2b-on", "x2bon", "headpassx2b")); off = lambda r: any(k in r["run"] for k in ("x2b-off", "x2boff"))
pairs("X2b_ON_minus_OFF", on, off, lambda r: on(r) or off(r))
pairs("literal_minus_succinct_persona", lambda r: r["per"] == "literal", lambda r: r["per"] == "succinct", lambda r: r["per"] in ("literal", "succinct"))
json.dump(out, open(sys.argv[2], "w"), indent=1)
for k, c in out["cells"].items(): print(k, c["n"], c["items"], "medw", c["median_words"], "bad", c["bad_share"], "all", c["all"], "partial", c["partial"], "shown", c["shown"], "within", c["within"], "wshown", c["within_shown"])
print(json.dumps(out["pairs"], indent=1))
