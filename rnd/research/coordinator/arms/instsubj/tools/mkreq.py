#!/usr/bin/env python3
"""mkreq.py <arm> <outdir>: stub-replay request files for cut 4 L0.
A.jsonl = v0.1 EN 60 + V-exact 11 (cryptosel/travelsel requests71) + the France warm-up + the 40 lookup-set items.
D.jsonl = Sonar's 1,328 EN dev messages (aligned-en 1010 + terse-live EN 213 + emergency-dev EN 105), last user turn only."""
import json, sys, copy
B = "<workspace>"; R = B + "/rnd/research"
arm, out = sys.argv[1], sys.argv[2]
base = [json.loads(l) for l in open(R + "/coordinator/arms/travelsel/tools/requests71.jsonl")]
tpl = base[0]
def req(i, q, run):
    r = copy.deepcopy(tpl); r["runId"] = run; r["config"]["arm"] = arm
    r["item"] = {"id": i, "question": q, "lang": "en"}; return r
A = []
for r in base:
    r = copy.deepcopy(r); r["config"]["arm"] = arm; r["runId"] = "c4a"; A.append(r)
A.append(req("warmup-france", "What is the capital of France?", "c4a"))
for l in []:  # lookup sets are never opened here
    d = json.loads(l); A.append(req(d["id"], d["question"], "c4a"))
jl = lambda p: [json.loads(l) for l in open(p) if l.strip()]
def last(d):
    t = d["turns"][-1]
    return t if isinstance(t, str) else [x for x in d["turns"] if x["role"] == "user"][-1]["text"]
E = R + "/sonar/exp/30-learned-detector/data/"
qs = [last(d) for d in jl(E + "aligned-en.jsonl")] + [last(d) for d in jl(E + "terse-live.jsonl") if d.get("lang") == "en"] + [last(d) for d in jl(R + "/compass/exp/emergency-dev/dev.jsonl") if d.get("lang", "en") == "en"]
D = [req("dev-%04d" % i, q, "c4d") for i, q in enumerate(qs)]
for name, rows in (("A", A), ("D", D)):
    with open(f"{out}/{name}.{arm}.requests.jsonl", "w") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(arm, len(A), len(D))
