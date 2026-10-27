# FACTS r6 on blind set 4 (2026-10-06 23:54): FAIL by the frozen criterion (recall 70 % < 75 %). Set 4 burnt. FACTS line CLOSED.
Code wt/facts 98db9827 (patch facts-r6.vs-cut6.patch 0eee6a0b…, asset 92d64c02…, 4,233 entities, 761 KB), criterion
FACTS-r6-criterion.md 60027d01…, set recall-set-4.jsonl d2ea2b5c… (sha verified before), scorer v2, one run: recall-set4-r6.*.
| metric | r6 on set 4 | bar | r5 on set 3 (for scale) |
|---|---|---|---|
| fact fired | 29/40 | — | 27/40 |
| recall | **28/40 = 70.0 %** | PASS ≥ 85, PARTIAL ≥ 75 | 24/40 = 60 % |
| precision | **28/29 = 96.6 %** | ≥ 90 | 88.9 % |
| false positives (20 near-misses) | **0/20** | 0 | 0/20 |
| lowercase-typed correct | 11/20 | — | 10/19 |
Gates before the run (FACTS-r6.md): G1 1346/1346; 13 probes 0 identical; r4 fresh 1/22; nearmiss-lc FP 0/40; G2 7/8 identical;
G3 0/52 0/12 0/11 2/192 identical to r5 (275/275); G4 52/52; G5 p95 0.082 ms, cold load 107 ms; data review seed 46 4/60 →
2 build gates → seed 47 1/60 (a third gate added after that sample, not re-sampled); **nearmiss-lc2 (blind, a4428c78…) FP 0/40**.
Dev sets r5 → r6: set 1 33 → 34, set 2 31 → 32, set 3 24 → 29 (of 40).
Miss classification (12), deterministic against the r6 asset:
- lowercase ONE-WORD non-country/non-capital names, blocked by the r3 rule on purpose (precision trade): houston, bangalore,
  osaka, aconcagua, kangchenjunga, yangtze, ganges, zambezi/orange → **8**. 7 of the 8 entities are in the table (Zambezi is absent; corrected by LCRELAX-PROBE).
- "turkey" on the risk list (+ opener typo) → 1. "Bogota" typed without the accent (label Bogotá; fold not applied on the label
  side, or "altitude" missing from the lexicon) → 1. Denali absent (no English label in the cached fetch) → 1.
  Caspian Sea area 386,400 vs the set's 371,000 km² (+4 %, data disagreement) → 1.
Reading: coverage is no longer the cause (11/12 missed entities are in the table). The binding constraint is the deliberate
rule "lowercase one-word names resolve only for countries and capitals", which is what keeps false positives at 0/100 across
the three adversarial blind sets (nearmiss-lc, nearmiss-lc2, set 3/4 near-misses). Relaxing it per entity kind is possible but
is a new precision/recall trade that needs its own blind sets; per the criterion there is no r7.
HEAD DECISION (coordinator): the criterion said "close at r5 on FAIL". r6 dominates r5 on every frozen measure (dev sets, set 3,
precision, FP, gates) and adds data gates; keeping r6 as the FACTS head is not a rescue of the verdict (FAIL stands for cut-7
purposes). The line's blind-tested state is: precision ≈ 90–97 %, FP 0/100 adversarial, recall 60–70 % on fresh phrasing,
75–85 % on capitalised typing. v0.1 effect unchanged since r2: 8 fires, +0.94 rubric/item, projected +0.027 (judged once).
UNKNOWN: recall on real user typing (our sets over-weight lowercase and typos on purpose); whether the r6 asset's 3,200 new
entities carry wrong values beyond the 2 × 60 sampled rows (1/60 after gates).
