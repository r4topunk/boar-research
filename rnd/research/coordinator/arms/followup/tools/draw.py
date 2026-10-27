"""FOLLOWUP draw (0 LLM): seed 999 picks 20 of the 180 public self-tests, 2 per pack (9 packs) + 2 extra packs get a 3rd.
Usage: python3 -I draw.py > runs/draw.json"""
import json, random
ST = "<workspace>/rnd/research/packs/selftest"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se",
         "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
r = random.Random(999); extra = set(r.sample(PACKS, 2)); out = []
for p in PACKS:
    ids = [json.loads(l)["id"] for l in open(f"{ST}/{p}.jsonl") if l.strip()]
    order = ids[:]; r.shuffle(order)
    out.append({"pack": p, "n": 3 if p in extra else 2, "order": order})
print(json.dumps({"seed": 999, "extra": sorted(extra), "packs": out}, indent=1))
