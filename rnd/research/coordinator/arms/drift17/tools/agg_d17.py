"""DRIFT17 aggregation (0 LLM calls). Per item: judge dims mean over both orders (boar = in-session A, ref = standalone B).
Usage: python3 -I agg_d17.py <questions> <A traces> <B traces> <judgments> <4B A traces csv> <4B judgments csv> --out file.json"""
import json, sys, collections, numpy as np
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
WARN = ("Not found in this phone's offline library", "This answer is not from an offline source")
REFUSE = ("I don't have a reliable offline source", "I don't know")
def judg(paths):
    J = collections.defaultdict(dict)
    for p in paths:
        for l in open(p):
            r = json.loads(l)
            if r.get("ok") in (True, "True"): m = r["mapped"]; J[r["queryId"]][r["order"]] = m if isinstance(m, dict) else json.loads(m)
    out = {}
    for q, v in J.items():
        if set(v) != {"boarA", "boarB"}: continue
        a, b = v["boarA"], v["boarB"]
        out[q] = {"sA": (mr(a["boar"]) + mr(b["boar"])) / 2, "sB": (mr(a["ref"]) + mr(b["ref"])) / 2,
                  "cA": (a["boar"]["correctness"] + b["boar"]["correctness"]) / 2, "cB": (a["ref"]["correctness"] + b["ref"]["correctness"]) / 2}
    return out
def traces(paths):
    T = {}
    for p in paths:
        for l in open(p):
            if l.strip(): t = json.loads(l); T[t["itemId"]] = t
    return T
def feat(t):
    a = t.get("answer") or {}; txt = a.get("text", "") or ""
    rc = (t.get("receipt") or {}).get("reasonCodes") or a.get("reasonCodes") or []
    if not rc:
        for e in t.get("events") or []:
            if isinstance(e, dict) and e.get("type") == "done": rc = (e.get("receipt") or {}).get("reasonCodes") or rc
    return {"declined": bool(a.get("declined")), "warned": txt.lstrip().startswith(WARN), "refuse_text": txt.lstrip().startswith(REFUSE),
            "fa_hist": "grounding:fa-card-from-history" in json.dumps(t), "text": txt}
def model(Q, TA, TB, J):
    D = {}
    for i, q in Q.items():
        if i not in J or i not in TA: continue
        fa, fb, j = feat(TA[i]), feat(TB[i]) if i in TB else None, J[i]
        D[i] = {"turn": q["turn"], "session": q["session"], "followup": q["followup"], "shape": q["shape"],
                "topic_drift": q["shape"] == "switch" and q["turn"] >= 3,
                "ceA": (not fa["declined"]) and (not fa["warned"]) and j["cA"] <= 1.5, "wceA": fa["warned"] and j["cA"] <= 1.5,
                "ceB": (fb is not None) and (not fb["declined"]) and (not fb["warned"]) and j["cB"] <= 1.5,
                "decA": fa["declined"], "refA": fa["declined"] or fa["refuse_text"], "warnA": fa["warned"], "warnB": bool(fb and fb["warned"]),
                "sA": 0.0 if fa["declined"] else j["sA"], "sB": 0.0 if (fb and fb["declined"]) else j["sB"], "cA": j["cA"], "cB": j["cB"],
                "fa_hist": fa["fa_hist"], "identical": bool(fb) and fa["text"] == fb["text"],
                "coref_ok": any(r.lower() in fa["text"].lower() for r in q.get("referent") or []) if q["followup"] else None}
    return D
def bucket(D, f):
    ids = [i for i in D if f(D[i])]; n = len(ids)
    if not n: return {"n": 0}
    g = lambda k: sum(D[i][k] for i in ids)
    sa, sb = g("sA"), g("sB")
    return {"n": n, "ce_unwarned_A": g("ceA"), "ce_unwarned_rate_A": round(g("ceA") / n, 3), "ce_unwarned_B": g("ceB"), "ce_unwarned_rate_B": round(g("ceB") / n, 3),
            "warned_ce_A": g("wceA"), "warned_A": g("warnA"), "warned_B": g("warnB"), "declined_A": g("decA"), "refusal_rate_A": round(g("refA") / n, 3),
            "U_ratio_A_over_B": round(sa / sb, 3) if sb else None, "mean_sA": round(sa / n, 3), "mean_sB": round(sb / n, 3),
            "mean_corrA": round(g("cA") / n, 3), "mean_corrB": round(g("cB") / n, 3), "fa_card_from_history": g("fa_hist")}
def sboot(D, stat, B=2000, seed=11):
    S = sorted({d["session"] for d in D.values()}); by = {s: [i for i in D if D[i]["session"] == s] for s in S}
    rng = np.random.default_rng(seed); v = []
    for _ in range(B):
        ids = [i for s in rng.choice(S, len(S)) for i in by[s]]; x = stat(ids)
        if x is not None: v.append(x)
    return [round(float(p), 3) for p in np.percentile(v, [2.5, 97.5])] if v else None
def rate(D, ids, k, f): z = [i for i in ids if f(D[i])]; return (sum(D[i][k] for i in z) / len(z)) if z else None
def analyse(D):
    B = {"t1": lambda d: d["turn"] == 1, "t2_3": lambda d: d["turn"] in (2, 3), "t4_5": lambda d: d["turn"] in (4, 5), "t4plus": lambda d: d["turn"] >= 4,
         "t2_5": lambda d: 2 <= d["turn"] <= 5, "t6_15": lambda d: d["turn"] >= 6, "followup_t2_5": lambda d: d["followup"] and 2 <= d["turn"] <= 5,
         "selfcontained_t2_5": lambda d: (not d["followup"]) and 2 <= d["turn"] <= 5, "topic_drift": lambda d: d["topic_drift"],
         "no_topic_drift_t3plus": lambda d: (not d["topic_drift"]) and d["turn"] >= 3, "all": lambda d: True}
    out = {"buckets": {k: bucket(D, f) for k, f in B.items()}, "per_turn": {t: bucket(D, lambda d, t=t: d["turn"] == t) for t in range(1, 16) if any(d["turn"] == t for d in D.values())}}
    t1, t45 = B["t1"], B["t4_5"]
    r1 = rate(D, list(D), "ceA", t1); r45 = rate(D, list(D), "ceA", t45)
    def diff(ids):
        a, b = rate(D, ids, "ceA", t45), rate(D, ids, "ceA", t1); return None if a is None or b is None else a - b
    def paired(ids, f):
        z = [i for i in ids if f(D[i])]; return (sum(D[i]["ceA"] - D[i]["ceB"] for i in z) / len(z)) if z else None
    def uratio(ids, f):
        z = [i for i in ids if f(D[i])]; sb = sum(D[i]["sB"] for i in z); return sum(D[i]["sA"] for i in z) / sb if sb else None
    n45 = sum(D[i]["ceA"] for i in D if t45(D[i]))
    ci = sboot(D, diff)
    a = r45 >= 2 * r1 if r1 > 0 else n45 > 0
    rule = {"r1": round(r1, 3), "r45": round(r45, 3), "n_ce_t4_5": n45, "diff_r45_minus_r1": round(r45 - r1, 3), "diff_ci": ci,
            "a_ratio_ge_2x": bool(a), "b_count_ge_3": n45 >= 3, "c_ci_low_gt_0": bool(ci and ci[0] > 0)}
    rule["label"] = "DRIFT CONFIRMED" if (rule["a_ratio_ge_2x"] and rule["b_count_ge_3"] and rule["c_ci_low_gt_0"]) else (
        "KILLED (point estimate meets 2x, CI covers 0: not confirmed)" if (rule["a_ratio_ge_2x"] and rule["b_count_ge_3"]) else "KILLED")
    all_ids = list(D)
    rule["paired_A_minus_B_ce_t4_5"] = {"pt": round(paired(all_ids, t45), 3), "ci": sboot(D, lambda ids: paired(ids, t45))}
    rule["paired_A_minus_B_ce_followup_t2_5"] = {"pt": round(paired(all_ids, B["followup_t2_5"]), 3), "ci": sboot(D, lambda ids: paired(ids, B["followup_t2_5"]))}
    rule["U_ratio_t2_5"] = {"pt": round(uratio(all_ids, B["t2_5"]), 3), "ci": sboot(D, lambda ids: uratio(ids, B["t2_5"]))}
    rule["U_ratio_t4plus"] = {"pt": round(uratio(all_ids, B["t4plus"]), 3), "ci": sboot(D, lambda ids: uratio(ids, B["t4plus"]))}
    out["rule"] = rule
    t1ids = [i for i in D if D[i]["turn"] == 1]; out["null_check_turn1_identical"] = f"{sum(D[i]['identical'] for i in t1ids)}/{len(t1ids)}"
    fu = [i for i in D if D[i]["followup"]]; out["coref_fail_A"] = f"{sum(not D[i]['coref_ok'] for i in fu)}/{len(fu)}"
    out["ce_unwarned_items_A"] = sorted(i for i in D if D[i]["ceA"])
    return out
args = sys.argv[1:]; o = args[args.index("--out") + 1] if "--out" in args else None
qp, ap, bp, jp, a4, j4 = args[:6]
Q = {q["id"]: q for q in map(json.loads, open(qp))}
res = {"q17": analyse(model(Q, traces([ap]), traces([bp]), judg([jp])))}
LS = "<workspace>/rnd/research/coordinator/arms/longsession/runs/"
res["q4b"] = analyse(model(Q, traces(a4.split(",")), traces([LS + "ls-standalone-s42.traces.jsonl", LS + "ls-ext15-standalone-s42.traces.jsonl"]), judg(j4.split(","))))
s = json.dumps(res, indent=1); print(s) if not o else open(o, "w").write(s + "\n")
