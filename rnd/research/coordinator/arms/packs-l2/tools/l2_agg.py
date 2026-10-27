#!/usr/bin/env python3
"""PACKS-L2 aggregation (0 LLM calls). Copy of packs/tools/localjudge_agg.py's estimator (load/ratios/boot/setstats/paired unchanged:
per-item bootstrap of the ratio-of-sums difference, B 2000, seed 11, paired on queryId), generalised to the cells
S-OFF, P-S, X-P (180 public self-test items) and wave-3 S-OFF (40, separate). Opus rows (*.judgments.opus.jsonl) primary; Haiku rows
(*.judgments.jsonl) computed separately on the same ids for calibration. Never pools Opus with Haiku rows.
Usage: python3 -I l2_agg.py <cell> [--out file.json]   cell in s_off|p_s|x_p|wave3_s_off|x_s"""
import json, os, sys, collections, numpy as np
ARMS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
SE = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se"]
TOPIC = ["boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
W3 = ["qa-cooking-se", "qa-money-se"]
def run(cell, p):
    return {"S": f"{ARMS}/packs/selftest-runs/st-{p}-cut7-s42", "OFF": f"{ARMS}/packs/selftest-runs/st-{p}-cut7-nopack-s42",
            "P": f"{ARMS}/crowdq/runs/st-{p}-cut7-all9-s42", "X": f"{ARMS}/stack/runs/st-{p}-cut7-stack-s42"}[cell]
CELLS = {"s_off": ("S", "OFF", SE + TOPIC), "p_s": ("P", "S", SE + TOPIC), "x_p": ("X", "P", SE + TOPIC),
         "x_s": ("X", "S", SE + TOPIC), "wave3_s_off": ("S", "OFF", W3)}
def load(p):
    J = collections.defaultdict(dict)
    if not os.path.exists(p): return {}
    for l in open(p):
        r = json.loads(l)
        if r.get("ok"): J[r["queryId"]][r["order"]] = r["mapped"]
    out = {}
    for q, v in J.items():
        if set(v) != {"boarA", "boarB"}:  # audit F7: never drop an item silently
            print(f"WARN {os.path.basename(p)}: {q} judged in order(s) {sorted(v)} only (needs boarA+boarB); item skipped", file=sys.stderr); continue
        a, b = v["boarA"], v["boarB"]
        out[q] = {"s": (mr(a["boar"]) + mr(b["boar"])) / 2, "r": (mr(a["ref"]) + mr(b["ref"])) / 2, "consistent": a["winner"] == b["winner"],
                  "winner": a["winner"] if a["winner"] == b["winner"] else "tie"}
    return out
def ratios(S, R): return S.sum() / R.sum(), (S - 1).sum() / (R - 1).sum()
def boot(fn, n, B=2000, seed=11):
    rng = np.random.default_rng(seed); return np.array([fn(rng.integers(0, n, n)) for _ in range(B)])
ci = lambda x: [round(float(v), 3) for v in np.percentile(x, [2.5, 97.5])]
def setstats(d, ids):
    S = np.array([d[q]["s"] for q in ids]); R = np.array([d[q]["r"] for q in ids]); pt = ratios(S, R); b = boot(lambda ii: ratios(S[ii], R[ii]), len(ids))
    w = collections.Counter(d[q]["winner"] for q in ids)
    return {"n": len(ids), "raw": round(pt[0], 3), "raw_ci": ci(b[:, 0]), "above_min": round(pt[1], 3), "above_min_ci": ci(b[:, 1]),
            "win_tie_loss": [w["boar"], w["tie"], w["ref"]], "pos_consistency": round(sum(d[q]["consistent"] for q in ids) / len(ids), 3)}
def paired(W, N, ids):
    SW = np.array([W[q]["s"] for q in ids]); RW = np.array([W[q]["r"] for q in ids]); SN = np.array([N[q]["s"] for q in ids]); RN = np.array([N[q]["r"] for q in ids])
    f = lambda ii: [ratios(SW[ii], RW[ii])[j] - ratios(SN[ii], RN[ii])[j] for j in (0, 1)]
    pt = f(np.arange(len(ids))); b = boot(f, len(ids))
    return {"n": len(ids), "d_raw": round(pt[0], 3), "d_raw_ci": ci(b[:, 0]), "d_above_min": round(pt[1], 3), "d_above_min_ci": ci(b[:, 1]),
            "items_better_worse": [int(sum(W[q]["s"] > N[q]["s"] for q in ids)), int(sum(W[q]["s"] < N[q]["s"] for q in ids))]}
def judge_rows(path):
    if not os.path.exists(path): return None
    r = [json.loads(l) for l in open(path) if l.strip()]
    return {"rows": len(r), "ok": sum(bool(x.get("ok")) for x in r), "judgeModel": sorted({str(x.get("judgeModel")) for x in r})}
cell = sys.argv[1]; hi, lo, packs = CELLS[cell]; out = {"cell": f"{hi}-{lo}", "estimator": "per-item bootstrap ratio-of-sums diff, B 2000, seed 11, paired on queryId", "judges": {}}
pools = {j: {"W": {}, "N": {}, "fam": {}} for j in ("opus", "haiku")}; out["packs"] = []
for p in packs:
    row = {"pack": p, "family": "SE" if p in SE + W3 else "topic"}
    for j, suf in (("opus", ".judgments.opus.jsonl"), ("haiku", ".judgments.jsonl")):
        fW, fN = run(hi, p) + suf, run(lo, p) + suf
        W, N = load(fW), load(fN); ids = sorted(set(W) & set(N))
        row[j] = {"files": {hi: fW, lo: fN}, "rows": {hi: judge_rows(fW), lo: judge_rows(fN)}, "n_paired": len(ids)}
        if len(ids) != 20 and (W or N): print(f"WARN {cell} {j} {p}: n_paired={len(ids)} (W {len(W)}, N {len(N)}) != 20; pack left out of the pool", file=sys.stderr)  # audit F7
        if len(ids) == 20:
            row[j].update({hi: setstats(W, ids), lo: setstats(N, ids), "paired": paired(W, N, ids)})
            for q in ids: k = f"{p}|{q}"; pools[j]["W"][k] = W[q]; pools[j]["N"][k] = N[q]; pools[j]["fam"][k] = row["family"]
    out["packs"].append(row)
for j in ("opus", "haiku"):
    W, N, fam = pools[j]["W"], pools[j]["N"], pools[j]["fam"]; res = {}
    groups = {"pooled": sorted(W)}
    if cell != "wave3_s_off": groups.update({"SE": sorted(k for k in W if fam[k] == "SE"), "topic": sorted(k for k in W if fam[k] == "topic")})
    for g, ids in groups.items():
        if ids: res[g] = {hi: setstats(W, ids), lo: setstats(N, ids), "paired": paired(W, N, ids), "packs_complete": sorted({k.split("|")[0] for k in ids})}
    out["judges"][j] = res
o = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
if o: json.dump(out, open(o, "w"), indent=1)
for j in ("opus", "haiku"):
    for g, r in out["judges"][j].items():
        p = r["paired"]; print(f"{cell} {j:5s} {g:6s} n={p['n']:3d} {hi} {r[hi]['raw']:.3f} {lo} {r[lo]['raw']:.3f} d_raw {p['d_raw']:+.3f} ({p['d_raw_ci'][0]:+.3f}..{p['d_raw_ci'][1]:+.3f}) d_above_min {p['d_above_min']:+.3f} ({p['d_above_min_ci'][0]:+.3f}..{p['d_above_min_ci'][1]:+.3f}) better/worse {p['items_better_worse'][0]}/{p['items_better_worse'][1]} packs={len(r['packs_complete'])}/{len(packs)} {','.join(r['packs_complete'])}")
for row in out["packs"]:
    s = " ".join(f"{j} {row[j]['paired']['d_raw']:+.3f} ({row[j]['paired']['d_raw_ci'][0]:+.3f}..{row[j]['paired']['d_raw_ci'][1]:+.3f}) b/w {row[j]['paired']['items_better_worse'][0]}/{row[j]['paired']['items_better_worse'][1]}" if "paired" in row[j] else f"{j} n_paired={row[j]['n_paired']}" for j in ("opus", "haiku"))
    print(f"{cell} pack {row['pack']:20s} {s}")
