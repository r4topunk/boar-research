#!/usr/bin/env python3
"""Round-6 cards (CPR ×3, poisoning) and their 36 mutants under safety v0.9 (same procedure as round6.py §3–4)."""
import importlib.util, sys
from pathlib import Path
H = Path(__file__).resolve().parent; FA = H.parent / "first-aid-cards"
sys.path.insert(0, str(FA)); import round6
spec = importlib.util.spec_from_file_location("sc", H / "safety_check.v0.9.1.py"); sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
S = sc.load(rules_path=H / "rules.v0.9.1.json", overlay_path=H / "overlay.v0.4.json")
st = lambda text, *c: {"text": text, "cites": list(c)}; L = lambda t, s, c: {"title": t, "steps": s, "call": c}
CARDS = {c["id"]: c for c in round6.build(st, L)}
text = lambda x: "\n".join([x["title"]] + [s["text"] for s in x["steps"]] + [x["call"]["text"]])
unsafe = 0
for c in CARDS.values():
    for lg in ("en", "pt", "es"):
        rules = sorted(set(c["rules"]) | set(sc.rules_by_topic(c["topic"][lg], S)))
        hs = [h for h in sc.check(text(c["langs"][lg]), rules, S) if h.get("status", "unsafe") in ("unsafe", "review")]
        unsafe += len(hs)
        for h in hs: print("CLEAN-FAIL", c["id"], lg, h["rule"], h.get("status"), h.get("sentence", "")[:90])
print("round-6 card texts flagged:", unsafe, "/ 12 texts")
caught = tot = 0
for cid, mid, by_lang in round6.MUTANTS6:
    c = CARDS[cid]
    for lg, edits in by_lang.items():
        x = {"title": c["langs"][lg]["title"], "steps": [dict(s) for s in c["langs"][lg]["steps"]], "call": dict(c["langs"][lg]["call"])}
        for slot, t in edits:
            if slot == "call": x["call"]["text"] = t
            elif slot == "+": x["steps"].append({"text": t})
            else: x["steps"][slot]["text"] = t
        topic = sc.rules_by_topic(c["topic"][lg], S)
        r = [h["rule"] for h in sc.check(text(x), topic, S) if h.get("status", "unsafe") in ("unsafe", "review")]
        tot += 1; caught += bool(r)
        if not r: print("  MISSED", cid, mid, lg)
print(f"mutants caught (unsafe or review) with topic-only selection: {caught}/{tot}")
