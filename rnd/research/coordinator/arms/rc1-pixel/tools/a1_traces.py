#!/usr/bin/env python3
"""A1-RC1-SHIPPED-U (0 LLM): RC1 eval-hook rows.jsonl -> EvalTrace jsonl for judge.mjs (minimal native shape, as runs/device-poco-x6pro/native-x6-v01).
Usage: python3 -I a1_traces.py <rows.jsonl> <ids file> <out traces.jsonl>
warmup-000 is dropped. A row whose outcome != success or whose answer is empty gets error = <outcome> (judge.mjs --floor-errored scores it 1/1/1).
answer.cited = retrievedTitles (the judge sees only question, reference and answer text)."""
import json, sys
rows, idf, out = sys.argv[1:4]
ids = open(idf).read().split()
R = {}
for l in open(rows):
    r = json.loads(l)
    if r.get("queryId") in ids: R.setdefault(r["queryId"], r)
with open(out, "w") as f:
    for q in ids:
        r = R.get(q)
        if r is None:
            t = {"itemId": q, "answer": {"text": "", "cited": []}, "engine": {"arm": "rc1-shipped", "commit": "apk-2ef43258"}, "error": "missing-row",
                 "timing": {}, "runId": "rc-cv5-51-15b", "protocol": "1.0.0"}
        else:
            txt = r.get("answer") or ""; ok = r.get("outcome") == "success" and txt.strip() != ""
            t = {"itemId": q, "question": r.get("query"), "answer": {"text": txt, "cited": r.get("retrievedTitles") or [], "declined": False},
                 "engine": {"arm": "rc1-shipped", "commit": "apk-2ef43258"}, "error": None if ok else (r.get("outcome") or "empty"),
                 "timing": {"totalMs": r.get("totalLatencyMs")}, "runId": "rc-cv5-51-15b", "protocol": "1.0.0"}
        f.write(json.dumps(t, ensure_ascii=False) + "\n")
print(f"{len(ids)} traces, {sum(1 for q in ids if q in R)} rows found", file=sys.stderr)
