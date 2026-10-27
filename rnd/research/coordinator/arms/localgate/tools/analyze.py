#!/usr/bin/env python3
"""LOCALGATE analysis: local verdicts vs cached jev probabilities. Counts/rates only.
usage: analyze.py --engine qwen [--engine laya ...]  -> aggregates/localgate.json + stdout tables
jev label at threshold t: jev_p >= t. Primary gate t = 0.7 (both sides). Strata weights (type, src, jev band) =
available/sampled, for population-weighted agreement / FPR."""
import json, argparse, collections, os
D = "<private held-out dir>"; OUT = "<workspace>/rnd/research/coordinator/arms/localgate/aggregates/localgate.json"
ap = argparse.ArgumentParser(); ap.add_argument("--engine", action="append", default=[]); a = ap.parse_args()
S = {};
for l in open(f"{D}/sample.jsonl"):
    r = json.loads(l); S[(r["rid"], r["type"])] = dict(src=r["src"], jev=r["jev_p"])
meta = json.load(open(f"{D}/sample-meta.json"))
def band(p): return "pos" if p >= 0.7 else ("neg" if p < 0.3 else "mid")
def auc(pos, neg):
    if not pos or not neg: return None
    w = 0.0
    for x in pos:
        for y in neg: w += 1.0 if x > y else (0.5 if x == y else 0.0)
    return w / (len(pos) * len(neg))
res = {"rule": "PASS iff agreement >= 0.90 AND FPR on jev-negatives <= 0.05 (gate threshold 0.7 both sides), >= 500 requests per type",
       "sample": meta["sample"], "available": meta["available"], "engines": {}}
for eng in a.engine:
    E = {}
    for t in ("has_fact", "quote_supports"):
        fp = f"{D}/{eng}-{t}.jsonl"
        if not os.path.exists(fp): continue
        V = [json.loads(l) for l in open(fp)]
        rows = [(S[(v["rid"], t)], v["p_local"], v.get("ms")) for v in V if (v["rid"], t) in S]
        nsamp = collections.Counter((s["src"], band(s["jev"])) for s, _, _ in rows)
        wt = {k: meta["available"].get(f"{t}|{k[0]}|{k[1]}", 0) / n for k, n in nsamp.items()}
        out = dict(n=len(rows))
        for th in (0.6, 0.7, 0.8):
            cm = collections.Counter(); wcm = collections.Counter()
            for s, p, _ in rows:
                k = ("J" if s["jev"] >= th else "j") + ("L" if p >= th else "l"); cm[k] += 1; wcm[k] += wt[(s["src"], band(s["jev"]))]
            def rates(c):
                n = sum(c.values()); neg = c["jl"] + c["jL"]; pos = c["JL"] + c["Jl"]
                return dict(agreement=round((c["JL"] + c["jl"]) / n, 4), fpr=round(c["jL"] / neg, 4) if neg else None, fnr=round(c["Jl"] / pos, 4) if pos else None)
            out[f"t{th}"] = dict(confusion={"jevT_locT": cm["JL"], "jevT_locF": cm["Jl"], "jevF_locT": cm["jL"], "jevF_locF": cm["jl"]}, sample=rates(cm), pop_weighted=rates(wcm))
        # strict negatives (jev p < 0.3)
        sn = [p for s, p, _ in rows if s["jev"] < 0.3]; out["fpr_strict_neg_p<0.3_at0.7"] = round(sum(p >= 0.7 for p in sn) / len(sn), 4) if sn else None
        out["auc_vs_jev0.7"] = round(auc([p for s, p, _ in rows if s["jev"] >= 0.7], [p for s, p, _ in rows if s["jev"] < 0.7]), 4)
        bins = [0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0001]; cal = []
        for lo, hi in zip(bins, bins[1:]):
            B = [s for s, p, _ in rows if lo <= p < hi]
            cal.append(dict(local_p=f"[{lo},{min(hi,1)}{']' if hi > 1 else ')'}", n=len(B), jev_pos_rate=round(sum(s["jev"] >= 0.7 for s in B) / len(B), 3) if B else None,
                            jev_mean_p=round(sum(s["jev"] for s in B) / len(B), 3) if B else None))
        out["calibration"] = cal
        by = {}
        for src in sorted({s["src"] for s, _, _ in rows}):
            R = [(s, p) for s, p, _ in rows if s["src"] == src]
            neg = [p for s, p in R if s["jev"] < 0.7]
            by[src] = dict(n=len(R), agreement=round(sum((s["jev"] >= 0.7) == (p >= 0.7) for s, p in R) / len(R), 4), fpr=round(sum(p >= 0.7 for p in neg) / len(neg), 4) if neg else None)
        out["by_src_t0.7"] = by
        ms = sorted(m for _, _, m in rows if m is not None)
        if ms:
            mean = sum(ms) / len(ms); out["timing"] = dict(mean_ms=round(mean), p50_ms=ms[len(ms) // 2], p90_ms=ms[int(len(ms) * .9)], req_per_s=round(1000 / mean, 3),
                                                         shard_pass_2800_min=round(2800 * mean / 60000, 1))
        pt = out["t0.7"]["sample"]; out["verdict"] = "PASS" if (len(rows) >= 500 and pt["agreement"] >= 0.90 and pt["fpr"] <= 0.05) else "FAIL"
        E[t] = out
        print(eng, t, json.dumps({k: out[k] for k in ("n", "verdict", "auc_vs_jev0.7")}), json.dumps(out["t0.7"]), json.dumps(out.get("timing")))
    res["engines"][eng] = E
json.dump(res, open(OUT, "w"), indent=1)
