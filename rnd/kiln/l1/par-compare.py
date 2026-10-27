#!/usr/bin/env python3
"""PARALLEL.md identity table: each run vs the N=1 reference (par-n1), same seed. Per item: identical answer text,
route identity (task, tier, outcome, reasonCodes), source identity (retrieval.raw, retrieval.kept, answer.shown), and
first differing character for changed texts. Reads traces only."""
import json, sys
R = "<workspace>/boar-eval/runs/kiln/l1/{}-retrieval-inkit-s42/traces.jsonl"
def load(label): return {t["itemId"]: t for t in map(json.loads, open(R.format(label))) }
def route(t): r = t["route"]; return (r["task"], r["tier"], r["outcome"], tuple(r["reasonCodes"]))
def srcs(t): k = lambda xs: tuple((x["title"], x["section"]) for x in xs); return (k(t["retrieval"]["raw"]), k(t["retrieval"]["kept"]), tuple(t["answer"]["shown"]))
def first_diff(a, b): return next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
ref = load(sys.argv[1] if len(sys.argv) > 1 else "par-n1")
for label in sys.argv[2:] or ["par-n1rep", "par-std", "par-n2", "par-n3", "par-n4"]:
    try: run = load(label)
    except FileNotFoundError: print(f"{label}: missing"); continue
    ids = [i for i in ref if i in run]
    txt = [i for i in ids if run[i]["answer"]["text"] == ref[i]["answer"]["text"]]
    rt = [i for i in ids if route(run[i]) == route(ref[i])]
    sc = [i for i in ids if srcs(run[i]) == srcs(ref[i])]
    errs = sum(1 for t in run.values() if t.get("error"))
    changed = [f"{i}@{first_diff(run[i]['answer']['text'], ref[i]['answer']['text'])}" for i in ids if i not in txt]
    print(f"{label}\tn={len(ids)}\terrors={errs}\ttext={len(txt)}/{len(ids)}\troute={len(rt)}/{len(ids)}\tsources={len(sc)}/{len(ids)}\tchanged(first diff char)={' '.join(changed)}")
