#!/usr/bin/env python3
"""RD2 stage-0 sanity vs F1b (0 LLM): rows, empty, loops, deterministic items identical, kept identical, text/rc differences. python3 -I sanity_rd2.py RUN"""
import json, sys, collections
CM = "<workspace>/rnd/research/coordinator/arms/coverage-map"; ids = open(CM + "/../lp-screens/main-97.ids").read().split()
ld = lambda p: {json.loads(l)["itemId"]: json.loads(l) for l in open(p)}
T = ld(f"{CM}/reader/traces/{sys.argv[1]}.traces.jsonl"); F = ld(CM + "/sefix/ans-traces/f1b-main-s42.traces.jsonl")
def loop(txt):
    w = txt.split(); c = collections.Counter(tuple(w[i:i+6]) for i in range(len(w) - 5)); return any(v >= 3 for v in c.values())
det = lambda t: (t["timing"].get("outputTokens") or 0) == 0 or not any(r.startswith("generate:user-model") for r in t["route"]["reasonCodes"])
dets = [i for i in ids if det(F[i])]
kept = lambda t: [(c["title"], c.get("section"), c.get("source")) for c in t["retrieval"]["kept"]]
r = dict(run=sys.argv[1], rows=len(T), expected=len(ids), missing=[i for i in ids if i not in T], errors=[i for i in T if T[i].get("error")],
         empty=[i for i in T if not (T[i]["answer"]["text"] or "").strip()], loops=[i for i in T if loop(T[i]["answer"]["text"] or "")],
         det_items=len(dets), det_text_identical=sum(T[i]["answer"]["text"] == F[i]["answer"]["text"] for i in dets),
         kept_identical=sum(kept(T[i]) == kept(F[i]) for i in ids),
         text_identical=sum(T[i]["answer"]["text"] == F[i]["answer"]["text"] for i in ids),
         rc_differs=[i for i in ids if T[i]["route"]["reasonCodes"] != F[i]["route"]["reasonCodes"]],
         text_differs=[i for i in ids if T[i]["answer"]["text"] != F[i]["answer"]["text"]],
         rc_diff_without_grounded=[i for i in ids if [x for x in T[i]["route"]["reasonCodes"] if not x.startswith("citations:grounded")] != [x for x in F[i]["route"]["reasonCodes"]] and T[i]["answer"]["text"] != F[i]["answer"]["text"] and False])
r["only_grounded_changes"] = all(any(x.startswith("citations:grounded") for x in T[i]["route"]["reasonCodes"]) for i in r["text_differs"])
json.dump(r, open(f"{CM}/reader/sanity.{sys.argv[1]}.json", "w"), indent=1); print(json.dumps(r, indent=1))
