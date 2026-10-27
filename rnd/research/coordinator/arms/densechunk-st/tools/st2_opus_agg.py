#!/usr/bin/env python3
"""DENSECHUNK-ST2 Opus L2 aggregation (0 LLM calls). Usage: python3 -I st2_opus_agg.py > ../aggregates/st2-l2-opus.json
Same estimators as st2_agg.py (ratio of sums, item bootstrap seed 11 B 2000) on the Opus judge.v1 judgments (*.judgments.opus.jsonl) of the SAME traces;
fail-closed: every one of the 180 ids must have an ok row in both orders for both arms, else exit 1. floor_metrics.py --strict per pack x arm
(symlink dir runs/judge/opus-fm). Haiku vs Opus agreement: per-item winner (orders disagree -> tie), per-item score r, ratios, paired delta."""
import json, os, sys, subprocess, collections, importlib.util, numpy as np
T = "<workspace>/rnd/research/coordinator/arms/densechunk-st/tools"
src = open(f"{T}/st2_agg.py").read().split("out = {")[0]          # import helpers only (load, setstats, paired, constants)
g = {}; exec(compile(src, "st2_agg_helpers", "exec"), g)
load, setstats, paired, SE, TOP, OD, ND = g["load"], g["setstats"], g["paired"], g["SE"], g["TOP"], g["OD"], g["ND"]
FM = "<workspace>/boar-eval/bench/v0.2/plan/floor_metrics.py"; FD = f"{ND}/opus-fm"; os.makedirs(FD, exist_ok=True)
def cnt(p):
    ok = collections.Counter(); rows = 0
    for l in open(p):
        r = json.loads(l); rows += 1
        if r.get("ok"): ok[(r["queryId"], r["order"])] += 1
        assert r["judgeModel"].startswith("claude-opus"), (p, r["judgeModel"])
    return rows, ok
out = {"criterion_sha256_prefix": "6c7b12dd", "judge": "claude-opus-5-5 judge.v1, N=4 shards, both orders (L2)", "packs": []}
pool = {a: {} for a in ("OFF", "ON", "OFF_h", "ON_h")}; fam = {}; fails = []
for p in SE + TOP:
    ids = [x.strip() for x in open(f"{ND}/st2-{p}-cut7-s42.ids") if x.strip()]
    files = {"OFF": (f"{OD}/st-{p}-cut7-s42", "st-%s-cut7-s42-opus" % p), "ON": (f"{ND}/st2-{p}-cut7-s42", "st2-%s-cut7-s42-opus" % p)}
    J = {}; fm = {}
    for a, (base, fmname) in files.items():
        jp = base + ".judgments.opus.jsonl"
        if not os.path.exists(jp): fails.append(f"{p} {a}: no judgments"); continue
        rows, ok = cnt(jp); miss = [q for q in ids if not (ok[(q, "boarA")] and ok[(q, "boarB")])]
        if miss or rows != 2 * len(ids): fails.append(f"{p} {a}: rows {rows} missing {miss}")
        J[a] = load(jp); J[a + "_h"] = load(base + ".judgments.jsonl")
        for ext, src_ in ((".traces.jsonl", base + ".traces.jsonl"), (".judgments.jsonl", jp)):
            l = f"{FD}/{fmname}{ext}"
            if not os.path.lexists(l): os.symlink(os.path.realpath(src_), l)
        r = subprocess.run(["python3", FM, "--runs", fmname, "--dir", FD, "--ids", f"{ND}/st2-{p}-cut7-s42.ids", "--strict"], capture_output=True, text=True)
        if r.returncode: fails.append(f"{p} {a}: floor_metrics rc {r.returncode} {r.stderr[-200:]}"); continue
        m = json.loads(r.stdout.replace("NaN", "null")); fm[a] = {k: m[k] for k in ("n_items", "raw", "above_min")}
    if len(J) < 4: continue
    out["packs"].append({"pack": p, "family": "SE" if p in SE else "topic", "OFF": setstats(J["OFF"], ids), "ON": setstats(J["ON"], ids),
                         "ON_minus_OFF": paired(J["ON"], J["OFF"], ids), "haiku_ON_minus_OFF": paired(J["ON_h"], J["OFF_h"], ids), "floor_metrics": fm})
    for q in ids:
        for a in pool: pool[a][q] = J[a][q]
        fam[q] = "SE" if p in SE else "topic"
if fails: print("\n".join(fails), file=sys.stderr); sys.exit(1)
for name, f in (("SE", "SE"), ("topic", "topic"), ("pooled", None)):
    ids = sorted(q for q in pool["ON"] if f is None or fam[q] == f)
    out[name] = {"OFF": setstats(pool["OFF"], ids), "ON": setstats(pool["ON"], ids), "ON_minus_OFF": paired(pool["ON"], pool["OFF"], ids),
                 "haiku_ON_minus_OFF": paired(pool["ON_h"], pool["OFF_h"], ids)}
ids = sorted(pool["ON"]); agr = {}
for a in ("OFF", "ON"):
    O, Hk = pool[a], pool[a + "_h"]
    so = np.array([O[q]["s"] for q in ids]); sh = np.array([Hk[q]["s"] for q in ids]); ro = np.array([O[q]["r"] for q in ids]); rh = np.array([Hk[q]["r"] for q in ids])
    agr[a] = {"winner_same": int(sum(O[q]["winner"] == Hk[q]["winner"] for q in ids)), "n": len(ids),
              "opus_winners": dict(collections.Counter(O[q]["winner"] for q in ids)), "haiku_winners": dict(collections.Counter(Hk[q]["winner"] for q in ids)),
              "ratio_opus": round(so.sum() / ro.sum(), 3), "ratio_haiku": round(sh.sum() / rh.sum(), 3),
              "r_boar_score": round(float(np.corrcoef(so, sh)[0, 1]), 3), "r_ratio_item": round(float(np.corrcoef(so / ro, sh / rh)[0, 1]), 3)}
dO = np.array([pool["ON"][q]["s"] / pool["ON"][q]["r"] - pool["OFF"][q]["s"] / pool["OFF"][q]["r"] for q in ids])
dH = np.array([pool["ON_h"][q]["s"] / pool["ON_h"][q]["r"] - pool["OFF_h"][q]["s"] / pool["OFF_h"][q]["r"] for q in ids])
agr["item_delta_r"] = round(float(np.corrcoef(dO, dH)[0, 1]), 3)
agr["item_delta_sign_agree"] = int(sum(np.sign(dO) == np.sign(dH)))
out["haiku_vs_opus"] = agr
d = out["pooled"]["ON_minus_OFF"]; lo, hi, x = d["d_raw_ci"][0], d["d_raw_ci"][1], d["d_raw"]
out["verdict"] = ("LEVER" if lo > 0 and x >= 0.03 else "SMALL" if lo > 0 else
                  "NO (not decided at MDE 0.03)" if abs(x) < 0.03 and lo <= 0 <= hi else "NO")
print(json.dumps(out, indent=1))
