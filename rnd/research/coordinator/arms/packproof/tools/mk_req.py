#!/usr/bin/env python3
"""PACKPROOF requests (0 LLM). python3 -I mk_req.py -> ../in/<group>.requests.jsonl + ../in/items.json
Template config = coverage-map/sefix/ans-req/sefix124-main-s42.requests.jsonl (SEFIX-124 K13 kit, settings quickFirst/packHeadPass a2/packDense2 append-budget, seed 42, persona = adapter default succinct).
Items = the 9 packs' public self-tests (rnd/research/packs/selftest/<pack>.jsonl, 20 each = 180).
Packs in K13 (7): ON = K13, OFF = K13 minus the pack. Packs not in K13 (qa-ethereum-se, qa-bitcoin-se): ON = K13 + the pack (v3proto build), OFF = K13."""
import json, os, collections
A = "<workspace>/rnd/research/coordinator/arms"; P = A + "/packproof"; ST = "<workspace>/rnd/research/packs/selftest/"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
EXTRA = {"qa-ethereum-se": "c58d44ebfe621d3bb23b284577a406e54a53c0ab0daa4241ae966f30ad4d749d", "qa-bitcoin-se": "012e0053b230ad04e94aeb89f21163f343dee954b01fb446f7073516272b8b23"}
T = json.loads(open(A + "/coverage-map/sefix/ans-req/sefix124-main-s42.requests.jsonl").readline())
K13 = T["config"]["kit"]; ids13 = [k["id"] for k in K13]; assert len(K13) == 13
G = collections.defaultdict(list); items = []
for p in PACKS:
    rows = [json.loads(l) for l in open(ST + p + ".jsonl") if l.strip()]; assert len(rows) == 20
    for x in rows:
        items.append(dict(id=x["id"], pack=p, in_k13=p in ids13))
        if p in ids13: on, off, gon, goff = K13, [k for k in K13 if k["id"] != p], "on-k13", "off-" + p
        else: on, off, gon, goff = K13 + [dict(id=p, sha256=EXTRA[p])], K13, "on-k13+" + p, "off-k13"
        for g, kit in ((gon, on), (goff, off)):
            r = json.loads(json.dumps(T)); r["item"] = dict(id=x["id"], question=x["question"], lang="en"); r["config"]["kit"] = kit
            r["runId"] = f"pp-{g}-s42"; r["config"]["arm"] = "cut7-headpass-x2+litepacks+sefix124+packproof"; G[g].append(r)
for g, rs in G.items():
    open(f"{P}/in/{g}.requests.jsonl", "w").write("\n".join(json.dumps(r, ensure_ascii=False) for r in rs) + "\n")
json.dump(dict(packs=PACKS, items=items), open(P + "/in/items.json", "w"), indent=0)
print({g: len(v) for g, v in G.items()}, sum(len(v) for v in G.values()))
