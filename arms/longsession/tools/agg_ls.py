"""LONGSESSION aggregation (0 LLM calls). Estimator copied from arms/device-x6/tools/agg_device.py (load / ratios / setstats unchanged: per-item mean of
correctness/completeness/usefulness over both orders, ratio of sums, item bootstrap B 2000 seed 11), adapted for per-turn groups; drift and slope use a
session-cluster bootstrap (resample the 10 sessions, B 2000, seed 11).
Usage: python3 -I agg_ls.py <questions.jsonl> <session traces> <standalone traces> <judgments.jsonl> [--out file.json]"""
import json, sys, os, collections, numpy as np
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
def load(p):
    J = collections.defaultdict(dict)
    for l in open(p):
        r = json.loads(l)
        if r.get("ok"): J[r["queryId"]][r["order"]] = r["mapped"]
    out = {}
    for q, v in J.items():
        if set(v) != {"boarA", "boarB"}: print(f"WARN {q} one order only; skipped", file=sys.stderr); continue
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
    return {"n": len(ids), "raw": round(pt[0], 3), "raw_ci": ci(b[:, 0]), "win_tie_loss": [w["boar"], w["tie"], w["ref"]],
            "pos_consistency": round(sum(d[q]["consistent"] for q in ids) / len(ids), 3), "mean_sA": round(float(S.mean()), 3), "mean_sB": round(float(R.mean()), 3)}
qp, ap, bp, jp = sys.argv[1:5]
Q = {q["id"]: q for q in (json.loads(l) for l in open(qp) if l.strip()) if q["turn"] <= 5}  # base arm = turns 1-5 (addendum 1 items: agg_ext.py)
rd = lambda p: {t["itemId"]: t for t in (json.loads(l) for l in open(p) if l.strip())}
TA, TB = rd(ap), rd(bp); J = load(jp)
ids = [i for i in Q if i in J]; sessions = sorted({Q[i]["session"] for i in Q})
out = {"estimator": "agg_device.py setstats per turn (item bootstrap B 2000 seed 11); drift/slope: session-cluster bootstrap B 2000 seed 11",
       "n_judged": len(ids), "n_items": len(Q)}
out["per_turn"] = {t: setstats(J, [i for i in ids if Q[i]["turn"] == t]) for t in range(1, 6)}
out["pooled_t2_5"] = setstats(J, [i for i in ids if Q[i]["turn"] > 1])
out["split"] = {"followup": setstats(J, [i for i in ids if Q[i]["followup"]]), "self_contained": setstats(J, [i for i in ids if not Q[i]["followup"]]),
                "self_contained_t2_5": setstats(J, [i for i in ids if not Q[i]["followup"] and Q[i]["turn"] > 1])}
out["per_turn_self_contained"] = {t: setstats(J, [i for i in ids if Q[i]["turn"] == t and not Q[i]["followup"]]) for t in range(1, 6)}
out["per_shape"] = {sh: setstats(J, [i for i in ids if Q[i]["shape"] == sh]) for sh in ("coref", "switch", "deepen")}
# session-cluster bootstrap: drift = ratio_5 - ratio_1, slope of ratio_t on t
cell = {(s, t): [i for i in ids if Q[i]["session"] == s and Q[i]["turn"] == t] for s in sessions for t in range(1, 6)}
def turn_ratio(ss, t, sc_only=False):
    it = [i for s in ss for i in cell[(s, t)] if not (sc_only and Q[i]["followup"])]
    if not it: return np.nan
    return sum(J[i]["s"] for i in it) / sum(J[i]["r"] for i in it)
def stats(ss, sc_only=False):
    r = np.array([turn_ratio(ss, t, sc_only) for t in range(1, 6)]); tt = np.arange(1, 6); m = ~np.isnan(r)
    return r[4] - r[0], (np.polyfit(tt[m], r[m], 1)[0] if m.sum() >= 2 else np.nan)
rng = np.random.default_rng(11); ns = len(sessions); B = []
for _ in range(2000): B.append(stats([sessions[k] for k in rng.integers(0, ns, ns)]))
B = np.array(B); pt = stats(sessions)
out["drift"] = {"d_ratio_t5_minus_t1": round(float(pt[0]), 3), "ci": ci(B[:, 0]), "slope_per_turn": round(float(pt[1]), 4), "slope_ci": ci(B[:, 1])}
rng = np.random.default_rng(11); B2 = []
for _ in range(2000):
    v = stats([sessions[k] for k in rng.integers(0, ns, ns)], True)
    if not np.isnan(v[0]): B2.append(v)
B2 = np.array(B2); pt2 = stats(sessions, True)
out["drift_self_contained"] = {"d_ratio_t5_minus_t1": round(float(pt2[0]), 3), "ci": ci(B2[:, 0]), "slope_per_turn": round(float(pt2[1]), 4), "slope_ci": ci(B2[:, 1]), "boot_valid": len(B2)}
# prompt tokens, latency
def col(T, f, t):
    return [T[i]["timing"].get(f) for i in Q if Q[i]["turn"] == t and i in T and T[i]["timing"].get(f) is not None]
tok = {}
for t in range(1, 6):
    a, b = col(TA, "promptTokens", t), col(TB, "promptTokens", t); la, lb = col(TA, "totalMs", t), col(TB, "totalMs", t)
    tok[t] = {"A_promptTokens_n": len(a), "A_p50": float(np.median(a)) if a else None, "A_mean": round(float(np.mean(a)), 1) if a else None, "A_max": max(a) if a else None,
              "B_p50": float(np.median(b)) if b else None, "B_max": max(b) if b else None,
              "A_totalMs_p50": round(float(np.median(la))), "A_totalMs_max": round(max(la)), "B_totalMs_p50": round(float(np.median(lb))), "B_totalMs_max": round(max(lb))}
out["tokens_latency"] = tok
tt = np.arange(1, 6); proj = {}
for k in ("A_mean", "A_max"):
    y = np.array([tok[t][k] for t in range(1, 6)], float); sl, ic = np.polyfit(tt, y, 1)
    proj[k] = {"slope_tokens_per_turn": round(float(sl), 1), "intercept": round(float(ic), 1), "turn_exceeding_4096": (round(float((4096 - ic) / sl), 1) if sl > 0 else None)}
# per-session growth: history-only token cost = A - B promptTokens on the same item
per_sess = {}
for s in sessions:
    d = [(Q[i]["turn"], TA[i]["timing"]["promptTokens"] - TB[i]["timing"]["promptTokens"]) for i in Q if Q[i]["session"] == s and i in TA and i in TB
         and TA[i]["timing"].get("promptTokens") is not None and TB[i]["timing"].get("promptTokens") is not None]
    per_sess[s] = d
hist = [(t, x) for v in per_sess.values() for t, x in v if t > 1]
if hist:
    ht = np.array([t for t, _ in hist], float); hx = np.array([x for _, x in hist], float); sl, ic = np.polyfit(ht, hx, 1)
    proj["history_overhead_A_minus_B"] = {"slope_tokens_per_turn": round(float(sl), 1), "per_turn_mean": {int(t): round(float(hx[ht == t].mean()), 1) for t in sorted(set(ht))}}
    proj["worst_case_turn_exceeding_4096"] = None
    # worst case: largest B prompt (sources) + worst per-turn history slope across sessions
    worst = []
    for s, v in per_sess.items():
        v2 = [(t, x) for t, x in v if t > 1]
        if len(v2) >= 2:
            a2 = np.array(v2, float); worst.append(np.polyfit(a2[:, 0], a2[:, 1], 1)[0])
    bmax = max(TB[i]["timing"]["promptTokens"] for i in TB if TB[i]["timing"].get("promptTokens") is not None)
    ws = max(worst) if worst else sl
    proj["worst_case"] = {"max_B_prompt": bmax, "max_session_history_slope": round(float(ws), 1), "turn_exceeding_4096": round(float(1 + (4096 - bmax) / ws), 1) if ws > 0 else None}
out["projection"] = proj
# reason codes / route / kept
rc = {}
for t in range(1, 6):
    it = [i for i in Q if Q[i]["turn"] == t and i in TA and i in TB]; c = collections.Counter()
    for i in it:
        a, b = TA[i], TB[i]; ca, cb = a["route"].get("reasonCodes", []), b["route"].get("reasonCodes", [])
        c["A_history_codes"] += sum("history" in x for x in ca); c["B_history_codes"] += sum("history" in x for x in cb)
        c["task_diff"] += a["route"].get("task") != b["route"].get("task")
        c["A_declined"] += bool(a["answer"].get("declined")); c["B_declined"] += bool(b["answer"].get("declined"))
        c["A_no_good_source"] += "grounding:no-good-source" in ca; c["B_no_good_source"] += "grounding:no-good-source" in cb
        c["kept_diff"] += sorted(k["title"] for k in a["retrieval"]["kept"]) != sorted(k["title"] for k in b["retrieval"]["kept"])
        c["A_no_llm"] += a["timing"].get("promptTokens") is None; c["B_no_llm"] += b["timing"].get("promptTokens") is None
        c["text_identical"] += a["answer"]["text"] == b["answer"]["text"]
        c["errors"] += bool(a.get("error")) + bool(b.get("error"))
    rc[t] = dict(c)
out["reason_codes"] = rc
out["history_code_names"] = sorted({x for i in TA for x in TA[i]["route"].get("reasonCodes", []) if "history" in x})
# coreference heuristic
co = []
for i, q in Q.items():
    if not q["followup"]: continue
    has = lambda T: any(r.lower() in T[i]["answer"]["text"].lower() for r in q["referent"])
    co.append({"id": i, "A_names_referent": has(TA), "B_names_referent": has(TB), "referent": q["referent"]})
out["coref"] = {"n_followup": len(co), "A_fail": sum(not x["A_names_referent"] for x in co), "B_fail": sum(not x["B_names_referent"] for x in co),
                "A_fail_ids": [x["id"] for x in co if not x["A_names_referent"]], "B_fail_ids": [x["id"] for x in co if not x["B_names_referent"]]}
# worst items (A - B)
diffs = sorted(((J[i]["s"] - J[i]["r"], i) for i in ids))
out["worst3"] = [{"id": i, "d": round(d, 3), "question": Q[i]["question"], "A": TA[i]["answer"]["text"][:160], "B": TB[i]["answer"]["text"][:160]} for d, i in diffs[:3]]
out["best3"] = [{"id": i, "d": round(d, 3), "question": Q[i]["question"]} for d, i in diffs[::-1][:3]]
js = json.dumps(out, indent=1, ensure_ascii=False); print(js)
if "--out" in sys.argv: open(sys.argv[sys.argv.index("--out") + 1], "w").write(js + "\n")
