#!/usr/bin/env python3
"""G1 explanation: for every greedy speculative run, find the first diverging token vs the non-speculative greedy run and look up the
base run's top1-top2 logprob gap at that token (res_lp/baselp = greedy + top-2 logprobs; identical text to baseg expected).
usage: specdec_ties.py DATADIR"""
import json, sys, statistics as st
D = sys.argv[1]
def L(p): return {json.loads(l)["itemId"]: json.loads(l) for l in open(p)}
lp = L(f"{D}/res_lp/baselp.jsonl"); bg = L(f"{D}/res/baseg.jsonl")
print("baselp text == baseg text:", sum(lp[i]["text"] == bg[i]["text"] for i in lp), "/", len(lp))
out = {}
for name in ("q06n4g", "q06n8g", "q06n4p75g", "q06n8p75g"):
    q = L(f"{D}/res/{name}.jsonl"); gaps = []; same = 0; nd = 0
    for i, b in lp.items():
        if q[i]["text"] == b["text"]: same += 1; continue
        nd += 1
        t = b["text"]; o = q[i]["text"]
        j = next((k for k in range(min(len(t), len(o))) if t[k] != o[k]), min(len(t), len(o)))
        pos = 0; hit = None
        for tok in b["lp"]:
            s = tok[0]; nxt = pos + len(s.encode("utf-8").decode("utf-8", "ignore"))
            if pos <= j < max(nxt, pos + 1): hit = tok; break
            pos = nxt
        if hit is None: continue
        gaps.append(hit[1] - hit[2] if len(hit) > 3 else None)
    g = [x for x in gaps if x is not None]
    out[name] = dict(identical=same, diverged=nd, gap_median=st.median(g) if g else None, gap_p90=sorted(g)[int(.9 * (len(g) - 1))] if g else None,
                     gap_le_0_5=sum(x <= 0.5 for x in g), gap_le_1_0=sum(x <= 1.0 for x in g), n=len(g))
print(json.dumps(out, indent=1))
# reference: distribution of top1-top2 gap over ALL generated tokens of the base run
allg = [t[1] - t[2] for b in lp.values() for t in b["lp"] if len(t) > 3]
print("all tokens: n", len(allg), "share gap<=0.1:", round(sum(x <= .1 for x in allg) / len(allg), 4), "<=0.5:", round(sum(x <= .5 for x in allg) / len(allg), 4), "<=1:", round(sum(x <= 1 for x in allg) / len(allg), 4))
json.dump(out, open(f"{D}/res/ties.json", "w"), indent=1)
