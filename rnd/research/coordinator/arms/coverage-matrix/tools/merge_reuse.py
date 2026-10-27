#!/usr/bin/env python3
"""COVERAGE-MATRIX judgment-reuse aggregate (0 LLM). Usage: python3 -I merge_reuse.py <traces.jsonl> <ids> <out.json> <agg1.json> [agg2.json ...]
Harness rule (LITEPACKS / GEMMA-PACKS): an answer whose text is byte-identical to an already judged answer of the same item reuses that judgment.
Per id: the first pooled aggregate (argument order) whose item text == this trace's answer text; if none matches, the first pooled row for the id
(then agg_run / run_cell see a text mismatch and the item is judged). Every id must have at least one pooled row."""
import json, sys
TRF, IDF, OUT, *POOL = sys.argv[1:]
tr = {json.loads(l)["itemId"]: json.loads(l)["answer"]["text"] for l in open(TRF) if l.strip()}
ids = [x for x in open(IDF).read().split() if x]
aggs = [(p, json.load(open(p))["items"]) for p in POOL]
items, src, reused = {}, {}, 0
for i in ids:
    cand = [(p, a[i]) for p, a in aggs if i in a]
    if not cand: sys.exit(f"no pooled row for {i}")
    hit = next(((p, r) for p, r in cand if r.get("text") == tr[i]), None)
    p, r = hit or cand[0]; reused += hit is not None
    items[i] = dict(r)  # fix 03:5x: full row (agg_run --control needs CE/warned/...); src[i] = p.split("/arms/")[-1] + (" (match)" if hit else " (no match)")
json.dump(dict(note="COVERAGE-MATRIX reuse aggregate (merge_reuse.py); not a measurement row", n=len(ids), reused=reused, source=src, items=items), open(OUT, "w"), indent=1)
print(f"reuse: {reused}/{len(ids)} byte-identical rows -> {OUT}")
