#!/usr/bin/env python3
"""Rewrite the funnel-K3 traces' detector codes with a head's p (GGUF embeddings of the item question; 0 LLM) for replay-sweep --tasks-from.
Only items that carry a detector:p= code are touched (the others never call the detector). usage: mk_tasks.py <head.json> <out.jsonl>"""
import json, sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); import dlib
A = "<workspace>/rnd/research/coordinator/arms/"; W = A + "detector-hn/work/"
e = np.load(W + "emb.main97.npz"); p = dict(zip([str(i) for i in e["ids"]], dlib.head_p(dlib.load_head(sys.argv[1]), e["vecs"])))
n = ch = 0
with open(sys.argv[2], "w") as f:
    for l in open(A + "coverage-map/replay/funnel-K3.traces.jsonl"):
        t = json.loads(l); rc = t["route"]["reasonCodes"]
        if any(c.startswith("detector:p=") for c in rc):
            q = float(p[t["itemId"]]); new = []
            for c in rc:
                if c == "detector:fire": continue
                new.append(f"detector:p={q:.3f}" if c.startswith("detector:p=") else c)
                if c.startswith("detector:p=") and q >= 0.2: new.append("detector:fire")
            ch += new != rc; t["route"]["reasonCodes"] = new; n += 1
        f.write(json.dumps(t, ensure_ascii=False) + "\n")
print("detector items", n, "codes changed", ch)
