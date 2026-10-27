#!/usr/bin/env python3
"""LITE17: answers/answers-Q17.jsonl -> traces/lite17-{B,T,Q,S}.traces.jsonl (+ .ids) by cloning the cut7+X2b engine trace of each item
(as PACKREAD/CHAINWHEN to_traces.py) and replacing answer.text, runId and config.arm. Q uses the pass-2 (Q2) answer; T uses message.content only
(reasoning split by --reasoning-format deepseek, never judged); S only for items where S != B (S = B elsewhere by construction).
Usage: python3 -I to_traces.py"""
import json, glob, os, copy
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(H, "..", "headpass-st", "gen-x2b")
ids = [l.strip() for l in open(os.path.join(H, "data", "ids-150.ids")) if l.strip()]
s_ids = [l.strip() for l in open(os.path.join(H, "data", "ids-S.ids")) if l.strip()]
eng = {}
for f in glob.glob(os.path.join(SRC, "st-*-cut7-headpassx2b-s42.traces.jsonl")):
    for l in open(f):
        t = json.loads(l); eng[t["itemId"]] = t
rows = {}
for l in open(os.path.join(H, "answers", "answers-Q17.jsonl")):
    r = json.loads(l); rows[(r["arm"], r["id"])] = r
for run_arm, ans_arm, idl in (("B", "B", ids), ("T", "T", ids), ("Q", "Q2", ids), ("S", "S", s_ids)):
    run = f"lite17-{run_arm}"; got = [i for i in idl if (ans_arm, i) in rows]
    with open(os.path.join(H, "traces", run + ".traces.jsonl"), "w") as o:
        for i in got:
            t = copy.deepcopy(eng[i]); r = rows[(ans_arm, i)]
            t["runId"] = run; t["config"]["arm"] = run; t["answer"] = dict(t["answer"], text=r["text"])
            t["error"] = None if r["text"] else "empty-answer"
            t.setdefault("timing", {})["lite17Ms"] = r["ms"]; o.write(json.dumps(t, ensure_ascii=False) + "\n")
    open(os.path.join(H, "traces", run + ".ids"), "w").write("".join(i + "\n" for i in got))
    print(run, len(got), "/", len(idl), "traces")
