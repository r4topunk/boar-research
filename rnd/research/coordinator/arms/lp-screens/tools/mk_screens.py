#!/usr/bin/env python3
"""Stage-1 screen lists (0 LLM) from the MacBook LITEPACKS judgments (GRILL-2026-10-20 Q6). Usage: python3 -I mk_screens.py
MAIN n 97 = data/v01-57.ids + qa-cooking-se 20 + qa-money-se 20 (as arms/litepacks/tools/agg.py). Per pack set K0 / K1:
  PROBLEMS  = every MAIN item that is a confident error (CE) in that arm: not declined and judge correctness (mean of both orders) <= 1.5 (agg.py).
  SENTINELS = 10 MAIN items the arm gets right: not CE, not declined, correctness == 5.0 (top of the 1-5 scale; if too few, best by correctness),
              6 from v01 + 4 from cm, each group ordered by ascending sha256(id) (deterministic).
K1 rows reuse K0 judgments for byte-identical answers (as agg.py). Writes screen-<K>.ids (problems then sentinels, sorted within each) + .sha256 + screen-<K>.json."""
import json, glob, hashlib, os
LP = "<workspace>/rnd/research/coordinator/arms/litepacks"; H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
def traces(a):
    out = {}
    for f in sorted(glob.glob(f"{LP}/traces/lp-{a}-*-s42.traces.jsonl")):
        if "smoke" in f: continue
        for t in rd(f): out[t["itemId"]] = t
    return out
def judg(a):
    by = {}
    for f in sorted(glob.glob(f"{LP}/judgments/lp-{a}-*.judgments.jsonl")):
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    return {q: sum(m["boar"]["correctness"] for m in v.values()) / 2 for q, v in by.items() if len(v) == 2}
TR = {a: traces(a) for a in ("K0", "K1")}; JR = {a: judg(a) for a in ("K0", "K1")}
V01 = [l.strip() for l in open(f"{LP}/data/v01-57.ids") if l.strip()]
CM = sorted(i for i in TR["K0"] if i.startswith("st-qa-cooking-se") or i.startswith("st-qa-money-se"))
MAIN = V01 + CM; assert len(MAIN) == 97
ans = lambda a, i: TR[a][i]["answer"]["text"]
def corr(a, i): return JR["K0"][i] if (a == "K0" or ans(a, i) == ans("K0", i)) else JR[a][i]
sh = lambda i: hashlib.sha256(i.encode()).hexdigest()
for a in ("K0", "K1"):
    dec = {i: bool(TR[a][i]["answer"].get("declined")) for i in MAIN}; c = {i: corr(a, i) for i in MAIN}
    prob = sorted(i for i in MAIN if not dec[i] and c[i] <= 1.5)
    ok = [i for i in MAIN if not dec[i] and c[i] > 1.5]
    def pick(pool, k):
        pool = sorted(pool, key=lambda i: (-c[i], sh(i)))  # top correctness first (== 5.0 when enough), ties by ascending sha256(id)
        top = [i for i in pool if c[i] == 5.0]
        return sorted(top, key=sh)[:k] if len(top) >= k else pool[:k]
    sv = pick([i for i in ok if i in V01], 6); sc = pick([i for i in ok if i in CM], 4)
    sent = sorted(sv + sc)
    ids = prob + sent; p = f"{H}/screen-{a}.ids"
    open(p, "w").write("".join(i + "\n" for i in ids))
    s = hashlib.sha256(open(p, "rb").read()).hexdigest(); open(p + ".sha256", "w").write(f"{s}  screen-{a}.ids\n")
    meta = dict(pack_set=a, problems=prob, sentinels=sent, sentinel_corr={i: c[i] for i in sent}, n_problems=len(prob), n_sentinels=len(sent),
                problems_v01=sum(i in V01 for i in prob), problems_cm=sum(i in CM for i in prob), ids_sha256=s,
                top_pool_v01=sum(1 for i in ok if i in V01 and c[i] == 5.0), top_pool_cm=sum(1 for i in ok if i in CM and c[i] == 5.0),
                fixed_needed=-(-22 * len(prob) // 100))
    json.dump(meta, open(f"{H}/screen-{a}.json", "w"), indent=1)
    print(a, "problems", len(prob), f"(v01 {meta['problems_v01']}, cm {meta['problems_cm']})", "sentinels", len(sent), "pool@5", meta["top_pool_v01"], meta["top_pool_cm"], "need", meta["fixed_needed"], s[:16])
