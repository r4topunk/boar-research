#!/usr/bin/env python3
"""FTDATA 1k: seeded (48) pick of 20 PASSING examples -> review-sample-20.md for the coordinator's separate Opus
reviewer (copy of the pilot review_sample.py; seed 48, n 20). Per example ONLY: id, passages (full text, as the teacher
saw them: "[i] title" + text), question, answer. No pack/qtype/role/word count, no rubric, no review done here.
Usage: python3 review_sample_1k.py [ftdata-1k.jsonl] [review-sample-20.md]"""
import json, random, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
P = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "ftdata-1k.jsonl"
O = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "review-sample-20.md"
rows = [json.loads(l) for l in P.read_text().splitlines() if l.strip()]
passing = [r for r in rows if r["pass"]]
pick = sorted(random.Random(48).sample(passing, min(20, len(passing))), key=lambda r: r["id"])
out = [f"# FTDATA 1k: review sample ({len(pick)} passing examples, seed 48)", ""]
for r in pick:
    out += [f"## {r['id']}", "", "**Passages:**", ""]
    for i, p in enumerate(r["passages"], 1):
        out += [f"[{i}] {p['title']}", "", "```text", p["text"], "```", ""]
    out += [f"**Question:** {r['question']}", "", "**Answer:**", "", "```text", r["answer"], "```", ""]
O.write_text("\n".join(out))
print(O, len(pick), [r["id"] for r in pick])
