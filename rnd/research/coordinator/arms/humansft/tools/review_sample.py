#!/usr/bin/env python3
"""HUMANSFT: seeded (51) pick of 20 ANSWERABLE CLAPnq + HAGRID rows (pool file order; Dolly excluded) ->
review-sample-20h.md for the coordinator's SEPARATE strict reviewer (rubric REVIEW-20.md). Per row ONLY: id,
passages (numbered, full text; "[i] title" when the source has titles, "[i]" otherwise), question, answer
(verbatim, HAGRID citation markers kept: [k] = passage k). No source tag beyond the id, no rubric, no review here.
Usage: python3 -I review_sample.py <humansft-pool.jsonl> <review-sample-20h.md>"""
import json, random, sys
from pathlib import Path

P, O = Path(sys.argv[1]), Path(sys.argv[2])
rows = [json.loads(l) for l in P.read_text().splitlines() if l.strip()]
elig = [r for r in rows if r["answerable"] and r["source"] in ("clapnq", "hagrid")]
pick = sorted(random.Random(51).sample(elig, 20), key=lambda r: r["id"])
out = [f"# HUMANSFT: review sample (20 answerable CLAPnq + HAGRID rows, seed 51)", ""]
for r in pick:
    out += [f"## {r['id']}", "", "**Passages:**", ""]
    for i, p in enumerate(r["passages"], 1):
        out += [f"[{i}] {p['title']}".rstrip(), "", "```text", p["text"], "```", ""]
    out += [f"**Question:** {r['question']}", "", "**Answer:**", "", "```text", r["answer"], "```", ""]
O.write_text("\n".join(out))
print(O, len(elig), len(pick), [r["id"] for r in pick])
