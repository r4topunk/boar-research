#!/usr/bin/env python3
"""PIN2-SCREEN requests (0 LLM): 5 MAIN rows from sefix124-main-s42 + b15 b18 from t27-succinct-s42; only runId / config.arm change. -> req/screen-{base,pin2}-{main,t27}-s42.requests.jsonl"""
import json
A = "<workspace>/rnd/research/coordinator/arms"; D = A + "/coverage-map/pin2"
MAIN = ["vit-hum-002", "vit-cry-008", "lan-exp-005", "trv-004", "st-qa-cooking-se-004"]; T27 = ["b15", "b18"]
rows = [json.loads(l) for l in open(A + "/coverage-map/sefix/ans-req/sefix124-main-s42.requests.jsonl")]
rows = [r for i in MAIN for r in rows if r["item"]["id"] == i]
t = [json.loads(l) for l in open(A + "/topics27/in/t27-succinct-s42.requests.jsonl")]
rows += [r for i in T27 for r in t if r["item"]["id"] == i]
assert [r["item"]["id"] for r in rows] == MAIN + T27 and all(r["seed"] == 42 for r in rows)
for arm in ("base", "pin2"):   # one file per (arm, set): the adapter needs one runId/config per requests file
    for st, ids in (("main", MAIN), ("t27", T27)):
        out = []
        for r in rows:
            if r["item"]["id"] not in ids: continue
            r = json.loads(json.dumps(r)); r["runId"] = f"pin2screen-{arm}-{st}-s42"; r["config"]["arm"] = "cut7-headpass-x2+litepacks+" + ("sefix124" if arm == "base" else "sefix124+pin2"); out.append(json.dumps(r, ensure_ascii=False))
        open(f"{D}/req/screen-{arm}-{st}-s42.requests.jsonl", "w").write("\n".join(out) + "\n")
print(len(rows))
