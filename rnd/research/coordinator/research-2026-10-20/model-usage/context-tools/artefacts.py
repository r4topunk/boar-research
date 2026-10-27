#!/usr/bin/env python3
"""Text artefacts inside prompt chunks by pack: space-before-punctuation holes ("the town of near ."), empty parens, per pack domain."""
import json, re, sys
from collections import Counter, defaultdict
C = "cap"
sys.path.insert(0, ".")
pat_hole = re.compile(r"\b(?:of|near|in|at|to|from|and|the|with|by|between|or|as|is|was|for)\s+[.,;:)]")
pat_paren = re.compile(r"\(\s*[,;]?\s*\)")
stats = defaultdict(lambda: Counter()); ex = defaultdict(list)
seen = set()
for run in ["lp-K1-v01-s42", "lp-K1-cm-s42", "lp-K3-st-s42", "lp-K0-v01-s42", "lp-K0-cm-s42"]:
    tr = {json.loads(l)["itemId"]: json.loads(l) for l in open(f"{C}/{run}.traces.jsonl")}
    for l in open(f"{C}/{run}.prompts.jsonl"):
        p = json.loads(l); s = p["messages"][0]["content"]
        if "\n\nContext:\n" not in s: continue
        parts = re.split(r"\n\n(?=\[\d+\] )", s.split("\n\nContext:\n", 1)[1])
        kept = tr[p["itemId"]]["retrieval"]["kept"]
        for k, part in enumerate(parts):
            src = kept[k]["source"] if k < len(kept) else ""
            m = re.search(r"https?://([^/]+)", src or ""); dom = m.group(1) if m else "corpus/other"
            key = (dom, part)
            if key in seen: continue
            seen.add(key)
            st = stats[dom]; st["chunks"] += 1
            h = pat_hole.findall(part); pp = pat_paren.findall(part)
            if h: st["hole"] += 1; ex[dom].append(part[max(0, pat_hole.search(part).start() - 60): pat_hole.search(part).end() + 20].replace("\n", " "))
            if pp: st["empty_paren"] += 1
for d, c in sorted(stats.items(), key=lambda x: -x[1]["chunks"]):
    print(d, dict(c))
    for e in ex[d][:4]: print("   ex:", e)
