#!/usr/bin/env python3
"""LITE6: residual loss map of the lite tier after the reach lever. 1.7B + X2b (L, lite5/runs/180 ON) vs 4B + X2b (X, headpass-st/gen-x2b),
180 public self-tests, Haiku 5.5-low rows both orders (reused; 0 Haiku, 0 Opus). Per item ratio = sum boar / sum ref over 3 dims x both orders
(LITE3 estimator). Loss = X ratio - L ratio. Fact in context = lite5/aggregates/fic-180.json 'on' (X2b kept lists identical for L and X, gate-180 G1).
jev (typesafe-ai/jev, gateway): losses -> LITE3's pick-one buckets + 5 axes, state exactly as LITE3 (stronger_answer = 4B X2b answer);
wins -> a pick-one over what the 1.7B does better. Identical answer text -> 'identical' (judge noise, no jev call).
usage: python3 -I lite6.py [--dry-run]"""
import json, os, re, sys, random, statistics as stt, importlib.util
from concurrent.futures import ThreadPoolExecutor
A = "<workspace>/rnd/research/coordinator/arms"; OUT = f"{A}/lite6"; CACHE = f"{OUT}/cache"
spec = importlib.util.spec_from_file_location("lite3", f"{A}/lite3/tools/lite3.py"); L3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(L3)
BUCKETS, QUESTIONS, call, nsent, health_safety, load = L3.BUCKETS, L3.QUESTIONS, L3.call, L3.nsent, L3.health_safety, L3.load
SE = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se"]; TOPIC = ["boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
PATH = {"L": lambda p: f"{A}/lite5/runs/180/lite5-180-on-{p}-s42", "X": lambda p: f"{A}/headpass-st/gen-x2b/st-{p}-cut7-headpassx2b-s42"}
JSUF = {"L": ".judgments.haiku55-low.jsonl", "X": ".judgments.jsonl"}
DIMS = L3.DIMS
WIN = {"big_error": "`big_rationale_1`/`big_rationale_2` fault `big_answer` for a wrong, inaccurate or unsupported claim that `small_answer` does not make",
       "small_more_complete": "`small_answer` covers more of the specific facts, figures or steps the reference has; `big_answer` is roughly right but thinner",
       "small_used_context": "`fact_in_context` is \"yes\" and `small_answer` states that fact while `big_answer` misses or garbles it",
       "big_hedged": "`big_answer` refuses, hedges, defers to an expert or says it lacks information, while `small_answer` answers substantively",
       "small_direct": "both carry similar content, but `small_answer` puts the asked verdict or number first or is clearer and less padded",
       "other": "none of the above fits, or the two answers are about equally good"}
WQ = {"primary": {"type": "choice", "instructions": "A judge scored `small_answer` and `big_answer` separately against the same reference (rationales given for each). What is the single main reason `small_answer` scored higher than `big_answer`?", "criteria": WIN}}

def rows(m):
    out = {}
    for p in SE + TOPIC:
        T = {t["itemId"]: t for t in load(PATH[m](p) + ".traces.jsonl")}; J = {}
        for r in load(PATH[m](p) + JSUF[m]):
            if r.get("ok"): J.setdefault(r["queryId"], []).append(r)
        for i, rs in J.items():
            rs = sorted(rs, key=lambda r: r["order"]); assert [r["order"] for r in rs] == ["boarA", "boarB"], (m, i); t = T[i]
            a = t["answer"]; txt = a.get("text") or ""; tm = t.get("timing") or {}
            boar = sum(r["mapped"]["boar"][d] for r in rs for d in DIMS); ref = sum(r["mapped"]["ref"][d] for r in rs for d in DIMS)
            out[i] = {"ratio": boar / ref, "pack": p, "cat": rs[0].get("category"), "rc": t["route"]["reasonCodes"], "words": len(txt.split()), "sent": nsent(txt),
                      "gt2": nsent(txt) > 2, "cited": len(a.get("cited") or []), "kept_titles": [k.get("title") for k in t["retrieval"]["kept"]], "declined": bool(a.get("declined")),
                      "ptok": tm.get("promptTokens"), "otok": tm.get("outputTokens"), "ttft": tm.get("ttftMs"), "_q": t.get("question"), "_txt": txt,
                      "_rat": [r["verdict"]["rationale"] for r in rs], "hs": health_safety(t, rs[0].get("category"))}
    assert len(out) == 180, (m, len(out)); return out

def main():
    dry = "--dry-run" in sys.argv; key = os.environ.get("VERCEL_AI_GATEWAY") or os.environ.get("AI_GATEWAY_API_KEY")
    if not key and not dry: sys.exit("no gateway key")
    os.makedirs(CACHE, exist_ok=True); L, X = rows("L"), rows("X"); F = json.load(open(f"{A}/lite5/aggregates/fic-180.json")); ids = sorted(L)
    assert all(L[i]["kept_titles"] == X[i]["kept_titles"] for i in ids), "kept titles differ"
    items = []; jobs = []
    for i in ids:
        l, x = L[i], X[i]; f = "yes" if F[i]["on"] else "no"; d = round(x["ratio"] - l["ratio"], 4)
        side = "below" if d > 1e-9 else "above" if d < -1e-9 else "tie"; same = l["_txt"].strip() == x["_txt"].strip()
        items.append({"id": i, "pack": l["pack"], "cat": l["cat"], "hs": l["hs"], "fic": F[i]["on"], "reach": F[i]["reach"], "loss": d, "side": side, "identical": same,
                      "rc_L": l["rc"], "L": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in l.items() if not k.startswith("_") and k not in ("rc", "kept_titles", "pack", "cat", "hs")},
                      "X": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in x.items() if not k.startswith("_") and k not in ("rc", "kept_titles", "pack", "cat", "hs")}})
        if side == "tie" or same: continue
        if side == "below":
            state = {"rationale_1": l["_rat"][0], "rationale_2": l["_rat"][-1], "answer": l["_txt"][:2500], "answer_words": l["words"], "reason_codes": l["rc"],
                     "kept_source_titles": l["kept_titles"], "cited_sources": l["cited"], "fact_in_context": f, "stronger_answer": x["_txt"][:1500]}
            jobs.append((i, "below", {"model": "typesafe-ai/jev", "state": state, "questions": QUESTIONS}))
        else:
            state = {"small_rationale_1": l["_rat"][0], "small_rationale_2": l["_rat"][-1], "big_rationale_1": x["_rat"][0], "big_rationale_2": x["_rat"][-1],
                     "small_answer": l["_txt"][:2000], "big_answer": x["_txt"][:2000], "kept_source_titles": l["kept_titles"], "fact_in_context": f}
            jobs.append((i, "above", {"model": "typesafe-ai/jev", "state": state, "questions": WQ}))
    if dry: print(len(jobs), "jobs", sum(len(json.dumps(j[2])) for j in jobs) // 3.3, "est tokens"); return
    cost = 0.0; new = 0; hit = 0; R = {}
    with ThreadPoolExecutor(4) as ex:
        for (i, s, _), (r, h) in zip(jobs, ex.map(lambda j: call(j[2], key, CACHE), jobs)):
            R[i] = r
            if h: hit += 1
            else: new += 1; cost += float(((r.get("providerMetadata") or {}).get("gateway") or {}).get("marketCost") or 0)
    for it in items:
        i = it["id"]
        if it["identical"]: it["bucket"] = "identical"; continue
        if i not in R: it["bucket"] = "tie"; continue
        a = R[i]["answers"]; it["bucket"] = a["primary"]["choice"]; it["bucket_conf"] = round(a["primary"].get("confidence") or 0, 3)
        it["bucket_p"] = {k: round(v, 3) for k, v in (a["primary"].get("probabilities") or {}).items()}
        if it["side"] == "below": it["axes"] = {q: round(a[q]["probability"], 3) for q in QUESTIONS if q.startswith("ax_")}
    def table(sel, labels):
        tot = sum(abs(r["loss"]) for r in sel) or 1e-9; t = {}
        for b in labels:
            bb = [r for r in sel if r["bucket"] == b]
            t[b] = {"n": len(bb), "sum": round(sum(abs(r["loss"]) for r in bb), 3), "share": round(sum(abs(r["loss"]) for r in bb) / tot, 3),
                    "n_fic": sum(r["fic"] for r in bb), "n_hs": sum(r["hs"] for r in bb), "ids": [r["id"] for r in bb]}
        return {"n": len(sel), "total": round(tot, 3), "low_conf_lt06": sum(1 for r in sel if r.get("bucket_conf", 1) < 0.6), "table": t}
    below = [r for r in items if r["side"] == "below"]; above = [r for r in items if r["side"] == "above"]
    res = {"arm": "LITE6", "date": "2026-10-16", "judge_rows": "Haiku 5.5-low N=4 both orders (LITE5-180 ON rows; HEADPASS-X2b rows)", "jev_model": "typesafe-ai/jev",
           "mean_ratio": {"L": round(stt.mean(L[i]["ratio"] for i in ids), 4), "X": round(stt.mean(X[i]["ratio"] for i in ids), 4)},
           "n_below_tie_above": [len(below), sum(r["side"] == "tie" for r in items), len(above)],
           "net_loss_sum": round(sum(r["loss"] for r in items), 3), "below": table(below, list(BUCKETS) + ["identical"]), "above": table(above, list(WIN) + ["identical"])}
    res["below"]["axes_p06"] = {q: sum(1 for r in below if r.get("axes", {}).get(q, 0) >= 0.6) for q in QUESTIONS if q.startswith("ax_")}
    res["below_by_reach"] = {c: {"n": len([r for r in below if r["reach"] == c]), "loss": round(sum(r["loss"] for r in below if r["reach"] == c), 3)} for c in ("newly_present", "present_off", "absent")}
    res["per_pack"] = {p: {"net": round(sum(r["loss"] for r in items if r["pack"] == p), 3),
                           "below": {b: round(sum(r["loss"] for r in below if r["pack"] == p and r["bucket"] == b), 3) for b in list(BUCKETS) + ["identical"]},
                           "above_sum": round(-sum(r["loss"] for r in above if r["pack"] == p), 3)} for p in SE + TOPIC}
    md = lambda xs: round(stt.median([v for v in xs if v is not None]), 1)
    res["profile"] = {m: {"words_p50": md([D[i]["words"] for i in ids]), "gt2_share": round(sum(D[i]["gt2"] for i in ids) / 180, 3), "cited_mean": round(stt.mean(D[i]["cited"] for i in ids), 2),
                          "ptok_p50": md([D[i]["ptok"] for i in ids]), "otok_p50": md([D[i]["otok"] for i in ids]), "ttft_s_p50": round(md([D[i]["ttft"] for i in ids]) / 1000, 2)} for m, D in (("L", L), ("X", X))}
    res["profile_below"] = {m: {"words_p50": md([r[m]["words"] for r in below]), "gt2_share": round(sum(r[m]["gt2"] for r in below) / len(below), 3)} for m in ("L", "X")}
    rnd20 = sorted(random.Random(616).sample(ids, 20)); res["random20_seed616"] = rnd20
    res["random20_below_by_bucket"] = {b: round(sum(r["loss"] for r in below if r["id"] in rnd20 and r["bucket"] == b), 3) for b in BUCKETS}
    worst = sorted(below, key=lambda r: -r["loss"])[:10]
    res["worst10"] = [{"id": r["id"], "loss": r["loss"], "bucket": r["bucket"], "fic": r["fic"], "q": L[r["id"]]["_q"], "L150": L[r["id"]]["_txt"][:150], "X150": X[r["id"]]["_txt"][:150]} for r in worst]
    res["jev"] = {"requests_new": new, "cached": hit, "cost_usd": round(cost, 5)}; res["items"] = items
    json.dump(res, open(f"{OUT}/aggregates/lite6.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ("items", "worst10")}, indent=0)[:6000])
if __name__ == "__main__": main()
