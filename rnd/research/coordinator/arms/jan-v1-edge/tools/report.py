#!/usr/bin/env python3
"""JAN-V1-EDGE per-run report (0 LLM), JAN-criterion.md §2 extras. Usage: python3 -I report.py <cand traces.jsonl> <K0|K1>
Prints: think-marker answers, [n] citation compliance on items where the control cites (live), answers with any [n] (live), mean output tokens and
totalMs on live items vs the control traces (lpctl-<K>-main + poolctl-<K>-st180, the sources of null-cal/control/pool-<K>.json)."""
import json, re, sys
A = "<workspace>/rnd/research/coordinator/arms"
K = sys.argv[2]
rd = lambda f: {json.loads(l)["itemId"]: json.loads(l) for l in open(f) if l.strip()}
C = rd(sys.argv[1]); T = {}
for f in (f"{A}/lp-screens/control/traces/lpctl-{K}-main-s42.traces.jsonl", f"{A}/null-cal/control/traces/poolctl-{K}-st180-s42.traces.jsonl"):
    T.update(rd(f))
ids = [i for i in C if i in T]
live = [i for i in ids if (T[i]["timing"].get("outputTokens") or 0) > 0]
cite = lambda t: bool(re.search(r"\[\d+\]", t["answer"]["text"]))
think = [i for i in C if "<think>" in C[i]["answer"]["text"] or "</think>" in C[i]["answer"]["text"]]
ctl_cites = [i for i in live if cite(T[i])]
m = lambda X, k, xs: round(sum(X[i]["timing"].get(k) or 0 for i in xs) / max(1, len(xs)), 1)
print(json.dumps(dict(n=len(C), matched=len(ids), live=len(live), think_marker_answers=len(think),
    cite_compliance=f"{sum(cite(C[i]) for i in ctl_cites)}/{len(ctl_cites)}", any_cite_cand=sum(cite(C[i]) for i in live), any_cite_ctl=len(ctl_cites),
    out_tok_cand=m(C, "outputTokens", live), out_tok_ctl=m(T, "outputTokens", live),
    out_tok_cand_p50=sorted(C[i]["timing"].get("outputTokens") or 0 for i in live)[len(live) // 2],
    at_cap_768=sum((C[i]["timing"].get("outputTokens") or 0) >= 768 for i in live),
    totalMs_cand=m(C, "totalMs", live), totalMs_ctl=m(T, "totalMs", live), wall_ratio=round(m(C, "totalMs", live) / m(T, "totalMs", live), 2))))
