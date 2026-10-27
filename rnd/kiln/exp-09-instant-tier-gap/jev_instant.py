#!/usr/bin/env python3
"""exp-09: Jev v2 (exp-04 frozen prompt) as second rater on what the instant tier showed (final answers and previews).
Reference per item: Veil's `answer` (o2 lots), Opus+web answer (rnd/plumb/data/claude-code__opus.jsonl) for the vitalik ids,
the rubric for bench dng/food items. Output: jev-instant.json {id: label}."""
import json, sys
B = "<workspace>"
sys.path.insert(0, f"{B}/rnd/kiln/exp-04-jev")
from jev_label import label_items
R = {r["id"]: r for r in map(json.loads, open("runs/exp09-ios-1.5b.jsonl"))}
hand = json.load(open("hand-labels-instant.json"))
refs = {}
for p in ("veil/o2-blind-items.jsonl", "veil/o2-blind-items-b2.jsonl", "veil/o2v2c-fresh.jsonl", "veil/o2v2c-fresh2.jsonl"):
    for q in map(json.loads, open(f"{B}/rnd/{p}")):
        refs[q["id"]] = q.get("answer", "")
for r in map(json.loads, open(f"{B}/rnd/plumb/data/claude-code__opus.jsonl")):
    refs.setdefault(r["id"], r["answer"])
for q in map(json.loads, open(f"{B}/rnd/bench/questions/v0/questions.public.jsonl")):
    refs.setdefault(q["id"], " ; ".join(q.get("rubric", [])))
ids = list(hand["final"]) + list(hand["preview"])
items = [{"id": i, "question": R[i]["question"], "reference": refs.get(i, ""), "rubric": "",
          "answer": R[i]["instantText"] or R[i]["answer"], "retrieved_titles": R[i]["instantSources"]} for i in ids]
out = {o["id"]: o["label"] for o in label_items(items, budget_usd=0.10)}
json.dump(out, open("jev-instant.json", "w"), indent=1)
print(len(out), "labelled; missing refs:", [i for i in ids if not refs.get(i)])
