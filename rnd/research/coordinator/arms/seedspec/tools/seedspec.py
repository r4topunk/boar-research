#!/usr/bin/env python3
"""SEEDSPEC (T7): are the deep tier's wrong claims seed-specific or stable across the three SEEDVAR seeds (arm H, V-para)?
jev (typesafe-ai/jev via Vercel AI Gateway), one request per item with all three seeds' rationales+answers. Script-only on blind:
outputs ids, labels, probabilities, counts. Cache: <runs dir>/seedspec-cache/.
usage: seedspec.py --dir RUNSDIR --lossmap L.json --out O.json [--smoke] [--dry-run]
"""
import argparse, json, os, sys, statistics
from concurrent.futures import ThreadPoolExecutor
from collections import Counter, defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lossmap", "tools"))
import lossmap as LM

SEEDS = ["s42", "s43", "s44"]
def B(instr, t, f): return {"type": "boolean", "instructions": instr, "criteria": {"true": t, "false": f}}
Q = {}
for s in SEEDS:
    Q["wrong_in_" + s] = B(f"Do `{s}.rationale_1` or `{s}.rationale_2` say that `{s}.answer` states something factually incorrect, inaccurate or contradicted by the reference?",
        "an explicit error, inaccuracy, contradiction or false claim is attributed to the answer of this seed",
        "the judge calls the answer accurate, or only says it is incomplete, brief or hedged")
Q["same_wrong_fact"] = B("Where two or more of `s42`, `s43`, `s44` are judged to contain a factual error, is it the SAME claim that is wrong in them (same number, date, name or statement)?",
    "the rationales of the wrong seeds point to the same incorrect number, date, name or statement",
    "the wrong seeds err on different claims, or only one seed (or none) is judged wrong")
Q["any_seed_correct_on_it"] = B("Does at least one seed's answer (`s42.answer`, `s43.answer`, `s44.answer`) get right the specific fact that another seed gets wrong according to its rationales?",
    "the specific claim one seed is faulted for is stated correctly in another seed's answer",
    "no seed states that fact correctly, or no seed is faulted for a wrong fact")
Q["pattern"] = {"type": "choice", "instructions": "Across the three seeds, how do the factual errors named in the rationales relate?",
    "criteria": {
      "stable_wrong": "the same wrong claim appears in every seed that is wrong, and no seed gets it right",
      "seed_specific": "different seeds err on different claims, or some seeds get right what others get wrong",
      "mixed": "part of the errors repeat across seeds and part are seed-specific",
      "not_wrong": "no seed is judged to contain a factual error"}}
BOOL = [q for q, s in Q.items() if s["type"] == "boolean"]

def load(d, s):
    J = [r for r in LM.read_jsonl(os.path.join(d, f"dh-H-vpara-{s}.judgments.jsonl")) if r.get("ok")]
    T = {t["itemId"]: t for t in LM.read_jsonl(os.path.join(d, f"dh-H-vpara-{s}.traces.jsonl"))}
    by = defaultdict(list)
    for r in J: by[r["queryId"]].append(r)
    return by, T

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True); ap.add_argument("--lossmap", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--threshold", type=float, default=0.6); ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    key = os.environ.get("VERCEL_AI_GATEWAY") or os.environ.get("AI_GATEWAY_API_KEY")
    if a.smoke:
        r, _ = LM.call({"model": LM.MODEL, "state": "the deploy failed halfway", "questions": {"bad": {"type": "boolean", "instructions": "Did something go wrong in `state`?"}}}, key, "/tmp") if False else (None, None)
        import urllib.request
        req = urllib.request.Request(LM.GATEWAY, data=json.dumps({"model": LM.MODEL, "state": "the deploy failed halfway", "questions": {"bad": {"type": "boolean", "instructions": "Did something go wrong in `state`?"}}}).encode(),
                                     headers={"authorization": "Bearer " + key, "content-type": "application/json"})
        print(json.load(urllib.request.urlopen(req, timeout=60))["answers"]); return
    if not key and not a.dry_run: sys.exit("no gateway key")
    data = {s: load(a.dir, s) for s in SEEDS}
    L = {i["id"]: i for i in json.load(open(a.lossmap))["items"]}
    wrong42 = {i for i, v in L.items() if v["labels"].get("wrong_fact")}
    ids = sorted(set.intersection(*[set(data[s][0]) for s in SEEDS]))
    cache = os.path.join(a.dir, "seedspec-cache"); os.makedirs(cache, exist_ok=True)
    items = []
    for qid in ids:
        st = {}; corr = {}
        for s in SEEDS:
            rows = sorted(data[s][0][qid], key=lambda r: r["order"]); t = data[s][1].get(qid, {})
            st[s] = {"rationale_1": rows[0]["verdict"]["rationale"], "rationale_2": rows[-1]["verdict"]["rationale"] if len(rows) > 1 else "",
                     "answer": ((t.get("answer") or {}).get("text") or "")[:2000]}
            corr[s] = sum(r["mapped"]["boar"]["correctness"] for r in rows) / len(rows)
        vals = list(corr.values())
        items.append({"id": qid, "in_wrong_s42_lossmap": qid in wrong42, "correctness": {s: round(corr[s], 2) for s in SEEDS},
                      "range": round(max(vals) - min(vals), 2), "_state": st})
    print(f"{len(items)} items, {sum(i['in_wrong_s42_lossmap'] for i in items)} in wrong_fact set", file=sys.stderr)
    if a.dry_run: return
    cost = 0.0; cached = 0
    def work(it): return it, *LM.call({"model": LM.MODEL, "state": it["_state"], "questions": Q}, key, cache)
    with ThreadPoolExecutor(a.workers) as ex:
        for it, res, hit in ex.map(work, items):
            ans = res["answers"]; it["p"] = {q: round(ans[q]["probability"], 3) for q in BOOL}
            it["labels"] = {q: ans[q]["probability"] >= a.threshold for q in BOOL}
            it["pattern"] = ans["pattern"]["choice"]; it["pattern_conf"] = round(ans["pattern"].get("confidence", 0) or 0, 3)
            it["n_wrong_seeds"] = sum(it["labels"]["wrong_in_" + s] for s in SEEDS)
            if hit: cached += 1
            else: cost += float(((res.get("providerMetadata") or {}).get("gateway") or {}).get("marketCost") or 0)
            del it["_state"]
    def summ(pool):
        wr = [i for i in pool if i["n_wrong_seeds"] >= 1]; multi = [i for i in pool if i["n_wrong_seeds"] >= 2]
        pat = Counter(i["pattern"] for i in pool); patw = Counter(i["pattern"] for i in wr)
        return {"n": len(pool), "wrong_per_seed": {s: sum(i["labels"]["wrong_in_" + s] for i in pool) for s in SEEDS},
                "overlap_wrong_in_k_seeds": {str(k): sum(1 for i in pool if i["n_wrong_seeds"] == k) for k in (1, 2, 3)},
                "n_wrong_any": len(wr), "n_multi_wrong": len(multi),
                "same_wrong_fact_of_multi": round(sum(i["labels"]["same_wrong_fact"] for i in multi) / max(1, len(multi)), 3),
                "any_seed_correct_of_wrong": round(sum(i["labels"]["any_seed_correct_on_it"] for i in wr) / max(1, len(wr)), 3),
                "pattern_all": dict(pat), "pattern_of_wrong_any": dict(patw),
                "seed_specific_share_of_wrong_pattern": round((patw["seed_specific"]) / max(1, len(wr)), 3),
                "seed_specific_or_mixed_share": round((patw["seed_specific"] + patw["mixed"]) / max(1, len(wr)), 3),
                "single_seed_wrong_share": round(sum(1 for i in wr if i["n_wrong_seeds"] == 1) / max(1, len(wr)), 3)}
    def rhist(pool):
        h = Counter(); 
        for i in pool: h["<1" if i["range"] < 1 else "1-<2" if i["range"] < 2 else ">=2"] += 1
        return dict(h)
    w = [i for i in items if i["in_wrong_s42_lossmap"]]
    out = {"arm": "H", "set": "vpara", "seeds": SEEDS, "threshold": a.threshold, "model": LM.MODEL, "gateway_cost_usd": round(cost, 5), "cached": cached,
           "wrong_s42_set": summ(w), "all_judged": summ(items),
           "correctness_range_hist": {"wrong_s42_set": rhist(w), "all_judged": rhist(items)},
           "n_range_ge2": {"wrong_s42_set": sum(i["range"] >= 2 for i in w), "all_judged": sum(i["range"] >= 2 for i in items)},
           "mean_range": {"wrong_s42_set": round(statistics.mean(i["range"] for i in w), 3), "all_judged": round(statistics.mean(i["range"] for i in items), 3)},
           "mean_correctness_per_seed": {s: round(statistics.mean(i["correctness"][s] for i in items), 3) for s in SEEDS},
           "items": items}
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("gateway_cost_usd", "cached", "wrong_s42_set", "all_judged", "correctness_range_hist", "n_range_ge2")}, indent=1))

if __name__ == "__main__": main()
