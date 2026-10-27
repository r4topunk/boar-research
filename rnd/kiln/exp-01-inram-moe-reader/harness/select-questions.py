#!/usr/bin/env python3
"""Build the two question files of exp-01 (deterministic, no randomness).

(a) v2-hard12: 12 items of boar-app eval v2 (feat/eval-frontier eval/dataset/questions.v2.jsonl):
    6 crypto-expert, 4 math-reasoning, 2 travel-practical, evenly spaced over the ids sorted per category.
(b) lantern52: Lantern's handoff set (rnd/lantern/handoff/questions.vitalik-lantern.jsonl), minus items marked
    duplicate_of in rnd/lantern/vitalik-evalset.jsonl and minus venue-list ("near me" places, answered without LLM).
    Tagged b1 (a competitor team verbatim, source=a competitor repo@...) / b2 (the rest).
Usage: python3 select-questions.py <tree>/eval/dataset/questions.v2.jsonl <boar root> <out dir>
"""
import json, sys, os

v2_path, root, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)

def spaced(ids, k):
    ids = sorted(ids)
    return [ids[round(i * (len(ids) - 1) / (k - 1))] if k > 1 else ids[0] for i in range(k)]

v2 = [json.loads(l) for l in open(v2_path)]
pick = {"crypto-expert": 6, "math-reasoning": 4, "travel-practical": 2}
chosen = set()
for cat, k in pick.items():
    chosen |= set(spaced([q["id"] for q in v2 if q["category"] == cat], k))
with open(f"{out}/questions.v2-hard12.jsonl", "w") as f:
    for q in v2:
        if q["id"] in chosen:
            f.write(json.dumps(q) + "\n")

full = {r["id"]: r for r in map(json.loads, open(f"{root}/rnd/lantern/vitalik-evalset.jsonl"))}
hand = [json.loads(l) for l in open(f"{root}/rnd/lantern/handoff/questions.vitalik-lantern.jsonl")]
kept, slices = [], {}
for q in hand:
    meta = full.get(q["id"], {})
    if meta.get("duplicate_of") or q.get("duplicate_of"):
        continue
    if (meta.get("grading") or q.get("grading") or {}).get("type") == "venue-list":
        continue
    q.setdefault("gold", [])
    kept.append(q)
    slices[q["id"]] = "b1-competitor-app" if str(meta.get("source", "")).startswith("a competitor repo") else "b2-boar"
with open(f"{out}/questions.lantern52.jsonl", "w") as f:
    for q in kept:
        f.write(json.dumps(q) + "\n")
json.dump(slices, open(f"{out}/slices.lantern52.json", "w"), indent=1)
print(f"v2-hard12: {len(chosen)} {sorted(chosen)}")
print(f"lantern: {len(kept)} kept (b1={sum(v == 'b1-competitor-app' for v in slices.values())}, b2={sum(v == 'b2-boar' for v in slices.values())})")
