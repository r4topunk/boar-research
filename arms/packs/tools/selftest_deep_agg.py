#!/usr/bin/env python3
"""SELFTEST-DEEP analysis (0 LLM calls). Usage: python3 -I selftest_deep_agg.py > ../aggregates/selftest-deep.json
Haiku 5.5-low rows. Per pack: H with pack (st-<p>-dt512-s42), H without (st-<p>-dt512-nopack-s42), 4B with (st-<p>-cut7-s42, SELFTEST-SCORES);
raw / above_min with item bootstrap CI; paired H with - H without, and H with - 4B with (same items); pooled over packs present.
Estimators copied from localjudge_agg.py (B 2000, seed 11). Gen/think stats from ../aggregates/<run>.{gen,think}.json."""
import json, os, sys, collections, numpy as np
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); D = f"{H}/selftest-runs"; DD = f"{D}/deep"; A = f"{H}/aggregates"
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
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
out = {"packs": []}; pool = {k: {} for k in ("HW", "HN", "BW")}
gk = ("kept_total", "kept_from_pack", "items_with_pack_kept", "fact_article_in_raw", "fact_article_in_kept", "p50_s", "errors", "nonempty", "median_words")
for p in PACKS:
    S = {"HW": load(f"{DD}/st-{p}-dt512-s42.judgments.jsonl"), "HN": load(f"{DD}/st-{p}-dt512-nopack-s42.judgments.jsonl"), "BW": load(f"{D}/st-{p}-cut7-s42.judgments.jsonl")}
    r = {"pack": p}
    for k, v in S.items():
        if len(v) == 20: r[k] = setstats(v, sorted(v))
        else: print(f"WARN {p} {k}: {len(v)} of 20 items with both orders; pack not in the {k} pool", file=sys.stderr)  # audit F7
    if len(S["HW"]) == 20 and len(S["HN"]) == 20:
        ids = sorted(set(S["HW"]) & set(S["HN"])); r["H_with_vs_without"] = paired(S["HW"], S["HN"], ids)
        for k in ("HW", "HN"): pool[k].update({f"{p}|{q}": S[k][q] for q in ids})
    if len(S["HW"]) == 20 and len(S["BW"]) == 20:
        ids = sorted(set(S["HW"]) & set(S["BW"])); r["Hwith_vs_4Bwith"] = paired(S["HW"], S["BW"], ids)
        pool["BW"].update({f"{p}|{q}": S["BW"][q] for q in ids})
    for tag, run in (("gen_with", f"st-{p}-dt512-s42"), ("gen_without", f"st-{p}-dt512-nopack-s42")):
        g = f"{A}/{run}.gen.json"; t = f"{A}/{run}.think.json"
        if os.path.exists(g): s = json.load(open(g))["summary"]; r[tag] = {k: s.get(k) for k in gk}
        if os.path.exists(t): a = json.load(open(t))["aggregate"]; r[tag].update({"deepThinking": a["deepThinkingRouted"], "n": a["n"], "reasoningMedian": a["reasoningTokens"]["median"], "zeroReasoning": a["reasoningTokens"]["zero"]})
    out["packs"].append(r)
ids = sorted(set(pool["HW"]) & set(pool["HN"])); ids2 = sorted(set(pool["HW"]) & set(pool["BW"]))
pk = lambda ii: sorted({k.split("|")[0] for k in ii})
if ids: print(f"pooled H_with_vs_without n={len(ids)} packs={len(pk(ids))}/{len(PACKS)} {','.join(pk(ids))}", file=sys.stderr)
if ids2: print(f"pooled Hwith_vs_4Bwith n={len(ids2)} packs={len(pk(ids2))}/{len(PACKS)} {','.join(pk(ids2))}", file=sys.stderr)
if ids: out["pooled"] = {"n": len(ids), "packs_pooled": pk(ids), "H_with": setstats(pool["HW"], ids), "H_without": setstats(pool["HN"], ids), "H_with_vs_without": paired(pool["HW"], pool["HN"], ids)}
if ids2: out.setdefault("pooled", {}).update({"n_vs4B": len(ids2), "packs_pooled_vs4B": pk(ids2), "4B_with": setstats(pool["BW"], ids2), "Hwith_vs_4Bwith": paired(pool["HW"], pool["BW"], ids2)})
print(json.dumps(out, indent=1))
