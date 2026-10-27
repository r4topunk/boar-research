#!/usr/bin/env python3
"""exp-04 rows: exp-03's 256 hand-labelled answers + the Opus+web reference + the item rubric.

hand4 (Plumb's blind labels mapped to Jev's 4 classes):
  pass -> correct | cw -> confident_wrong | fail, empty -> wrong_or_incomplete_hedged | refused, declined -> refused
Split (coordinator): TUNE = iPhone runs 2-3 (P2, P3); TEST = run 4 Maple (H2) + baseline-mix 4B/Ling + 1.5B (H1).
`app_declined` marks the 45 iPhone rows whose text is the app's fixed decline message (trivial for any classifier;
metrics are reported with and without them).
"""
import json
B = "<workspace>"
refs = {r["id"]: r for r in map(json.loads, open(f"{B}/rnd/plumb/data/claude-code__opus.jsonl"))}
qs = {q["id"]: q for q in map(json.loads, open(f"{B}/rnd/lantern/handoff/questions.vitalik-lantern.jsonl"))}
M = {"pass": "correct", "cw": "confident_wrong", "fail": "wrong_or_incomplete_hedged", "empty": "wrong_or_incomplete_hedged",
     "refused": "refused", "declined": "refused"}
tune, test = [], []
for l in open(f"{B}/rnd/kiln/exp-03-o2/inputs.jsonl"):
    r = json.loads(l)
    ref = refs[r["queryId"]]
    row = {"src": r["src"], "model": r["model"], "queryId": r["queryId"], "category": r["category"], "query": r["query"],
           "answer": r["answer"], "hand_raw": r["label"], "hand4": M[r["label"]], "app_declined": r["label"] == "declined",
           "reference": ref["answer"], "rubric": qs[r["queryId"]].get("notes", ""),
           "titles": r["citedTitles"] or r["promptTitles"]}
    (tune if r["src"] in ("P2", "P3") else test).append(row)
for name, rows in (("rows-tune.jsonl", tune), ("rows-test.jsonl", test)):
    with open(name, "w") as f:
        for x in rows:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    from collections import Counter
    print(name, len(rows), dict(Counter(x["hand4"] for x in rows)), "app_declined", sum(x["app_declined"] for x in rows))
