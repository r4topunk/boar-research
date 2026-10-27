#!/usr/bin/env python3
"""DETECTOR-HN reads 1-3 (+ MAIN fires) at the shipped threshold 0.2, v3b vs a candidate head, GGUF embeddings (0 LLM).
usage: reads.py <head.json> <out.json>"""
import json, sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); import dlib
W = "<workspace>/rnd/research/coordinator/arms/detector-hn/work/"; THR = 0.2
hb, hc = dlib.load_head(dlib.HEAD_V3B), dlib.load_head(sys.argv[1])
z = lambda s: np.load(W + f"emb.{s}.npz")
out = {"head": sys.argv[1], "thr": THR, "read1": {}, "read2": {}}
for s in ("compass300", "sonar903", "terse30", "ptmirror28", "v3b_val"):
    e = z(s); y = e["labels"]; pb, pc = dlib.head_p(hb, e["vecs"]), dlib.head_p(hc, e["vecs"])
    fb, fc = pb >= THR, pc >= THR; pos = y == 1; neg = y == 0
    out["read1"][s] = {"pos": int(pos.sum()), "recall_v3b": int((fb & pos).sum()), "recall_v3c": int((fc & pos).sum()),
                       "lost_pos": [str(i) for i in e["ids"][fb & ~fc & pos]], "gained_pos": int((~fb & fc & pos).sum()),
                       "neg": int(neg.sum()), "fp_v3b": int((fb & neg).sum()), "fp_v3c": int((fc & neg).sum())}
e = z("titles_heldout"); pb, pc = dlib.head_p(hb, e["vecs"]), dlib.head_p(hc, e["vecs"]); ck = np.array([i.startswith("qa-cooking") for i in e["ids"]])
r = lambda f, m: round(float(f[m].mean()), 4)
out["read2"]["titles_heldout"] = {"n": len(pb), "fp_v3b": r(pb >= THR, ck | ~ck), "fp_v3c": r(pc >= THR, ck | ~ck), "cook_v3b": r(pb >= THR, ck), "cook_v3c": r(pc >= THR, ck),
                                  "money_v3b": r(pb >= THR, ~ck), "money_v3c": r(pc >= THR, ~ck), "drop": round(1 - (pc >= THR).mean() / max((pb >= THR).mean(), 1e-9), 3)}
e = z("main97"); pb, pc = dlib.head_p(hb, e["vecs"]), dlib.head_p(hc, e["vecs"]); ids = [str(i) for i in e["ids"]]
cm = np.array([i.startswith("st-qa-") for i in ids])
out["read2"]["cm40"] = {"n": int(cm.sum()), "fires_v3b": [i for i, f, c in zip(ids, pb >= THR, cm) if f and c], "fires_v3c": [i for i, f, c in zip(ids, pc >= THR, cm) if f and c]}
out["main97"] = {"p_v3b": {i: round(float(p), 4) for i, p in zip(ids, pb)}, "p_v3c": {i: round(float(p), 4) for i, p in zip(ids, pc)},
                 "fire_flips": [(i, round(float(a), 3), round(float(b), 3)) for i, a, b in zip(ids, pb, pc) if (a >= THR) != (b >= THR)]}
e = z("probes65"); pb, pc = dlib.head_p(hb, e["vecs"]), dlib.head_p(hc, e["vecs"]); ids = [str(i) for i in e["ids"]]
out["read3"] = {"fires_v3b": int((pb >= THR).sum()), "fires_v3c": int((pc >= THR).sum()),
                "lost_fires": [(i, round(float(a), 3), round(float(b), 3)) for i, a, b in zip(ids, pb, pc) if a >= THR and b < THR],
                "new_fires": [(i, round(float(a), 3), round(float(b), 3)) for i, a, b in zip(ids, pb, pc) if a < THR and b >= THR],
                "p": {i: [round(float(a), 4), round(float(b), 4)] for i, a, b in zip(ids, pb, pc)}}
json.dump(out, open(sys.argv[2], "w"), indent=1)
s = {k: v for k, v in out.items() if k not in ("main97",)}; s["read3"] = {k: v for k, v in out["read3"].items() if k != "p"}
s["main_flips"] = out["main97"]["fire_flips"]; print(json.dumps(s, indent=None)[:3000])
