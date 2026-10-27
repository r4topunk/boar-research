#!/bin/bash
# NUMGUARD-FINAL step 3 analysis (0 LLM): score_mr.py on the slice (A = cut 7, NGR2, NGF), per-item table of the 5 ever-fired items,
# citations on guard-fired model-answered items, v0.1 compare_ng.py + same_answer.py vs OFF and vs r2.
set -u
A=<workspace>/rnd/research/coordinator/arms; N=$A/numguard; R=$N/runs; G=$N/aggregates
python3 -I $A/mathroute/tools/score_mr.py <workspace>/boar-eval/bench/slices/mathroute-v1/gold.jsonl $G/score_slice_final.json A=$A/mathroute/runs/mr-A-s42.traces.jsonl NGR2=$R/ngr2-A-s42.traces.jsonl NGF=$R/ngf-A-s42.traces.jsonl > $R/final-score-slice.txt 2>&1; tail -3 $R/final-score-slice.txt
python3 -I - $G/score_slice_final.json $R/ngf-A-s42.traces.jsonl $R/ngr2-A-s42.traces.jsonl > $R/final-slice-items.txt <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); it = d["items"]
tr = lambda p: {(t := json.loads(l))["itemId"]: t for l in open(p) if l.strip()}
F, R2 = tr(sys.argv[2]), tr(sys.argv[3])
codes = lambda t: (t.get("route") or {}).get("reasonCodes") or []
fired = [i for i in it if any(c.startswith("detector:fire") or c == "detector:numeric-guard" or c.startswith("numguard") for c in codes(F[i]) + codes(R2[i]))]
c2w = [i for i in it if it[i]["NGR2"]["correct"] and not it[i]["NGF"]["correct"]]
changed = [i for i in it if " ".join((it[i]["NGR2"]["text"] or "").split()) != " ".join((it[i]["NGF"]["text"] or "").split())]
gf_model = [i for i in it if "numguard:fired" in codes(F[i]) and not it[i]["NGF"]["calc"]]
print("correct_to_wrong_vs_r2", c2w); print("text_changed_vs_r2", changed)
print("guard_fired_model_answered", gf_model, "cited", sum(it[i]["NGF"]["cited"] for i in gf_model))
for k in ("A", "NGR2", "NGF"): print(k, "cited_total", sum(v[k]["cited"] for v in it.values()), "extra", sum(v[k]["extra"] for v in it.values()), "headline", sum(v[k]["headline"] for v in it.values()))
print("cited items NGF", [i for i in it if it[i]["NGF"]["cited"]], "A", [i for i in it if it[i]["A"]["cited"]])
for i in fired:
    print("ITEM", i, {k: {x: it[i][k][x] for x in ("correct", "cited", "calc", "retrieved", "extra", "headline")} for k in ("A", "NGR2", "NGF")})
    print("  codes", [c for c in codes(F[i]) if c.startswith(("detector", "numguard", "retrieve", "answer:"))])
    print("  text", it[i]["NGF"]["text"][:300])
PY
cat $R/final-slice-items.txt
for ref in off:v01-ng-off-s42 r2:v01-ngr2-on-s42; do n=${ref%%:*}; f=${ref#*:}
  python3 -I $N/tools/compare_ng.py $R/$f.traces.jsonl $R/v01-ngf-on-s42.traces.jsonl $R/final-route-replay.jsonl v01 > $R/v01-final-compare-vs-$n.json; cat $R/v01-final-compare-vs-$n.json
  python3 -I $A/seedgen/tools/same_answer.py $R/$f.traces.jsonl $R/v01-ngf-on-s42.traces.jsonl --label final-vs-$n > $R/v01-final-same_answer-vs-$n.txt; tail -1 $R/v01-final-same_answer-vs-$n.txt | cut -c1-400
done
