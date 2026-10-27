# FACTS r5 on blind set 3 (2026-10-06 22:56): FAIL by the frozen criterion (recall 60 % < 75 %). Set 3 is burnt (dev now).
Code wt/facts 802c28bb (patch facts-r5.vs-cut6.patch 9c86bf3f…), criterion FACTS-r5-criterion.md 54ab7a1b…, set recall-set-3.jsonl
e59e99f0… (sha verified before the run), scorer v2, one run by the coordinator: recall-set3-r5.jsonl / .out.txt.
| metric | r5 on set 3 | bar |
|---|---|---|
| fact fired | 27/40 | — |
| recall | **24/40 = 60.0 %** | PASS ≥ 85 %, PARTIAL ≥ 75 % |
| precision | 24/27 = 88.9 % | ≥ 90 % |
| false positives (20 near-misses) | **0/20** | 0 |
| lowercase-typed correct | 10/19 | — |
Gates before the run (FACTS-r5.md): G1 tsc 0 / vitest 1341; G2 7/8 identical to r3; G3 0/52, 0/12, 0/11, 2/192 same; G4 52/52 vs
cut 6, 60/60 vs r3; G5 p95 0.085 ms; r4 fresh probes 1/22 (the real entity only); adversarial lowercase near-miss set
nearmiss-lc.jsonl (517de417…, 40 items, blind) **FP 0/40**. Dev sets: set 1 33/40, set 2 31/40.
Miss classification (deterministic, entity presence checked in src/rag/facts.v1.json):
- entity ABSENT from the table (8): Matterhorn, Denver, The Shard, Hoover Dam, Rhine, Thames, Loire + Seine, Chrysler Building.
- trigger/template (5): "whta is" (function-word typo), "official language of iran" (opener without "what"), "what continent is
  nairobi on", "what country surrounds lesotho" (borders phrasing), "Which is taller, K2 or Everest?" (both present; no
  compare_elevation for "taller").
- value disagrees with the set's expect (3): Berlin 3.7 M (2025) vs 3.9 M; Seoul 9.7 M dated 2020 vs 9.4 M; Mekong 4,350 km vs
  4,900 km (sources differ 4,350–4,909).
Reading: precision is solved (0/60 adversarial fires across two blind sets, 88.9–100 % precision). Recall is now bounded by
TABLE COVERAGE (8/16 misses), then by 5 trigger gaps; trigger fixes alone reach at most 29/40 = 72.5 %. The next lever is the
asset (entity coverage), a data round with its own blind set, not a trigger round.
