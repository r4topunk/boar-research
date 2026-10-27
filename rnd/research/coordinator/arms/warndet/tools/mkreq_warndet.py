"""WARN-DET replay requests: v0.2 110 (blind, script-only) on the WARNSPEC v0.1 request template (claim kit, seed, settings unchanged).
Writes to a scratch path outside git (the requests hold question text). Prints counts only. Usage: python3 -I mkreq_warndet.py <out.jsonl>"""
import json, sys, copy
ROOT = "<workspace>"
tpl = json.loads(open(f"{ROOT}/rnd/research/coordinator/arms/warnspec/runs/warn-replay-v01.pr1+warn.requests.jsonl").readline())
Q = [json.loads(l) for l in open(f"{ROOT}/blind/bench-v02/live/v0.2/questions.v02-new.jsonl") if l.strip()]
with open(sys.argv[1], "w") as o:
    for q in Q:
        r = copy.deepcopy(tpl); r["runId"] = "warndet-v02"; r["item"] = {"id": q["id"], "question": q["question"], "lang": q["lang"]}
        o.write(json.dumps(r, ensure_ascii=False) + "\n")
print("requests", len(Q), "kit", [k["id"] for k in tpl["config"]["kit"]], "arm", tpl["config"]["arm"], "seed", tpl["seed"])
