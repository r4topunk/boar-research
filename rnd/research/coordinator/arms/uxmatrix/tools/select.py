#!/usr/bin/env python3
"""UXMATRIX item selection + OFF kits (0 LLM, outcome-blind). python3 -I select.py -> ../items.json
cm 40 = the st-qa-cooking-se-* / st-qa-money-se-* ids of lp-screens/main-97.ids; OFF kit = K13 minus qa-cooking-se / qa-money-se.
general-delivered 15 = random.Random(20261023).sample(sorted(D), 15), D = v0.1 keyed items with chunk-level delivery under SEFIX-124
  (coverage-map/sefix/chunklevel-124.json per_item['sefix F1F2F4'][i]['chunk']); OFF kit = K13 minus EVERY pack that has a kept chunk with share_v01 >= 0.5 (deliv_packs.json).
general-no-pack = v0.1 keyed items, not delivered, with no qualifying chunk in any K13 pack (coverage-pool.json, RAG-FUNNEL pool rule) and not moved into a pack by the
  COVERAGE-MAP hand reads (vit-cry-005 boar-crypto, lan-rsn-002 simplewiki, vit-sci-002 factbook-derivable are removed); ON = OFF (one generation per mode)."""
import json, random, collections
A = "<workspace>/rnd/research/coordinator/arms"; CM = A + "/coverage-map"
K13 = ["boar-crypto", "boar-wikivoyage-en", "boar-simplewiki-en", "qa-cooking-se", "qa-money-se", "boar-factbook", "boar-medlineplus-en", "boar-firstaid-en", "boar-visa-en", "qa-health-se", "qa-travel-se", "qa-outdoors-se", "wiki-vital5"]
ids = open(A + "/lp-screens/main-97.ids").read().split()
P = json.load(open(CM + "/aggregates/coverage-pool.json"))["items"]; CL = json.load(open(CM + "/sefix/chunklevel-124.json"))["per_item"]["sefix F1F2F4"]
DP = json.load(open(A + "/uxmatrix/deliv_packs.json"))
cm = [i for i in ids if i.startswith("st-")]; assert len(cm) == 40
D = sorted(i for i in DP); assert len(D) == 28
dl = sorted(random.Random(20261023).sample(D, 15))
HAND = {"vit-cry-005", "lan-rsn-002", "vit-sci-002"}
nop = sorted(i for i in P if P[i]["set"] == "v0.1" and CL[i] and not CL[i]["chunk"] and not any(P[i]["packs"].get(p, {}).get("n_qualifying", 0) > 0 for p in K13) and i not in HAND)
items = []
for i in cm: items.append(dict(id=i, cls="cm", off_minus=["qa-cooking-se" if "cooking" in i else "qa-money-se"]))
for i in dl: items.append(dict(id=i, cls="gen-delivered", off_minus=DP[i]["packs"]))
for i in nop: items.append(dict(id=i, cls="gen-nopack", off_minus=[]))
json.dump(dict(K13=K13, items=items), open(A + "/uxmatrix/items.json", "w"), indent=1)
print(len(items), collections.Counter(x["cls"] for x in items)); print("delivered", dl); print("nopack", nop)
print("OFF kit groups:", collections.Counter(",".join(x["off_minus"]) for x in items if x["off_minus"]))
