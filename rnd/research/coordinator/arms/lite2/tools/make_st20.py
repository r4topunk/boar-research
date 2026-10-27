#!/usr/bin/env python3
"""LITE2 selftest20: 20 ids by seeded random (random.Random(42)) over the 180 public self-test items of SELFTEST-SCORES
(9 packs x 20: qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en;
the wave-3 packs qa-cooking-se / qa-money-se are not in the 180). Stratified: 2 per pack (packs in sorted order, rng.sample over the sorted ids) = 18,
then 2 more drawn with rng.sample from the remaining 162 sorted ids (9 packs cannot give 20 at exactly 2 each). Output sorted ids, one per line."""
import json, random, sys
B = "<workspace>/boar-eval/bench/selftest"
PACKS = sorted("qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en".split())
rng = random.Random(42); pick = []; allids = []
for p in PACKS:
    ids = sorted(json.loads(l)["id"] for l in open(f"{B}/{p}/questions.jsonl") if l.strip()); assert len(ids) == 20, p
    allids += ids; pick += rng.sample(ids, 2)
assert len(allids) == 180
rest = sorted(set(allids) - set(pick)); pick += rng.sample(rest, 2)
out = sys.argv[1] if len(sys.argv) > 1 else "selftest20.ids"
open(out, "w").write("".join(i + "\n" for i in sorted(pick)))
print(len(pick), "ids;", {p: sum(i.startswith("st-" + p + "-") for i in pick) for p in PACKS})
