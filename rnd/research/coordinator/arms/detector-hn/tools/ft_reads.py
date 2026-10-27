#!/usr/bin/env python3
"""DETECTOR-FT reads 1-3 at the shipped threshold 0.2 (0 LLM): v3b = v3b head on v3b-GGUF vectors (work/emb.*), candidate = its head on
ITS GGUF vectors (work/<tag>/emb.*). Same tables as reads.py (DETECTOR-HN) + writes work/<tag>/tasks.jsonl (K3 traces with the candidate's
detector codes, mk_tasks.py logic) for the MAIN 97 replay. usage: ft_reads.py <tag> <head.json> <out.json>"""
import json, sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); import dlib
A = "<workspace>/rnd/research/coordinator/arms/"; W = A + "detector-hn/work/"; THR = 0.2
tag, hp, outp = sys.argv[1:4]; W2 = W + tag + "/"
hb, hc = dlib.load_head(dlib.HEAD_V3B), dlib.load_head(hp)
def P(s):
    a, b = np.load(W + f"emb.{s}.npz"), np.load(W2 + f"emb.{s}.npz"); assert (a["ids"] == b["ids"]).all()
    return a, dlib.head_p(hb, a["vecs"]), dlib.head_p(hc, b["vecs"])
out = {"tag": tag, "head": hp, "thr": THR, "read1": {}, "read2": {}}
for s in ("compass300", "sonar903", "terse30", "ptmirror28", "v3b_val"):
    e, pb, pc = P(s); y = e["labels"]; fb, fc = pb >= THR, pc >= THR; pos = y == 1; neg = y == 0
    out["read1"][s] = {"pos": int(pos.sum()), "recall_v3b": int((fb & pos).sum()), "recall_new": int((fc & pos).sum()),
                       "lost_pos": [str(i) for i in e["ids"][fb & ~fc & pos]], "gained_pos": [str(i) for i in e["ids"][~fb & fc & pos]],
                       "neg": int(neg.sum()), "fp_v3b": int((fb & neg).sum()), "fp_new": int((fc & neg).sum())}
e, pb, pc = P("titles_heldout"); ck = np.array([str(i).startswith("qa-cooking") for i in e["ids"]]); r = lambda f, m: round(float(f[m].mean()), 4)
out["read2"]["titles_heldout"] = {"n": len(pb), "fp_v3b": r(pb >= THR, ck | ~ck), "fp_new": r(pc >= THR, ck | ~ck), "cook_v3b": r(pb >= THR, ck), "cook_new": r(pc >= THR, ck),
                                  "money_v3b": r(pb >= THR, ~ck), "money_new": r(pc >= THR, ~ck)}
e, pb, pc = P("titles_train"); out["read2"]["titles_train"] = {"fp_v3b": round(float((pb >= THR).mean()), 4), "fp_new": round(float((pc >= THR).mean()), 4)}
e, pb, pc = P("main97"); ids = [str(i) for i in e["ids"]]; cm = np.array([i.startswith("st-qa-") for i in ids])
out["read2"]["cm40"] = {"n": int(cm.sum()), "fires_v3b": [i for i, f, c in zip(ids, pb >= THR, cm) if f and c], "fires_new": [i for i, f, c in zip(ids, pc >= THR, cm) if f and c]}
out["main97"] = {"p_v3b": {i: round(float(p), 4) for i, p in zip(ids, pb)}, "p_new": {i: round(float(p), 4) for i, p in zip(ids, pc)},
                 "fire_flips": [(i, round(float(a), 3), round(float(b), 3)) for i, a, b in zip(ids, pb, pc) if (a >= THR) != (b >= THR)]}
pm = dict(zip(ids, pc)); n = ch = 0
with open(W2 + "tasks.jsonl", "w") as f:
    for l in open(A + "coverage-map/replay/funnel-K3.traces.jsonl"):
        t = json.loads(l); rc = t["route"]["reasonCodes"]
        if any(c.startswith("detector:p=") for c in rc):
            q = float(pm[t["itemId"]]); new = []
            for c in rc:
                if c == "detector:fire": continue
                new.append(f"detector:p={q:.3f}" if c.startswith("detector:p=") else c)
                if c.startswith("detector:p=") and q >= THR: new.append("detector:fire")
            ch += new != rc; t["route"]["reasonCodes"] = new; n += 1
        f.write(json.dumps(t, ensure_ascii=False) + "\n")
out["main97"]["tasks"] = {"detector_items": n, "codes_changed": ch}
e, pb, pc = P("probes65"); ids = [str(i) for i in e["ids"]]
out["read3"] = {"fires_v3b": int((pb >= THR).sum()), "fires_new": int((pc >= THR).sum()),
                "lost_fires": [(i, round(float(a), 3), round(float(b), 3)) for i, a, b in zip(ids, pb, pc) if a >= THR and b < THR],
                "new_fires": [(i, round(float(a), 3), round(float(b), 3)) for i, a, b in zip(ids, pb, pc) if a < THR and b >= THR],
                "p": {i: [round(float(a), 4), round(float(b), 4)] for i, a, b in zip(ids, pb, pc)}}
json.dump(out, open(outp, "w"), indent=1)
s = {k: v for k, v in out.items() if k != "main97"}; s["read3"] = {k: v for k, v in out["read3"].items() if k != "p"}
s["main_flips"] = out["main97"]["fire_flips"]; s["tasks"] = out["main97"]["tasks"]; print(json.dumps(s)[:4000])
