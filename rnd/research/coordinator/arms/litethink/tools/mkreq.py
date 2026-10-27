#!/usr/bin/env python3
"""LITETHINK requests (0 LLM): per budget B in {256,512} and pack, the LITE5-180 ON rows (1.7B + X2b) on the selftest20 ids with only runId changed
(litethink-t<B>-st20-<pack>-s42). Asserts every other field equals the LITE5-180 ON request. Also writes the 3-item smoke files per budget."""
import json, os
A = "<workspace>/rnd/research/coordinator/arms"; H = f"{A}/litethink"; R5 = f"{A}/lite5/runs/180"
ids = [l.strip() for l in open(f"{A}/lite2/selftest20.ids") if l.strip()]; assert len(ids) == 20
PACKS = ["boar-factbook", "boar-firstaid-en", "boar-medlineplus-en", "boar-simplewiki-en", "qa-bitcoin-se", "qa-ethereum-se", "qa-health-se", "qa-outdoors-se", "qa-travel-se"]
SMOKE = ["st-qa-travel-se-001", "st-boar-factbook-001", "st-qa-ethereum-se-002"]
rows = {}
for p in PACKS:
    for l in open(f"{R5}/lite5-180-on-{p}-s42.requests.jsonl"):
        r = json.loads(l)
        if r["item"]["id"] in ids: rows[r["item"]["id"]] = (p, r)
assert len(rows) == 20
os.makedirs(f"{H}/runs/smoke", exist_ok=True)
for B in (256, 512):
    for p in PACKS:
        out = []
        for q in ids:
            pp, r = rows[q]
            if pp != p: continue
            n = dict(r); n["runId"] = f"litethink-t{B}-st20-{p}-s42"
            assert {k: v for k, v in n.items() if k != "runId"} == {k: v for k, v in r.items() if k != "runId"}
            out.append(n)
        assert out, p
        open(f"{H}/runs/litethink-t{B}-st20-{p}-s42.requests.jsonl", "w").write("".join(json.dumps(x) + "\n" for x in out))
    sm = []
    for q in SMOKE:
        n = dict(rows[q][1]); n["runId"] = f"litethink-t{B}-smoke-s42"; sm.append(n)
    open(f"{H}/runs/smoke/litethink-t{B}-smoke-s42.requests.jsonl", "w").write("".join(json.dumps(x) + "\n" for x in sm))
print("ok", {p: sum(1 for q in ids if rows[q][0] == p) for p in PACKS})
