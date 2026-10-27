#!/usr/bin/env python3
"""DENSECHUNK-ST2 stages 2-3 analysis (0 LLM calls). Usage: python3 -I st2_agg.py > ../aggregates/st2-stage2.json
OFF = arms/packs/selftest-runs/st-<p>-cut7-s42 (traces + Haiku 5.5-low judgments, SELFTEST-SCORES); ON = runs/judge/st2-<p>-cut7-s42.
Per pack / family (SE Q&A vs topic) / pooled 180: raw, above_min with item bootstrap CI; paired ON-OFF delta (item bootstrap, seed 11, B 2000);
gen checks from aggregates (OFF: arms/packs/aggregates/<run>.gen.json; ON: aggregates/st2-<p>-cut7-s42.gen.json); retrieval diagnostics from traces
(OFF raw is a prefix of ON raw; appended dense chunks kept; OFF-kept chunk cut; lost-context items; identical answers when kept unchanged).
Estimators = arms/packs/tools/selftest_deep_agg.py (copied)."""
import json, os, statistics, collections, numpy as np
AR = "<workspace>/rnd/research/coordinator/arms"; OD = f"{AR}/packs/selftest-runs"; OA = f"{AR}/packs/aggregates"
ND = f"{AR}/densechunk-st/runs/judge"; NA = f"{AR}/densechunk-st/aggregates"
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
SE = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se"]; TOP = ["boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
def load(p):
    J = collections.defaultdict(dict)
    for l in open(p):
        r = json.loads(l)
        if r.get("ok"): J[r["queryId"]][r["order"]] = r["mapped"]
    return {q: {"s": (mr(v["boarA"]["boar"]) + mr(v["boarB"]["boar"])) / 2, "r": (mr(v["boarA"]["ref"]) + mr(v["boarB"]["ref"])) / 2,
                "winner": v["boarA"]["winner"] if v["boarA"]["winner"] == v["boarB"]["winner"] else "tie"} for q, v in J.items() if len(v) == 2}
def ratios(S, R): return S.sum() / R.sum(), (S - 1).sum() / (R - 1).sum()
def boot(fn, n, B=2000, seed=11):
    rng = np.random.default_rng(seed); return np.array([fn(rng.integers(0, n, n)) for _ in range(B)])
ci = lambda x: [round(float(v), 3) for v in np.percentile(x, [2.5, 97.5])]
def setstats(d, ids):
    S = np.array([d[q]["s"] for q in ids]); R = np.array([d[q]["r"] for q in ids]); pt = ratios(S, R); b = boot(lambda ii: ratios(S[ii], R[ii]), len(ids))
    w = collections.Counter(d[q]["winner"] for q in ids)
    return {"n": len(ids), "raw": round(pt[0], 3), "raw_ci": ci(b[:, 0]), "above_min": round(pt[1], 3), "above_min_ci": ci(b[:, 1]), "win_tie_loss": [w["boar"], w["tie"], w["ref"]]}
def paired(W, N, ids):
    SW = np.array([W[q]["s"] for q in ids]); RW = np.array([W[q]["r"] for q in ids]); SN = np.array([N[q]["s"] for q in ids]); RN = np.array([N[q]["r"] for q in ids])
    f = lambda ii: [ratios(SW[ii], RW[ii])[j] - ratios(SN[ii], RN[ii])[j] for j in (0, 1)]
    pt = f(np.arange(len(ids))); b = boot(f, len(ids))
    return {"n": len(ids), "d_raw": round(pt[0], 3), "d_raw_ci": ci(b[:, 0]), "d_above_min": round(pt[1], 3), "d_above_min_ci": ci(b[:, 1]),
            "items_better_worse": [int(sum(W[q]["s"] > N[q]["s"] for q in ids)), int(sum(W[q]["s"] < N[q]["s"] for q in ids))]}
def traces(p): return {(t := json.loads(l))["itemId"]: t for l in open(p)}
key = lambda s: (s.get("title"), s.get("section"), s.get("source"))
out = {"criterion_sha256_prefix": "6c7b12dd", "judge": "claude-haiku-5-5 effort low, judge.v1, N=4 shards, both orders", "packs": []}
pool = {"OFF": {}, "ON": {}}; diag_pool = collections.Counter(); tms = {"OFF": [], "ON": []}; items_family = {}
gk = ("kept_total", "kept_from_pack", "items_with_pack_kept", "fact_article_in_raw", "fact_article_in_kept", "fact_article_shown", "p50_s", "errors", "nonempty", "median_words")
for p in SE + TOP:
    on_j = f"{ND}/st2-{p}-cut7-s42.judgments.jsonl"
    if not os.path.exists(on_j): continue
    OFF, ON = load(f"{OD}/st-{p}-cut7-s42.judgments.jsonl"), load(on_j); ids = sorted(set(OFF) & set(ON))
    TO, TN = traces(f"{OD}/st-{p}-cut7-s42.traces.jsonl"), traces(f"{ND}/st2-{p}-cut7-s42.traces.jsonl")
    dg = collections.Counter()
    for q in TO:
        o, n = TO[q], TN.get(q)
        if not n: continue
        ro, rn = [key(s) for s in o["retrieval"]["raw"]], [key(s) for s in n["retrieval"]["raw"]]
        ko, kn = {key(s) for s in o["retrieval"]["kept"]}, {key(s) for s in n["retrieval"]["kept"]}
        app = rn[len(ro):]
        dg["items"] += 1; dg["off_prefix"] += rn[:len(ro)] == ro; dg["items_appended"] += bool(app); dg["appended_chunks"] += len(app)
        dg["appended_kept"] += sum(a in kn and a not in set(ro) for a in app); dg["items_appended_kept"] += any(a in kn and a not in set(ro) for a in app)
        dg["items_offkept_cut"] += bool(ko - kn); dg["lost_context"] += bool(ko) and not kn; dg["gained_context"] += (not ko) and bool(kn)
        dg["kept_unchanged"] += ko == kn; dg["kept_unchanged_same_answer"] += ko == kn and o["answer"]["text"] == n["answer"]["text"]
        tms["OFF"].append(o["timing"]["totalMs"]); tms["ON"].append(n["timing"]["totalMs"])
    diag_pool.update(dg)
    gen = {"OFF": {k: json.load(open(f"{OA}/st-{p}-cut7-s42.gen.json"))["summary"].get(k) for k in gk},
           "ON": {k: json.load(open(f"{NA}/st2-{p}-cut7-s42.gen.json"))["summary"].get(k) for k in gk}}
    out["packs"].append({"pack": p, "family": "SE" if p in SE else "topic", "OFF": setstats(OFF, ids), "ON": setstats(ON, ids), "ON_minus_OFF": paired(ON, OFF, ids), "gen": gen, "retrieval": dict(dg)})
    for q in ids: pool["OFF"][q] = OFF[q]; pool["ON"][q] = ON[q]; items_family[q] = "SE" if p in SE else "topic"
for name, fam in (("SE", "SE"), ("topic", "topic"), ("pooled", None)):
    ids = sorted(q for q in pool["ON"] if fam is None or items_family[q] == fam)
    if ids: out[name] = {"OFF": setstats(pool["OFF"], ids), "ON": setstats(pool["ON"], ids), "ON_minus_OFF": paired(pool["ON"], pool["OFF"], ids)}
out["retrieval_pooled"] = dict(diag_pool)
out["p50_s"] = {k: round(statistics.median(v) / 1000, 1) for k, v in tms.items() if v}
d = out.get("pooled", {}).get("ON_minus_OFF")
if d:
    lo, x = d["d_raw_ci"][0], d["d_raw"]
    out["verdict"] = ("LEVER" if lo > 0 and x >= 0.03 else "SMALL" if lo > 0 else
                      "NO (not decided at MDE 0.03)" if abs(x) < 0.03 and d["d_raw_ci"][0] <= 0 <= d["d_raw_ci"][1] else "NO")
print(json.dumps(out, indent=1))
