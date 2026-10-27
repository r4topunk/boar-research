#!/usr/bin/env python3
"""v0.8.8 wrong-card over every DEV output that shows a card (boar-eval/runs, sonar/exp; never blind/, veil, or Sonar's
leak/ dir). Dedupes by (itemId, answer text): one Jev call per distinct shown card answer. Conversation = the item's
turns when the item is a chat-slice or emergency-dev item, else the trace question. Prints counts per card key and every wrong-card
(id, key, p, first 140 chars of the question). Run: python3 scan_dev.py"""
import glob, json, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); from wrong_card import check, card_keys, answer_text
H = Path(__file__).resolve().parent; RND = H.parents[2]; BOAR = RND.parents[1]
CS = RND / "compass/chat-slice"
items = {}
for f in (CS / "slice.v0.jsonl", CS / "v1-fresh/slice.v1.jsonl", CS / "v2-fresh/slice.v2.jsonl", RND / "compass/exp/emergency-dev/dev.jsonl"):
    items.update({json.loads(l)["id"]: json.loads(l) for l in open(f)})
files = [f for f in glob.glob(str(BOAR / "boar-eval/runs/**/*.jsonl"), recursive=True) + glob.glob(str(RND / "sonar/exp/**/*.jsonl"), recursive=True)
         if "/blind/" not in f and "veil" not in f and "/leak/" not in f]
seen = {}; per_key = Counter(); n_answers = 0
for f in files:
    for l in open(f, errors="ignore"):
        if "fa-card-" not in l and "first-aid-card-" not in l: continue
        try: t = json.loads(l)
        except Exception: continue
        if not isinstance(t, dict) or not card_keys(t) or not answer_text(t): continue
        n_answers += 1
        k = (t.get("itemId"), answer_text(t))
        if k not in seen: seen[k] = t
res = []
for (iid, _), t in seen.items():
    r = check(t, items.get(iid)); res.append((r, t))
    for c in r["cards"]: per_key[c] += 1
bad = [(r, t) for r, t in res if r["status"] == "wrong-card"]
print(f"files {len(files)}; card answers {n_answers}; distinct {len(res)}; wrong-card {len(bad)}")
print("distinct per card:", dict(per_key.most_common()))
for r, t in sorted(bad, key=lambda x: x[0]["p_right"]):
    print(f"  {r['itemId']} {r['cards']} p={r['p_right']:.2f} | {(t.get('question') or '')[:110]!r} || ANSWER {answer_text(t)[:90]!r}")
