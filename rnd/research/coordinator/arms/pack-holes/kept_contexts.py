#!/usr/bin/env python3 -I
"""Hole share among chunks actually placed in LITEPACKS prompts. usage: kept_contexts.py <cap dir> <out.json>
Reads <run>.prompts.jsonl + <run>.traces.jsonl (never blind/): parts of 'Context:' split like artefacts.py; domain from
trace retrieval.kept[k].source. Hole = any STRONG pattern of holes.py (full set and a 'core' subset)."""
import sys, re, json, os, importlib.util
from collections import Counter, defaultdict
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("holes", os.path.join(here, "holes.py")); h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
CORE = ["empty_paren", "paren_lead_punct", "paren_dash_only", "prep_punct", "born_died_empty", "lang_label_empty", "orphan_modifier"]
cap = sys.argv[1]
runs = sorted({f.split(".")[0] for f in os.listdir(cap) if f.endswith(".prompts.jsonl")})
res = {}
for run in runs:
    tr = {json.loads(l)["itemId"]: json.loads(l) for l in open(f"{cap}/{run}.traces.jsonl")}
    c = Counter(); items_fact = set(); dom = defaultdict(Counter); items_hole = set(); items = set(); ex = []
    for l in open(f"{cap}/{run}.prompts.jsonl"):
        p = json.loads(l); s = p["messages"][0]["content"]
        if "\n\nContext:\n" not in s: continue
        items.add(p["itemId"])
        parts = re.split(r"\n\n(?=\[\d+\] )", s.split("\n\nContext:\n", 1)[1])
        kept = tr[p["itemId"]]["retrieval"]["kept"]
        for k, part in enumerate(parts):
            src = (kept[k]["source"] if k < len(kept) else "") or ""
            m = re.search(r"https?://([^/\s)]+)", src); d = m.group(1) if m else "other(" + src[:24] + ")"
            c["chunks"] += 1; dom[d]["chunks"] += 1
            hits = [n for n in h.STRONG if h.PATTERNS[n].search(part)]
            core = [n for n in hits if n in CORE]
            if hits: c["hole_any"] += 1; dom[d]["hole_any"] += 1
            if any(n in h.FACT for n in core): c["hole_fact"] += 1; items_fact.add(p["itemId"])
            if core:
                c["hole_core"] += 1; dom[d]["hole_core"] += 1; items_hole.add(p["itemId"])
                if len(ex) < 12:
                    mm = h.PATTERNS[core[0]].search(part)
                    ex.append({"item": p["itemId"], "q": tr[p["itemId"]]["question"][:100], "dom": d, "pattern": core[0],
                               "ctx": part[max(0, mm.start() - 70): mm.end() + 40].replace("\n", " ")})
    res[run] = {"items": len(items), "items_with_core_hole": len(items_hole), "chunks": c["chunks"], "chunks_hole_any": c["hole_any"],
                "chunks_hole_core": c["hole_core"], "chunks_hole_fact": c["hole_fact"], "items_with_fact_hole": len(items_fact), "by_domain": {k: dict(v) for k, v in dom.items()}, "examples": ex}
    print(run, "items", len(items), "w/hole", len(items_hole), "chunks", c["chunks"], "core", c["hole_core"], "fact", c["hole_fact"], "items_fact", len(items_fact), "any", c["hole_any"])
json.dump(res, open(sys.argv[2], "w"), indent=1, ensure_ascii=False)
