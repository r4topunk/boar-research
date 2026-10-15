"""LONGSESSION addendum 1 aggregation (0 LLM calls): per turn block (6-10, 11-15) ratio A/B with the agg_ls.py / agg_device.py estimator, token curve
to turn 15, adapter-vs-app history window, coreference + card-reuse checks, worst 3. Merges into aggregates/longsession.json under key ext15.
Usage: python3 -I agg_ext.py <questions.jsonl> <base session traces> <base standalone traces> <base judgments> <ext session traces> <ext standalone traces>
                              <ext judgments> <prompt dump glob dir> <aggregates json>"""
import json, sys, os, glob, collections, numpy as np
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
def load(p):
    J = collections.defaultdict(dict)
    for l in open(p):
        r = json.loads(l)
        if r.get("ok"): J[r["queryId"]][r["order"]] = r["mapped"]
    return {q: {"s": (mr(v["boarA"]["boar"]) + mr(v["boarB"]["boar"])) / 2, "r": (mr(v["boarA"]["ref"]) + mr(v["boarB"]["ref"])) / 2,
                "winner": v["boarA"]["winner"] if v["boarA"]["winner"] == v["boarB"]["winner"] else "tie", "consistent": v["boarA"]["winner"] == v["boarB"]["winner"]}
            for q, v in J.items() if set(v) == {"boarA", "boarB"}}
def boot(fn, n, B=2000, seed=11):
    rng = np.random.default_rng(seed); return np.array([fn(rng.integers(0, n, n)) for _ in range(B)])
ci = lambda x: [round(float(v), 3) for v in np.percentile(x, [2.5, 97.5])]
def setstats(d, ids):
    if not ids: return {"n": 0}
    S = np.array([d[q]["s"] for q in ids]); R = np.array([d[q]["r"] for q in ids]); b = boot(lambda ii: S[ii].sum() / R[ii].sum(), len(ids))
    w = collections.Counter(d[q]["winner"] for q in ids)
    return {"n": len(ids), "raw": round(float(S.sum() / R.sum()), 3), "raw_ci": ci(b), "win_tie_loss": [w["boar"], w["tie"], w["ref"]],
            "pos_consistency": round(sum(d[q]["consistent"] for q in ids) / len(ids), 3), "mean_sA": round(float(S.mean()), 3), "mean_sB": round(float(R.mean()), 3)}
qp, bA, bB, bJ, eA, eB, eJ, dumpdir, aggp = sys.argv[1:10]
Q = {q["id"]: q for q in (json.loads(l) for l in open(qp) if l.strip())}
rd = lambda p: {t["itemId"]: t for t in (json.loads(l) for l in open(p) if l.strip())}
TA = {**rd(bA), **rd(eA)}; TB = {**rd(bB), **rd(eB)}; J = {**load(bJ), **load(eJ)}
SS = ["ls02", "ls06", "ls08"]; ext = [i for i in Q if Q[i]["session"] in SS and Q[i]["turn"] >= 6]
out = {"criterion_addendum1_sha256": open(os.path.join(os.path.dirname(aggp), "..", "LONGSESSION-criterion-addendum1.sha256")).read().split()[0],
       "n_ext": len(ext), "n_judged": sum(i in J for i in ext)}
blk = lambda lo, hi, extra=lambda i: True: [i for i in Q if Q[i]["session"] in SS and lo <= Q[i]["turn"] <= hi and i in J and extra(i)]
out["blocks"] = {"t1_5_same3": setstats(J, blk(1, 5)), "t6_10": setstats(J, blk(6, 10)), "t11_15": setstats(J, blk(11, 15)), "t6_15": setstats(J, blk(6, 15))}
out["blocks_followup"] = {"t6_15_followup": setstats(J, blk(6, 15, lambda i: Q[i]["followup"])), "t6_15_self_contained": setstats(J, blk(6, 15, lambda i: not Q[i]["followup"]))}
out["per_session_t6_15"] = {s: setstats(J, [i for i in blk(6, 15) if Q[i]["session"] == s]) for s in SS}
# token curve per turn (3 sessions)
curve = {}
for t in range(1, 16):
    it = [i for i in Q if Q[i]["session"] in SS and Q[i]["turn"] == t and i in TA]
    a = {i: TA[i]["timing"].get("promptTokens") for i in it}; b = {i: TB[i]["timing"].get("promptTokens") for i in it if i in TB}
    curve[t] = {"A_promptTokens": a, "B_promptTokens": b, "A_totalMs_p50": round(float(np.median([TA[i]["timing"]["totalMs"] for i in it]))),
                "B_totalMs_p50": round(float(np.median([TB[i]["timing"]["totalMs"] for i in it if i in TB])))}
out["token_curve"] = curve
# chars/token ratio from the dumped prompts (all LONGSESSION dumps with a matching trace promptTokens)
pts = []
for f in glob.glob(os.path.join(dumpdir, "ls-*.prompts.jsonl")):
    run = os.path.basename(f).split(".prompts")[0]
    for l in open(f):
        if not l.strip(): continue
        r = json.loads(l); i = r.get("itemId"); T = TA if "session" in run else TB
        if i in T and T[i]["timing"].get("promptTokens") and isinstance(r.get("messages"), list):
            pts.append((sum(len(m["content"]) for m in r["messages"]), T[i]["timing"]["promptTokens"]))
pts = np.array(pts, float); slope, ic = np.polyfit(pts[:, 0], pts[:, 1], 1)
out["chars_to_tokens"] = {"n_prompts": len(pts), "tokens_per_char": round(float(slope), 4), "intercept_tokens": round(float(ic), 1), "note": "linear fit promptTokens ~ prompt chars; template tokens in the intercept"}
tok = lambda txt: len(txt) * slope
# history the adapter passed vs what the app would pass, per session and turn
win = {}
ans = {i: TA[i]["answer"]["text"] for i in TA}
for s in SS:
    msgs = []; win[s] = {}
    for t in range(1, 16):
        i = f"{s}-t{t}"
        if i not in Q: continue
        full = sum(tok(m) for m in msgs); last6 = sum(tok(m) for m in msgs[-6:])
        summary = 150 if t >= 8 else 0  # app: summary produced after a turn completes with > 6 turns in total (historyTurnThreshold 6), nPredict 150
        win[s][t] = {"prior_messages": len(msgs), "adapter_history_tokens_est": round(full), "app_history_tokens_est": round(last6 + summary),
                     "app_dropped_messages": max(0, len(msgs) - 6), "app_has_summary": t >= 8}
        if i in TA: msgs += [Q[i]["question"], ans[i]]
out["history_window"] = win
first_trunc = {s: next((t for t, v in win[s].items() if v["app_dropped_messages"] > 0), None) for s in SS}
out["app_first_truncation"] = {s: {"turn": first_trunc[s], "adapter_history_tokens_est_at_that_turn": win[s][first_trunc[s]]["adapter_history_tokens_est"],
                                   "app_history_tokens_est_at_that_turn": win[s][first_trunc[s]]["app_history_tokens_est"]} for s in SS if first_trunc[s]}
t15 = {s: win[s][15] for s in SS}; out["at_turn15"] = t15
# token growth fit (A promptTokens on t, LLM items only)
xy = [(t, v) for t in range(1, 16) for v in curve[t]["A_promptTokens"].values() if v is not None]
xy = np.array(xy, float); sl, ic2 = np.polyfit(xy[:, 0], xy[:, 1], 1)
out["projection"] = {"A_promptTokens_fit": {"slope_per_turn": round(float(sl), 1), "intercept": round(float(ic2), 1),
                     "turn_exceeding_4096": round(float((4096 - ic2) / sl), 1) if sl > 0 else None}, "max_A_promptTokens_t6_15": int(max(v for t in range(6, 16) for v in curve[t]["A_promptTokens"].values() if v is not None) if any(v is not None for t in range(6, 16) for v in curve[t]["A_promptTokens"].values()) else 0)}
# coref + cards
co = [{"id": i, "A": any(r.lower() in TA[i]["answer"]["text"].lower() for r in Q[i]["referent"]), "B": any(r.lower() in TB[i]["answer"]["text"].lower() for r in Q[i]["referent"])}
      for i in ext if Q[i]["followup"]]
out["coref"] = {"n_followup": len(co), "A_fail": sum(not x["A"] for x in co), "B_fail": sum(not x["B"] for x in co), "A_fail_ids": [x["id"] for x in co if not x["A"]]}
card = lambda T, i: [c for c in T[i]["route"].get("reasonCodes", []) if c.startswith("grounding:fa-card")]
out["cards"] = {"from_history_ids": [i for i in ext if "grounding:fa-card-from-history" in card(TA, i)],
                "A_card_not_in_B": [{"id": i, "A": card(TA, i), "B": card(TB, i)} for i in ext if set(card(TA, i)) - set(card(TB, i))],
                "A_health_strict_not_in_B": [i for i in ext if "grounding:health-strict" in TA[i]["route"]["reasonCodes"] and "grounding:health-strict" not in TB[i]["route"]["reasonCodes"]],
                "A_no_llm": [i for i in ext if TA[i]["timing"].get("promptTokens") is None], "text_identical": sum(TA[i]["answer"]["text"] == TB[i]["answer"]["text"] for i in ext),
                "errors": sum(bool(TA[i].get("error")) + bool(TB[i].get("error")) for i in ext)}
d = sorted((J[i]["s"] - J[i]["r"], i) for i in ext if i in J)
out["worst3"] = [{"id": i, "d": round(x, 3), "question": Q[i]["question"], "A": TA[i]["answer"]["text"][:160], "B": TB[i]["answer"]["text"][:160]} for x, i in d[:3]]
agg = json.load(open(aggp)); agg["ext15"] = out; open(aggp, "w").write(json.dumps(agg, indent=1, ensure_ascii=False) + "\n")
print(json.dumps({k: v for k, v in out.items() if k not in ("token_curve", "history_window")}, indent=1, ensure_ascii=False))
