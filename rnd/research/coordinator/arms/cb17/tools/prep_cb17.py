#!/usr/bin/env python3
"""CB17 prep (0 calls). python3 -I prep_cb17.py
-> in/opus.ids: CV5 51 ids whose closed-book (id, text) unit has no existing Opus judge.v1 row on the v0.1 frame (cv5_opus_pool), in/opus.reuse.json;
-> in/stage1.units.jsonl: the 97 closed-book (question, answer) units for DECLINE2STAGE stage 1."""
import json, sys, hashlib
R = "<workspace>/rnd/research/coordinator"; H = R + "/arms/cb17"
sys.path.insert(0, R + "/ruler/tools"); import cv5_opus_pool as CP
T = {(j := json.loads(l))["itemId"]: j for l in open(H + "/traces/cb17-main-s42.traces.jsonl")}
Q = {(j := json.loads(l))["item"]["id"]: j["item"]["question"] for l in open(H + "/runs/req/cb17-main-s42.requests.jsonl")}
assert len(T) == 97 and not [i for i, t in T.items() if t.get("error")]
ids = json.load(open(R + "/ruler/cv5-ladder/in/set.json"))["ids"]; assert len(ids) == 51
P = CP.pool("bd235bb9811f6d1ae88ba2d2ae3973e3572d75b6c451ee4cdd3a2e7644db48b1", "568b3ececd8afe5cad63a7f39bffe414e6dd45bcef9d03ef112faecad2981b18", exclude_prefix=H)
reuse = {q: P[CP.key(q, T[q]["answer"]["text"])]["src"] for q in ids if CP.key(q, T[q]["answer"]["text"]) in P}
open(H + "/in/opus.ids", "w").write("".join(q + "\n" for q in ids if q not in reuse))
json.dump(reuse, open(H + "/in/opus.reuse.json", "w"), indent=1)
with open(H + "/in/stage1.units.jsonl", "w") as f:
    for q, t in T.items():
        tx = t["answer"]["text"]; sh = hashlib.sha256(tx.encode()).hexdigest()
        f.write(json.dumps({"key": f"{q}|{sh}", "set": "MAIN", "id": q, "question": Q[q], "text": tx, "text_sha256": sh}, ensure_ascii=False) + "\n")
print(f"opus new {51 - len(reuse)} reuse {len(reuse)}; stage1 units {len(T)}")
