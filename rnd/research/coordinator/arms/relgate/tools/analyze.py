#!/usr/bin/env python3
"""RELGATE analysis per the frozen criterion (RELGATE-criterion.md, sha256 10b462f8...).
usage: analyze.py [--audit]   -> writes ../aggregates/relgate.json, prints a summary."""
import json, os, sys, random, math
from collections import defaultdict

ARM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D, R = f"{ARM}/data", f"{ARM}/runs"
PHONE_PREFILL = 47.6
K = [json.loads(l) for l in open(f"{D}/contexts.jsonl")]
C = [json.loads(l) for l in open(f"{D}/chunks.jsonl")]
S = [json.loads(l) for l in open(f"{D}/safety.jsonl")]
Kid = {k["id"]: k for k in K}

def auc(pos, neg):
    if not pos or not neg: return None
    s = 0.0
    for p in pos:
        for n in neg:
            s += 1.0 if p > n else (0.5 if p == n else 0.0)
    return s / (len(pos) * len(neg))

def boot_auc(rows, score, label, cluster, n=2000, seed=31):
    """rows: list of dicts; cluster bootstrap by item id."""
    by = defaultdict(list)
    for r in rows: by[cluster(r)].append(r)
    keys = sorted(by); rnd = random.Random(seed); vals = []
    for _ in range(n):
        smp = [r for k in (rnd.choice(keys) for _ in keys) for r in by[k]]
        a = auc([score(r) for r in smp if label(r)], [score(r) for r in smp if not label(r)])
        if a is not None: vals.append(a)
    vals.sort()
    return [round(vals[int(0.025 * len(vals))], 3), round(vals[int(0.975 * len(vals)) - 1], 3)]

def prf(rows, score, label, t):
    tp = sum(1 for r in rows if score(r) >= t and label(r)); fp = sum(1 for r in rows if score(r) >= t and not label(r))
    fn = sum(1 for r in rows if score(r) < t and label(r)); tn = sum(1 for r in rows if score(r) < t and not label(r))
    p = tp / (tp + fp) if tp + fp else 0.0; rc = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * rc / (p + rc) if p + rc else 0.0
    return {"t": t, "precision": round(p, 3), "recall": round(rc, 3), "f1": round(f, 3), "tp": tp, "fp": fp, "fn": fn, "tn": tn}

def best_f1_t(rows, score, label):
    cands = sorted({score(r) for r in rows})
    best = max(cands, key=lambda t: (prf(rows, score, label, t)["f1"], -t))
    return best

BINS = [0, .1, .3, .5, .7, .9, 1.0001]
def calib(rows, score, label):
    out = []
    for lo, hi in zip(BINS, BINS[1:]):
        b = [r for r in rows if lo <= score(r) < hi]
        out.append({"bin": f"[{lo},{min(hi,1)})", "n": len(b), "pos_rate": round(sum(label(r) for r in b) / len(b), 3) if b else None})
    ends = sum(1 for r in rows if score(r) < .1 or score(r) >= .9) / len(rows)
    band = sum(1 for r in rows if .3 <= score(r) < .7) / len(rows)
    return {"bins": out, "end_bins_share": round(ends, 3), "band_0.3_0.7_share": round(band, 3)}

def pct(xs, q):
    xs = sorted(xs); return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else None

def load(model):
    f = f"{R}/{model}.jsonl"
    if not os.path.exists(f): return None
    return {json.loads(l)["key"]: json.loads(l) for l in open(f)}

res = {"criterion_sha256": open(f"{ARM}/RELGATE-criterion.sha256").read().split()[0], "phone_prefill_tok_s": PHONE_PREFILL, "models": {}}
for model in [m for m in ("m4", "q17") if m in os.environ.get("MODELS", "m4,q17").split(",")]:
    run = load(model)
    if not run: continue
    M = {}
    # ---- G1
    lab = lambda r: r["label"]
    g1 = {}
    for w in ("W1", "W2", "W3"):
        rows = [dict(c, s=run[f"{c['cid']}|G1|{w}"]["p"]) for c in C if f"{c['cid']}|G1|{w}" in run]
        A = [r for r in rows if r["half"] == "A"]; B = [r for r in rows if r["half"] == "B"]
        sc = lambda r: r["s"]
        g1[w] = {"n": len(rows), "auc_A": round(auc([r["s"] for r in A if r["label"]], [r["s"] for r in A if not r["label"]]) or 0, 3),
                 "auc_B": round(auc([r["s"] for r in B if r["label"]], [r["s"] for r in B if not r["label"]]) or 0, 3),
                 "_rows": rows}
    wsel = max(g1, key=lambda w: g1[w]["auc_A"])
    rows = g1[wsel]["_rows"]; A = [r for r in rows if r["half"] == "A"]; B = [r for r in rows if r["half"] == "B"]
    sc = lambda r: r["s"]
    tA = best_f1_t(A, sc, lab)
    rank = lambda r: 1.0 / r["rank"]
    rank_auc_B = auc([rank(r) for r in B if r["label"]], [rank(r) for r in B if not r["label"]])
    G1 = {"wordings": {w: {k: v for k, v in g1[w].items() if k != "_rows"} for w in g1}, "selected": wsel,
          "auc_B": g1[wsel]["auc_B"], "auc_B_ci": boot_auc(B, sc, lab, lambda r: r["id"]),
          "threshold_A": tA, "at_A_threshold_on_A": prf(A, sc, lab, tA), "at_A_threshold_on_B": prf(B, sc, lab, tA),
          "at_0.5_on_B": prf(B, sc, lab, 0.5),
          "rank_baseline_auc_B": round(rank_auc_B, 3), "calibration_all": calib(rows, sc, lab),
          "auc_54_all": round(auc([r["s"] for r in rows if r["in54"] and r["label"]], [r["s"] for r in rows if r["in54"] and not r["label"]]), 3),
          "by_pack_auc_all": {p: round(auc([r["s"] for r in rows if r["pack"] == p and r["label"]], [r["s"] for r in rows if r["pack"] == p and not r["label"]]) or float("nan"), 3)
                              for p in sorted({r["pack"] for r in rows})}}
    # rule
    G1["rule"] = {"auc_B>=0.85": G1["auc_B"] >= 0.85, "f1_B>=0.70": G1["at_A_threshold_on_B"]["f1"] >= 0.70,
                  "auc_B>=rank+0.05": G1["auc_B"] >= rank_auc_B + 0.05}
    G1["verdict"] = "PASS" if all(G1["rule"].values()) else "FAIL"
    # G1 aggregated to context level (max over chunks) as a sufficiency score, reported only
    mx = defaultdict(float)
    for r in rows: mx[r["id"]] = max(mx[r["id"]], r["s"])
    KB = [k for k in K if k["half"] == "B"]
    G1["max_over_chunks_auc_K_B"] = round(auc([mx[k["id"]] for k in KB if k["label"]], [mx[k["id"]] for k in KB if not k["label"]]), 3)
    # G1 tokens (selected wording): total prompt length per chunk = cache_n + prompt_n
    tok_chunk = [run[f"{c['cid']}|G1|{wsel}"]["cache_n"] + run[f"{c['cid']}|G1|{wsel}"]["prompt_n"] for c in C if f"{c['cid']}|G1|{wsel}" in run]
    per_item = defaultdict(int)
    for c in C:
        k = f"{c['cid']}|G1|{wsel}"
        if k in run: per_item[c["id"]] += run[k]["cache_n"] + run[k]["prompt_n"]
    G1["tokens"] = {"per_chunk_p50": pct(tok_chunk, .5), "per_item_unshared_p50": pct(list(per_item.values()), .5), "per_item_unshared_p90": pct(list(per_item.values()), .9),
                    "phone_s_per_item_p50_unshared": round(pct(list(per_item.values()), .5) / PHONE_PREFILL, 1)}
    M["G1"] = G1
    # ---- G2
    rows = [dict(k, s=run[f"{k['id']}|G2"]["p"]) for k in K if f"{k['id']}|G2" in run]
    A = [r for r in rows if r["half"] == "A"]; B = [r for r in rows if r["half"] == "B"]
    posA = sorted([r["s"] for r in A if r["label"]], reverse=True)
    need = math.ceil(0.90 * len(posA)); tstar = posA[need - 1]
    recB = sum(1 for r in B if r["label"] and r["s"] >= tstar) / sum(1 for r in B if r["label"])
    catchB = sum(1 for r in B if not r["label"] and r["s"] < tstar) / sum(1 for r in B if not r["label"])
    aucB = auc([r["s"] for r in B if r["label"]], [r["s"] for r in B if not r["label"]])
    G2 = {"n": len(rows), "auc_A": round(auc([r["s"] for r in A if r["label"]], [r["s"] for r in A if not r["label"]]), 3),
          "auc_B": round(aucB, 3), "auc_B_ci": boot_auc(B, sc, lab, lambda r: r["id"]),
          "t_star": tstar, "B_pos_recall": round(recB, 3), "B_neg_catch": round(catchB, 3),
          "at_A_bestF1_on_B": prf(B, sc, lab, best_f1_t(A, sc, lab)), "at_0.5_on_B": prf(B, sc, lab, 0.5),
          "auc_B_vs_label_all": round(auc([r["s"] for r in B if r["label_all"]], [r["s"] for r in B if not r["label_all"]]), 3),
          "auc_54_all": round(auc([r["s"] for r in rows if r["in54"] and r["label"]], [r["s"] for r in rows if r["in54"] and not r["label"]]), 3),
          "calibration_all": calib(rows, sc, lab)}
    G2["rule"] = {"auc_B>=0.80": aucB >= 0.80, "B_pos_recall>=0.85": recB >= 0.85, "B_neg_catch>=0.40": catchB >= 0.40}
    G2["verdict"] = "PASS" if all(G2["rule"].values()) else "FAIL"
    ex = [run[f"{k['id']}|G2"] for k in K if f"{k['id']}|G2" in run]; mn = [run[f"{k['id']}|main"] for k in K if f"{k['id']}|main" in run]
    G2["cost"] = {"extra_prompt_tokens_p50": pct([e["prompt_n"] for e in ex], .5), "extra_ms_p50_host": pct([e["prompt_ms"] for e in ex], .5),
                  "main_prefill_tokens_p50": pct([m["prompt_n"] for m in mn], .5), "main_prefill_ms_p50_host": pct([m["prompt_ms"] for m in mn], .5),
                  "phone_extra_s_p50": round(pct([e["prompt_n"] for e in ex], .5) / PHONE_PREFILL, 2),
                  "phone_main_prefill_s_p50": round(pct([m["prompt_n"] for m in mn], .5) / PHONE_PREFILL, 1)}
    M["G2"] = G2
    # ---- G3
    g3 = []
    for k in K:
        r = run.get(f"{k['id']}|G3")
        if not r: continue
        d = r["digits"]; N = k["n_src"]
        pick = max(range(1, N + 1), key=lambda i: d.get(str(i), 0))
        tot = sum(d.values()) or 1
        g3.append(dict(k, pick=pick, p0=d["0"] / tot, hit=pick in k["pos_nums"], base=1 in k["pos_nums"],
                       oor=sum(v for kk, v in d.items() if int(kk) > N or (int(kk) == 0 and False)) / tot))
    for half_ in ("A", "B"):
        P = [r for r in g3 if r["half"] == half_ and r["label"]]
        M.setdefault("G3", {})[f"top1_hit_{half_}"] = round(sum(r["hit"] for r in P) / len(P), 3)
        M["G3"][f"always1_hit_{half_}"] = round(sum(r["base"] for r in P) / len(P), 3)
        M["G3"][f"n_pos_{half_}"] = len(P)
    B = [r for r in g3 if r["half"] == "B"]
    M["G3"]["none_score_auc_B"] = round(auc([1 - r["p0"] for r in B if r["label"]], [1 - r["p0"] for r in B if not r["label"]]), 3)
    M["G3"]["argmax_is_0_on_B_neg"] = round(sum(1 for r in B if not r["label"] and r["p0"] > max(run[f"{r['id']}|G3"]["digits"].get(str(i), 0) for i in range(1, r["n_src"] + 1)) / (sum(run[f"{r['id']}|G3"]["digits"].values()) or 1)) / max(1, sum(1 for r in B if not r["label"])), 3)
    M["G3"]["argmax_is_0_on_B_pos"] = round(sum(1 for r in B if r["label"] and r["p0"] > max(run[f"{r['id']}|G3"]["digits"].get(str(i), 0) for i in range(1, r["n_src"] + 1)) / (sum(run[f"{r['id']}|G3"]["digits"].values()) or 1)) / max(1, sum(1 for r in B if r["label"])), 3)
    M["G3"]["digit_mass_p50"] = round(pct([run[f"{k['id']}|G3"]["mass"] for k in K if f"{k['id']}|G3" in run], .5), 4)
    M["G3"]["rule"] = {"top1_B>=0.70": M["G3"]["top1_hit_B"] >= 0.70, "beats_always1_by_0.10": M["G3"]["top1_hit_B"] >= M["G3"]["always1_hit_B"] + 0.10}
    M["G3"]["verdict"] = "PASS" if all(M["G3"]["rule"].values()) else "FAIL"
    ex3 = [run[f"{k['id']}|G3"] for k in K if f"{k['id']}|G3" in run]
    M["G3"]["cost"] = {"extra_prompt_tokens_p50": pct([e["prompt_n"] for e in ex3], .5), "extra_ms_p50_host": pct([e["prompt_ms"] for e in ex3], .5),
                       "phone_extra_s_p50": round(pct([e["prompt_n"] for e in ex3], .5) / PHONE_PREFILL, 2)}
    # ---- Safety
    s1 = [dict(s, s=run[f"{s['sid']}|S1|{wsel}"]["p"]) for s in S if f"{s['sid']}|S1|{wsel}" in run]
    s2 = [dict(s, s=run[f"{s['sid']}|S2"]["p"]) for s in S if f"{s['sid']}|S2" in run]
    SAFE = {}
    if s1:
        SAFE["G1"] = {"n": len(s1), "auc": round(auc([r["s"] for r in s1 if r["label"]], [r["s"] for r in s1 if not r["label"]]), 3),
                      "pos_below_t": sum(1 for r in s1 if r["label"] and r["s"] < M["G1"]["threshold_A"]),
                      "neg_above_t": sum(1 for r in s1 if not r["label"] and r["s"] >= M["G1"]["threshold_A"]),
                      "pos_below_ids": [r["id"] for r in s1 if r["label"] and r["s"] < M["G1"]["threshold_A"]]}
        SAFE["G1"]["pass"] = SAFE["G1"]["auc"] >= 0.90 and SAFE["G1"]["pos_below_t"] <= 1
    if s2:
        SAFE["G2"] = {"n": len(s2), "auc": round(auc([r["s"] for r in s2 if r["label"]], [r["s"] for r in s2 if not r["label"]]), 3),
                      "pos_below_t": sum(1 for r in s2 if r["label"] and r["s"] < tstar),
                      "neg_above_t": sum(1 for r in s2 if not r["label"] and r["s"] >= tstar),
                      "pos_below_ids": [r["id"] for r in s2 if r["label"] and r["s"] < tstar]}
        SAFE["G2"]["pass"] = SAFE["G2"]["auc"] >= 0.90 and SAFE["G2"]["pos_below_t"] <= 1
    M["SAFETY"] = SAFE
    M["p_fallback_0.5"] = sum(1 for v in run.values() if v.get("mass", 1) == 0)
    res["models"][model] = M

if "m4" in res["models"] and "q17" in res["models"]:
    m, q = res["models"]["m4"], res["models"]["q17"]
    res["q17_vs_m4"] = {"G1_auc_B_diff": round(q["G1"]["auc_B"] - m["G1"]["auc_B"], 3), "G2_auc_B_diff": round(q["G2"]["auc_B"] - m["G2"]["auc_B"], 3),
                        "G3_top1_B_diff": round(q["G3"]["top1_hit_B"] - m["G3"]["top1_hit_B"], 3)}
json.dump(res, open(f"{ARM}/aggregates/relgate.json", "w"), indent=1)
print(json.dumps(res, indent=1))

if "--audit" in sys.argv and "m4" in res["models"]:
    run = load("m4"); w = res["models"]["m4"]["G1"]["selected"]
    negB = sorted([c for c in C if c["half"] == "B" and not c["label"]], key=lambda c: -run[f"{c['cid']}|G1|{w}"]["p"])[:20]
    with open(f"{ARM}/data/audit-top20-negB.jsonl", "w") as fh:
        for c in negB:
            it = c["id"]
            fh.write(json.dumps({"cid": c["cid"], "p": run[f"{c['cid']}|G1|{w}"]["p"], "question": c["question"], "chunk": c["chunk"]}, ensure_ascii=False) + "\n")
    print("audit file written")
