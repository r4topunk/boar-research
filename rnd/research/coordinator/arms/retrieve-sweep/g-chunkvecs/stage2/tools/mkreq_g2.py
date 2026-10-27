#!/usr/bin/env python3
"""Arm G stage 2 requests (0 LLM). python3 -I mkreq_g2.py <ctl|arm> <out>
Template = the QFORM secondary requests (arms/qform/gen/req/qform-gen-a.requests.jsonl first row: LITEPACKS K1 request shape, Qwen3-1.7B, seed 42, android 12 GB),
items = g-chunkvecs/q3.jsonl (216 QFORM items of factbook/firstaid/medlineplus; text from qform.jsonl). Differences vs the QFORM secondary, all in config:
kit = the three single packs sha-pinned (ctl = v2 persona-a-union files, arm = v3proto files with chunk_vecs); settings = {quickFirst, alwaysComplete:false} (ctl)
or + packDense2:true (arm) = the replay's settings in g-chunkvecs/{ctl3,dense2-true}.jsonl."""
import json, sys, hashlib
which, out = sys.argv[1:3]
B = "<workspace>"; ROOT = f"{B}/rnd/research/coordinator/arms"
tmpl = json.loads(open(f"{ROOT}/qform/gen/req/qform-gen-a.requests.jsonl").readline())
PACKS = ["boar-factbook", "boar-firstaid-en", "boar-medlineplus-en"]
d = {"ctl": f"{B}/shared-data/packs/persona-a-union", "arm": f"{B}/shared-data/packs/v3proto"}[which]
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 24), b""): h.update(c)
    return h.hexdigest()
kit = [{"id": p, "sha256": sha(f"{d}/{p}.sqlite")} for p in PACKS]
items = {}
for l in open(f"{ROOT}/qform/items/qform.jsonl"):
    x = json.loads(l); items[x["id"]] = x
ids = [json.loads(l)["id"] for l in open(f"{ROOT}/retrieve-sweep/g-chunkvecs/q3.jsonl") if l.strip()]
assert len(ids) == 216 and len(set(ids)) == 216
run = f"g2-{which}"
with open(out, "w") as fo:
    for i in ids:
        r = json.loads(json.dumps(tmpl)); r["runId"] = run
        r["item"] = {"id": i, "question": items[i]["question"], "lang": items[i]["lang"]}
        c = r["config"]; c["arm"] = "cut7-headpass-x2+litepacks+g2" + ("-dense2" if which == "arm" else "")
        c["kit"] = kit
        c["settings"] = {"quickFirst": True, "alwaysComplete": False, **({"packDense2": True} if which == "arm" else {})}
        fo.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"{len(ids)} requests -> {out}; kit {[(k['id'], k['sha256'][:12]) for k in kit]}; settings {c['settings']}")
