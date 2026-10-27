#!/bin/bash
# NUMGUARD-r3 step 3 analysis (0 LLM): score_mr.py on the slice (A = cut 7, NGF = FINAL, NGR3), per-item table of the ever-fired items,
# citations on numguard items, v0.1 compare_ng.py + same_answer.py vs OFF.
set -u
A=<workspace>/rnd/research/coordinator/arms; N=$A/numguard; R=$N/runs; G=$N/aggregates
python3 -I $A/mathroute/tools/score_mr.py <workspace>/boar-eval/bench/slices/mathroute-v1/gold.jsonl $G/score_slice_r3.json A=$A/mathroute/runs/mr-A-s42.traces.jsonl NGF=$R/ngf-A-s42.traces.jsonl NGR3=$R/ngr3-A-s42.traces.jsonl > $R/r3-score-slice.txt 2>&1; tail -4 $R/r3-score-slice.txt
python3 -I - $G/score_slice_r3.json $R/ngr3-A-s42.traces.jsonl $R/ngf-A-s42.traces.jsonl > $R/r3-slice-items.txt <<'EOPY'
import json, sys
d = json.load(open(sys.argv[1])); it = d["items"]
tr = lambda p: {(t := json.loads(l))["itemId"]: t for l in open(p) if l.strip()}
R3, F = tr(sys.argv[2]), tr(sys.argv[3])
codes = lambda t: (t.get("route") or {}).get("reasonCodes") or []
fired = [i for i in it if any(c.startswith("detector:fire") or c == "detector:numeric-guard" or c.startswith("numguard") for c in codes(R3[i]) + codes(F[i]))]
print("correct", {k: sum(v[k]["correct"] for v in it.values()) for k in ("A", "NGF", "NGR3")})
print("correct_to_wrong_vs_cut7", [i for i in it if it[i]["A"]["correct"] and not it[i]["NGR3"]["correct"]])
print("lost_vs_final", [i for i in it if it[i]["NGF"]["correct"] and not it[i]["NGR3"]["correct"]])
print("gained_vs_cut7", [i for i in it if it[i]["NGR3"]["correct"] and not it[i]["A"]["correct"]])
print("text_changed_vs_cut7", [i for i in it if " ".join((it[i]["A"]["text"] or "").split()) != " ".join((it[i]["NGR3"]["text"] or "").split())])
ng = [i for i in it if any(c in ("numguard:fired", "numguard:no-calculator") for c in codes(R3[i]))]
print("numguard_items", ng, "cited", sum(it[i]["NGR3"]["cited"] for i in ng))
for k in ("A", "NGF", "NGR3"): print(k, "cited_total", sum(v[k]["cited"] for v in it.values()), "extra", sum(v[k]["extra"] for v in it.values()), "headline", sum(v[k]["headline"] for v in it.values()))
for i in fired:
    print("ITEM", i, {k: {x: it[i][k][x] for x in ("correct", "cited", "calc", "retrieved")} for k in ("A", "NGF", "NGR3")})
    print("  codes", [c for c in codes(R3[i]) if c.startswith(("detector", "numguard", "retrieve", "answer:", "grounding"))])
    print("  text", (it[i]["NGR3"]["text"] or "")[:240])
EOPY
cat $R/r3-slice-items.txt
python3 -I $N/tools/compare_ng.py $R/v01-ng-off-s42.traces.jsonl $R/v01-ngr3-on-s42.traces.jsonl $R/r3-route-replay.jsonl v01 > $R/v01-r3-compare-vs-off.json; cat $R/v01-r3-compare-vs-off.json
python3 -I $A/seedgen/tools/same_answer.py $R/v01-ng-off-s42.traces.jsonl $R/v01-ngr3-on-s42.traces.jsonl --label r3-vs-off > $R/v01-r3-same_answer-vs-off.txt; tail -1 $R/v01-r3-same_answer-vs-off.txt | cut -c1-400
