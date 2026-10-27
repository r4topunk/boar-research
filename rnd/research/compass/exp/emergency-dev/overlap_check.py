#!/usr/bin/env python3
"""For the COORDINATOR (Compass must not run it on blind data): word-Jaccard between this dev set's user turns and a blind
set's items. Prints only DEV ids and J values, never blind text, so the output is safe to send to Compass.
Usage: python3 overlap_check.py <blind items.jsonl>   (items need 'turns' or 'question')"""
import json, re, sys
from pathlib import Path
H = Path(__file__).resolve().parent
W = lambda s: set(re.findall(r"\w+", s.lower()))
U = lambda r: " ".join(t["text"] for t in r.get("turns", []) if t.get("role") == "user") or r.get("question", "")
D = [json.loads(l) for l in open(H / "dev.jsonl")]; B = [W(U(json.loads(l))) for l in open(sys.argv[1]) if l.strip()]
best = []
for r in D:
    w = W(U(r)); j = max((len(w & b) / max(1, len(w | b)) for b in B), default=0); best.append((round(j, 3), r["id"]))
best.sort(reverse=True)
print(f"dev {len(D)} vs blind {len(B)}: max J {best[0][0]}; dev items with J>=0.5: {sum(j >= 0.5 for j, _ in best)}; >=0.4: {sum(j >= 0.4 for j, _ in best)}")
print("top 10 (dev ids only):", best[:10])
