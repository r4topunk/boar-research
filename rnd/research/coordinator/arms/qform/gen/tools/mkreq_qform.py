#!/usr/bin/env python3
"""QFORM secondary requests (0 LLM). python3 -I mkreq_qform.py <ids file|-> <runId> <out> [--k1]
Template = the LITEPACKS K1 request (as lp-screens/tools/mkreq.py: Qwen3-1.7B, seed 42, same device/model fields). Differences, all in config:
kit = the A-union merged file as ONE entry (id boar-aunion-merged, sha256 7e86674b...), settings = the replay's stock settings {quickFirst, alwaysComplete:false}
(no packHeadPass / packDense2) so retrieval reproduces replay/qform.replay.jsonl; --k1 keeps the K1 head pass + dense append (matches qform.replay.k1settings.jsonl)."""
import json, sys, hashlib
ids_f, run, out = sys.argv[1:4]
K1 = "--k1" in sys.argv
ROOT = "<workspace>/rnd/research/coordinator/arms"
tmpl = json.loads(open(f"{ROOT}/litepacks/runs/req/lp-K1-cm-s42.requests.jsonl").readline())
h = hashlib.sha256()
with open("<workspace>/shared-data/packs/persona-a-union-merged/boar-aunion-merged.sqlite", "rb") as f:
    for c in iter(lambda: f.read(1 << 24), b""): h.update(c)
SHA = h.hexdigest()
items = {}
for l in open(f"{ROOT}/qform/items/qform.jsonl"):
    d = json.loads(l); items[d["id"]] = d
ids = [x for x in open(ids_f).read().split() if x]
miss = [i for i in ids if i not in items]
if miss: sys.exit(f"unknown ids {miss}")
with open(out, "w") as fo:
    for i in ids:
        r = json.loads(json.dumps(tmpl)); r["runId"] = run
        r["item"] = {"id": i, "question": items[i]["question"], "lang": items[i]["lang"]}
        c = r["config"]; c["arm"] = "cut7-headpass-x2+litepacks+qform"
        c["kit"] = [{"id": "boar-aunion-merged", "sha256": SHA}]
        if not K1: c["settings"] = {"quickFirst": True, "alwaysComplete": False}
        fo.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"{len(ids)} requests -> {out} (kit sha {SHA[:12]}, {'K1' if K1 else 'stock'} settings)")
