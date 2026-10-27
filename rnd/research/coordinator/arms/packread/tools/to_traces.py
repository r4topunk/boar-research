#!/usr/bin/env python3
"""PACKREAD: answers-<MODEL>.jsonl -> traces/packread-<MODEL>-<ARM>.traces.jsonl (one per arm) by cloning the cut7+X2b engine trace of each item
and replacing answer.text, runId and config.arm. Also writes the anchor traces (engine answers, untouched) for the 54 ids.
Usage: python3 -I to_traces.py <answers.jsonl ...>"""
import json, glob, os, sys, copy
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(H, "..", "headpass-st", "gen-x2b")
ids = [l.strip() for l in open(os.path.join(H, "ids-54.ids")) if l.strip()]
eng = {}
for f in glob.glob(os.path.join(SRC, "st-*-cut7-headpassx2b-s42.traces.jsonl")):
    for l in open(f):
        t = json.loads(l); eng[t["itemId"]] = t
os.makedirs(os.path.join(H, "traces"), exist_ok=True)
assert all(i in eng for i in ids)
with open(os.path.join(H, "traces", "packread-anchor-engine.traces.jsonl"), "w") as o:
    for i in ids:
        t = copy.deepcopy(eng[i]); t["runId"] = "packread-anchor-engine"; o.write(json.dumps(t, ensure_ascii=False) + "\n")
for af in sys.argv[1:]:
    by = {}
    for l in open(af):
        r = json.loads(l); by.setdefault((r["model"], r["arm"]), {})[r["id"]] = r
    for (m, arm), rows in sorted(by.items()):
        run = f"packread-{m}-{arm}"; n = 0
        with open(os.path.join(H, "traces", run + ".traces.jsonl"), "w") as o:
            for i in ids:
                if i not in rows: continue
                t = copy.deepcopy(eng[i]); r = rows[i]
                t["runId"] = run; t["config"]["arm"] = run; t["answer"] = dict(t["answer"], text=r["text"])
                t["error"] = None if r["text"] else "empty-answer"
                t.setdefault("timing", {})["packreadMs"] = r["ms"]; o.write(json.dumps(t, ensure_ascii=False) + "\n"); n += 1
        print(run, n, "traces", "MISSING" if n < len(ids) else "")
