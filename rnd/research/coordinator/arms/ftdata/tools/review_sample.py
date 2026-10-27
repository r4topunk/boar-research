#!/usr/bin/env python3
"""Seeded (46) pick of 10 PASSING pilot examples -> review-sample-10.md for the coordinator's separate Opus reviewer.
No review is done here. Usage: python3 review_sample.py [pilot-50.jsonl] [review-sample-10.md]"""
import json, random, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
P = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "pilot-50.jsonl"
O = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "review-sample-10.md"
rows = [json.loads(l) for l in P.read_text().splitlines() if l.strip()]
passing = [r for r in rows if r["pass"]]
pick = sorted(random.Random(46).sample(passing, min(10, len(passing))), key=lambda r: r["id"])
out = ["# FTDATA pilot: review sample (10 passing examples, seed 46)", "",
       "For the coordinator's SEPARATE Opus reviewer. Bar (criterion): <= 1/10 examples with an unsupported claim.",
       "Per example, judge: does every claim in ANSWER follow from PASSAGES? Mark each example SUPPORTED or",
       "UNSUPPORTED (quote the unsupported claim). Passage roles are shown; the teacher did not see them.", ""]
for r in pick:
    out += [f"## {r['id']} ({r['pack']}, {r['qtype']}, {r['words']} words)", "", f"**Question:** {r['question']}", "", "**Passages:**", ""]
    for i, p in enumerate(r["passages"], 1):
        out += [f"[{i}] {p['title']} ({p['source']}, {p['role']})", "", "```text", p["text"], "```", ""]
    out += ["**Answer:**", "", "```text", r["answer"], "```", "", "Verdict: ____", ""]
O.write_text("\n".join(out))
print(O, len(pick), [r["id"] for r in pick])
