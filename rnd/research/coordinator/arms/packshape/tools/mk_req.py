#!/usr/bin/env python3
"""PACKSHAPE stage 2 requests: the 20 factbook lines of packproof on-k13 requests, runId pshape-on-k13s-s42, kit boar-factbook sha -> shaped."""
import json, hashlib
P = "<workspace>/rnd/research/coordinator/arms/"; SH = "<workspace>/kiln-local/shape-packs/shaped/boar-factbook.sqlite"
sha = hashlib.sha256(open(SH, "rb").read()).hexdigest(); n = 0
with open(P + "packshape/in/on-k13s.requests.jsonl", "w") as f:
    for l in open(P + "packproof/in/on-k13.requests.jsonl"):
        r = json.loads(l)
        if "factbook" not in r["item"]["id"]: continue
        r["runId"] = "pshape-on-k13s-s42"; r["config"]["arm"] += "+packshape"
        for k in r["config"]["kit"]:
            if k["id"] == "boar-factbook": k["sha256"] = sha
        f.write(json.dumps(r) + "\n"); n += 1
print(n, sha)
