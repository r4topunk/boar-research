#!/usr/bin/env python3
"""ORACLE-REAL inputs (0 LLM): items = gold-labels.tsv Y/P items whose LITEPACKS K3 MacBook trace reaches the 1.7B (route has generate:, i.e.
not answered by a deterministic layer); oracle file {itemId: {question, pack, chunk_id}}; requests = the LITEPACKS K3 v0.1 requests of those ids
with runId/arm renamed. Usage: build_inputs.py <out dir>"""
import json, sys, hashlib
A = "<workspace>/rnd/research/coordinator/arms/"; O = sys.argv[1]
lab = {}
for l in open(A + "oracle-real/gold-labels.tsv"):
    f = l.rstrip("\n").split("\t")
    if l.startswith("#") or f[0] == "item" or len(f) < 4: continue
    if f[2] in ("Y", "P"): lab[f[0]] = dict(chunk=f[1], label=f[2], source=f[3])
tr = {json.loads(l)["itemId"]: json.loads(l) for l in open(A + "litepacks/traces/lp-K3-v01-s42.traces.jsonl")}
llm = [i for i in sorted(lab) if any(c.startswith("generate:") for c in tr[i]["route"]["reasonCodes"])]
det = [i for i in sorted(lab) if i not in llm]
req = {json.loads(l)["item"]["id"]: json.loads(l) for l in open(A + "litepacks/runs/req/lp-K3-v01-s42.requests.jsonl")}
orc = {}
with open(f"{O}/runs/req/oracle-K3-v01gold-s42.requests.jsonl", "w") as w:
    for i in llm:
        r = req[i]; r["runId"] = "oracle-K3-v01gold-s42"; r["config"]["arm"] = "cut7-headpass-x2+litepacks+oracle-real"; w.write(json.dumps(r) + "\n")
        _, pk, cid = lab[i]["chunk"].split(":"); orc[i] = dict(question=r["item"]["question"], pack=pk, chunk_id=int(cid))
open(f"{O}/tools/oracle-file.json", "w").write(json.dumps(orc, indent=1) + "\n")
open(f"{O}/items.ids", "w").write("".join(i + "\n" for i in llm))
print(f"items {len(llm)} (Y {sum(lab[i]['label']=='Y' for i in llm)}, P {sum(lab[i]['label']=='P' for i in llm)}, manual {sum(lab[i]['source']=='manual' for i in llm)}); excluded deterministic {len(det)}: {' '.join(det)}")
