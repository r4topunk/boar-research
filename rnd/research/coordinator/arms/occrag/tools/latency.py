#!/usr/bin/env python3
"""OCCRAG latency / length / route report (0 LLM). Usage: python3 -I latency.py <candidate traces.jsonl> <control traces.jsonl> <candidate .occ.jsonl> [--json out]
Wall time per answer = trace timing.totalMs (mini, desktop CPU) over items in both files without error; median candidate vs control and the
1.5x clause. Answer length = words of answer.text. Routes from the sidecar (one row per answer generation): occ, occ-abstain-fallback-qwen
(UNANSWERABLE / "Not enough information" = the false-UNANSWERABLE candidates), occ-malformed-fallback-qwen, occ-looped-fallback-qwen,
qwen-nosource, qwen-prompt; items with no generation (facts/places answers) have no row. OCC tokens = all tokens OCC generated for the
answer (trace + answer + forced close), on the rows that went to OCC."""
import json, statistics as st, sys, collections
ld = lambda p: {r["itemId"]: r for r in map(json.loads, open(p))}
c, k = ld(sys.argv[1]), ld(sys.argv[2]); occ = [json.loads(l) for l in open(sys.argv[3])]
ids = [i for i in c if i in k and not c[i].get("error") and not k[i].get("error")]
med = lambda xs: st.median(xs) if xs else None
cw, kw = [c[i]["timing"]["totalMs"] for i in ids], [k[i]["timing"]["totalMs"] for i in ids]
ow = [c[i]["timing"]["totalMs"] for i in ids if any(x["itemId"] == i and x["route"].startswith("occ") for x in occ)]
okw = [k[i]["timing"]["totalMs"] for i in ids if any(x["itemId"] == i and x["route"].startswith("occ") for x in occ)]
tt = sorted(x["occTokens"] for x in occ if "occTokens" in x)
r = dict(n=len(ids), errors=sum(1 for i in c if c[i].get("error")),
         wall_ms_median_cand_ctl=[med(cw), med(kw)], wall_ratio=round(med(cw) / med(kw), 2), latency_clause_le_1_5x=med(cw) <= 1.5 * med(kw),
         wall_ms_median_occ_items_cand_ctl=[med(ow), med(okw)],
         answer_words_median_cand_ctl=[med([len(c[i]["answer"]["text"].split()) for i in ids]), med([len(k[i]["answer"]["text"].split()) for i in ids])],
         routes=dict(collections.Counter(x["route"] for x in occ)), occ_rows=len(tt),
         occ_tokens_median=med(tt), occ_tokens_p90=tt[int(0.9 * (len(tt) - 1))] if tt else None, occ_tokens_max=tt[-1] if tt else None,
         ctl_output_tokens_median=med([k[i]["timing"]["outputTokens"] or 0 for i in ids if k[i]["timing"]["outputTokens"]]),
         forced=sum(1 for x in occ if x.get("forced")), identical_text_to_control=sum(1 for i in ids if c[i]["answer"]["text"] == k[i]["answer"]["text"]))
print(json.dumps(r, indent=1))
if "--json" in sys.argv: json.dump(r, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
