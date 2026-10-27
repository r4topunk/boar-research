#!/usr/bin/env python3
"""CHAINWHEN: answers/answers-M4.jsonl -> traces/chainwhen-OFF.traces.jsonl (150) and traces/chainwhen-ON.traces.jsonl (triggered ids only;
untriggered ON = OFF by construction and are not re-judged). Clones the cut7+X2b engine trace of each item (as PACKREAD to_traces.py)
and replaces answer.text, runId and config.arm. Usage: python3 -I to_traces.py"""
import json, glob, os, copy
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(H, "..", "headpass-st", "gen-x2b")
plan = json.load(open(os.path.join(H, "data", "plan.json")))
eng = {}
for f in glob.glob(os.path.join(SRC, "st-*-cut7-headpassx2b-s42.traces.jsonl")):
    for l in open(f):
        t = json.loads(l); eng[t["itemId"]] = t
rows = {}
for l in open(os.path.join(H, "answers", "answers-M4.jsonl")):
    r = json.loads(l); rows[(r["arm"], r["id"])] = r
for arm in ("OFF", "ON"):
    ids = [p["id"] for p in plan if arm == "OFF" or p["branch"] in ("pick>1", "pick0")]
    run = f"chainwhen-{arm}"; n = 0
    with open(os.path.join(H, "traces", run + ".traces.jsonl"), "w") as o:
        for i in ids:
            if (arm, i) not in rows: continue
            t = copy.deepcopy(eng[i]); r = rows[(arm, i)]
            t["runId"] = run; t["config"]["arm"] = run; t["answer"] = dict(t["answer"], text=r["text"])
            t["error"] = None if r["text"] else "empty-answer"
            t.setdefault("timing", {})["chainwhenMs"] = r["ms"]; o.write(json.dumps(t, ensure_ascii=False) + "\n"); n += 1
    open(os.path.join(H, "traces", run + ".ids"), "w").write("".join(i + "\n" for i in ids if (arm, i) in rows))
    print(run, n, "/", len(ids), "traces")
