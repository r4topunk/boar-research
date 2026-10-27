#!/usr/bin/env python3
"""KEEP-E baseline (0 LLM): LITEPACKS K1 seed 42 answers + Haiku judgments (K0 rows reused for byte-identical answers, as routing-r1/analyze.py)
for the given ids; stage-1 (DECLINE2STAGE) labels looked up by answer text sha256 in ruler/decline2stage/out/stage1.jsonl.
Usage: baseline.py <ids...> -> stdout JSON"""
import json, glob, os, sys, hashlib
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); LP = H + "/../litepacks"; D2 = H + "/../../ruler/decline2stage/out/stage1.jsonl"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
def judg(files):
    by = {}
    for f in files:
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    m3 = lambda d: sum(d.values()) / 3
    return {q: dict(s=sum(m3(m["boar"]) for m in v.values()) / 2, sref=sum(m3(m["ref"]) for m in v.values()) / 2, corr=sum(m["boar"]["correctness"] for m in v.values()) / 2) for q, v in by.items() if len(v) == 2}
tr = lambda a: {t["itemId"]: t for f in glob.glob(f"{LP}/traces/lp-{a}-*-s42.traces.jsonl") if "-st-" not in f and "smoke" not in f for t in rd(f)}
T0, T1 = tr("K0"), tr("K1")
J0 = judg([f for f in glob.glob(f"{LP}/judgments/lp-K0-*.judgments.jsonl") if "-st-" not in f]); J1 = judg([f for f in glob.glob(f"{LP}/judgments/lp-K1-*.judgments.jsonl") if "-st-" not in f])
JB = {i: (J0.get(i) if T1[i]["answer"]["text"] == T0[i]["answer"]["text"] else J1.get(i)) for i in T1}
S1 = {}
for r in rd(D2):
    if r.get("ok"): S1.setdefault(r["textSha256"], set()).add(r["attempted"])
out = {"sref_main": sum(j["sref"] for j in JB.values() if j), "n_main_judged": sum(1 for j in JB.values() if j), "items": {}}
for i in sys.argv[1:]:
    t = T1[i]["answer"]["text"]; sh = hashlib.sha256(t.encode()).hexdigest()
    out["items"][i] = dict(text=t, sha=sh, src="K0" if t == T0[i]["answer"]["text"] else "K1", judged=JB[i], stage1=sorted(S1.get(sh, [])),
                           trace_file=[os.path.basename(f) for f in glob.glob(f"{LP}/traces/lp-K1-*-s42.traces.jsonl") if any(json.loads(l)["itemId"] == i for l in open(f))])
print(json.dumps(out, indent=1))
