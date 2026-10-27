#!/usr/bin/env python3
"""SELFTEST-SCORES analysis (0 LLM calls). Usage: python3 -I localjudge_agg.py [--calib-only] [--local] > ../aggregates/selftest-scores.json
Per-pack table uses the Haiku 5.5-low L1 rows (primary) unless --local (Qwen local-judge rows).
Calibration (qa-travel-se with pack): local Qwen judge vs Haiku 5.5-low rows on the same traces: winner agreement after combineOrders,
position consistency, ratio raw/above_min, per-dimension means. Per pack: raw / above_min for with (W) and without (N) pack, item
bootstrap CI (B 2000, seed 11; same estimator as floor_metrics.py with one run), paired Δ W−N (per-item bootstrap of the ratio-of-sums
difference, seed 11), win/tie/loss; pooled over all packs present (paired per item). Gen checks from ../aggregates/<run>.gen.json."""
import json, os, sys, collections, numpy as np
H = "<workspace>/rnd/research/coordinator/arms/pack-visa"; D = f"{H}/selftest-runs"; L = f"{D}/localjudge"; A = f"{H}/aggregates"
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
if "--packs" in sys.argv: PACKS = sys.argv[sys.argv.index("--packs") + 1].split(",")  # e.g. wave 3: --packs qa-cooking-se,qa-money-se
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
                  "winner": a["winner"] if a["winner"] == b["winner"] else "tie", "dims": {side: {k: (a[side][k] + b[side][k]) / 2 for k in K} for side in ("boar", "ref")}}
    return out
def ratios(S, R): return S.sum() / R.sum(), (S - 1).sum() / (R - 1).sum()
def boot(fn, n, B=2000, seed=11):
    rng = np.random.default_rng(seed); return np.array([fn(rng.integers(0, n, n)) for _ in range(B)])
ci = lambda x: [round(float(v), 3) for v in np.percentile(x, [2.5, 97.5])]
def setstats(d, ids):
    S = np.array([d[q]["s"] for q in ids]); R = np.array([d[q]["r"] for q in ids]); pt = ratios(S, R); b = boot(lambda ii: ratios(S[ii], R[ii]), len(ids))
    w = collections.Counter(d[q]["winner"] for q in ids)
    return {"n": len(ids), "raw": round(pt[0], 3), "raw_ci": ci(b[:, 0]), "above_min": round(pt[1], 3), "above_min_ci": ci(b[:, 1]),
            "win_tie_loss": [w["boar"], w["tie"], w["ref"]], "pos_consistency": round(sum(d[q]["consistent"] for q in ids) / len(ids), 3),
            "dims_boar": {k: round(float(np.mean([d[q]["dims"]["boar"][k] for q in ids])), 2) for k in K},
            "dims_ref": {k: round(float(np.mean([d[q]["dims"]["ref"][k] for q in ids])), 2) for k in K}}
def paired(W, N, ids):
    SW = np.array([W[q]["s"] for q in ids]); RW = np.array([W[q]["r"] for q in ids]); SN = np.array([N[q]["s"] for q in ids]); RN = np.array([N[q]["r"] for q in ids])
    f = lambda ii: [ratios(SW[ii], RW[ii])[j] - ratios(SN[ii], RN[ii])[j] for j in (0, 1)]
    pt = f(np.arange(len(ids))); b = boot(f, len(ids))
    return {"n": len(ids), "d_raw": round(pt[0], 3), "d_raw_ci": ci(b[:, 0]), "d_above_min": round(pt[1], 3), "d_above_min_ci": ci(b[:, 1]),
            "items_better_worse": [int(sum(W[q]["s"] > N[q]["s"] for q in ids)), int(sum(W[q]["s"] < N[q]["s"] for q in ids))]}
out = {}
# calibration
Q = load(f"{L}/st-qa-travel-se-cut7-s42.judgments.qwen36q2.jsonl"); Hk = load(f"{D}/st-qa-travel-se-cut7-s42.judgments.jsonl")
ids = sorted(set(Q) & set(Hk))
if ids:
    out["calibration"] = {"n": len(ids), "winner_agreement": round(sum(Q[q]["winner"] == Hk[q]["winner"] for q in ids) / len(ids), 3),
        "local": setstats(Q, ids), "haiku": setstats(Hk, ids),
        "pearson_boar_mean": round(float(np.corrcoef([Q[q]["s"] for q in ids], [Hk[q]["s"] for q in ids])[0, 1]), 3),
        "disagreements": {q: [Q[q]["winner"], Hk[q]["winner"]] for q in ids if Q[q]["winner"] != Hk[q]["winner"]}}
if "--calib-only" in sys.argv: print(json.dumps(out, indent=1)); sys.exit()
JS = "--local" in sys.argv  # per-pack table: Haiku 5.5-low rows (primary, selftest-runs/<run>.judgments.jsonl) or local rows (--local)
rows = []; pW = {}; pN = {}
for p in PACKS:
    W = load(f"{L}/st-{p}-cut7-s42.judgments.qwen36q2.jsonl" if JS else f"{D}/st-{p}-cut7-s42.judgments.jsonl")
    N = load(f"{L}/st-{p}-cut7-nopack-s42.judgments.qwen36q2.jsonl" if JS else f"{D}/st-{p}-cut7-nopack-s42.judgments.jsonl")
    ids = sorted(set(W) & set(N)); r = {"pack": p, "n_with": len(W), "n_without": len(N)}
    if ids and (len(ids) < len(W) or len(ids) < len(N)):  # audit F7: with/without/paired all on the same (paired) ids
        print(f"WARN {p}: unpaired ids skipped (with only: {sorted(set(W) - set(N))}, without only: {sorted(set(N) - set(W))})", file=sys.stderr)
    if W: r["with"] = setstats(W, ids if ids else sorted(W))
    if N: r["without"] = setstats(N, ids if ids else sorted(N))
    if ids: r["paired"] = paired(W, N, ids); pW.update({f"{p}|{q}": W[q] for q in ids}); pN.update({f"{p}|{q}": N[q] for q in ids})
    g = f"{A}/st-{p}-cut7-s42.gen.json"
    if os.path.exists(g):
        s = json.load(open(g))["summary"]; r["gen_with"] = {k: s[k] for k in ("kept_total", "kept_from_pack", "items_with_pack_kept", "fact_article_in_raw", "fact_article_in_kept", "p50_s", "errors")}
    g = f"{A}/st-{p}-cut7-nopack-s42.gen.json"
    if os.path.exists(g):
        s = json.load(open(g))["summary"]; r["gen_without"] = {k: s[k] for k in ("kept_total", "kept_from_pack", "fact_article_in_kept", "p50_s", "errors")}
    rows.append(r)
out["packs"] = rows
if pW:
    ids = sorted(pW); pk = sorted({k.split("|")[0] for k in ids})
    out["pooled"] = {"n_pooled": len(ids), "packs_pooled": pk, "with": setstats(pW, ids), "without": setstats(pN, ids), "paired": paired(pW, pN, ids)}
    print(f"pooled n={len(ids)} packs={len(pk)}/{len(PACKS)} {','.join(pk)}", file=sys.stderr)
print(json.dumps(out, indent=1))
