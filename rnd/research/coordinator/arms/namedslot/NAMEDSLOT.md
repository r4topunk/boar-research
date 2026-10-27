# NAMEDSLOT result (2026-10-06): NOT ADOPTED as frozen (G2 fails on breadth)

Criterion: NAMEDSLOT-criterion.md cfcb81e3… · build: wt/namedslot ec851327 (patch namedslot.vs-cut6.patch 27dc50ab…, vs 0cfd4a77 c5cd6a18…)
Measurement: retrieval-only replay on the MacBook (boar-eval/adapters/desktop-node/tools/replay-retrieval.ts, validated 60/60 identical raw lists vs ctl-v01-s44 on cut 6; 8 s per run). Files: boar-eval/runs/replay-cache/{cut6-v01-s44.compress,namedslot-v01-s44}.replay.jsonl.

| Gate | Bar | Result | |
|---|---|---|---|
| G1 build | tsc clean, vitest, +tests | tsc clean; 1313/1313 (+1 test; wikiPack.destination "Darwin" regression caught and fixed before freeze of the build) | PASS |
| G2a recall@5 (39 gold) | ≥ 0.41 | 0.333 → **0.4103** (+3: Japan/Germany, Kenya, Iceland) | PASS |
| G2b gold newly in raw on B2 items | ≥ 3 of 7 | 3 (vit-sci-002, lan-exp-003, lan-ref-004) | PASS |
| G2c items whose raw list changes | ≤ 12/60 | **15/60** | **FAIL** |
| G2d first raw title unchanged | all | 15/15 unchanged | PASS |
| G3/G4 | — | not run (G2 failed; no judge spent) | — |

Changed items (added → removed): vit-hum-006 +Liberty · lan-rsn-001 +Moon −Wenzhou · lan-ref-001 +Literary travel −Lübeck · lan-hlt-003 +Infectious diseases −Africa · vit-cry-001 +Quantum computing, Ethereum −EIP-8202 · vit-cry-010 +Ethereum −DAO · vit-sci-002 +Japan, Germany −Pacific War (gold) · vit-hlt-001 +Jellyfish, Thailand −Langkawi, Darwin · vit-hlt-002 +Andes · lan-ref-004 +Iceland −European quick reference (gold) · lan-exp-003 +Kenya −Nairobi (gold) · lan-cmp-004 +Malé, United States · lan-cmp-005 +Nile −Costa Rica · lan-rsn-005 +Destinations · dng-005 +Water.

Reading: the rule reaches the three target items exactly as predicted, but it also fires on generic words that resolve to guides ("Liberty" for On Liberty, "Moon", "Water", "Destinations", and **"Malé" from the lowercase word "male"** in moose-vs-bison: resolveTitle is accent-insensitive on lowercase single words). 12 of the 15 changes are such side slots; they replace noise with other noise (Lübeck → Literary travel) and never the first title, so quality harm is unlikely, but the frozen breadth bar was 12 and the result is 15. Per the stop rule: closed, no rescue, no threshold tuning.
Expected value if it had passed: ratio Δ ≈ 0 (Kenya and Iceland already scored 5/5 from memory; Japan/Germany 3/5 is the "4B misreads numbers in context" item from rv2). The arm was a correctness fix, not a bar mover; the judge was not spent.
Kept: the replay harness (the reusable asset), the scorecard tool, and two upstream notes for the PR phase: (1) lowercase "male" → "Malé" in resolveTitle; (2) a question-named article below NAMED_MIN_SHARE loses to generic-word guides (Kenya → Angola/Mexico/Bangladesh).
A narrower variant (capitalised names only, no accent-folded lowercase matches) would be a NEW pre-registration, not a rescue, and is not worth a judge run on the 4B.
