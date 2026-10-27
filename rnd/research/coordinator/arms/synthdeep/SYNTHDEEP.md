# SYNTHDEEP step 0 — one pinned source per side of a comparison on the deep thinking tier (cmpsplit v2.1 ported to dt512): 0-call replay gate (2026-10-12; B7 gate as written in LOOP-PROGRAM §3: "both sides in the kept sources on ≥ 5 more comparison items")

**Verdict: FAIL at step 0 (closed; no judge call).** Curated kit (crypto + wikivoyage): both sides kept on 1 → 2 of the 7 two-sided v0.1 items (+1, bar +5); the kit has no article for at least one side on 5 items (nothing to pin). Labelled variant with the wiki-vital5 pack in the kit (encyclopedic sides available): both sides kept 2 → **5 (+3)**, gold gained on 3 items (lan-cmp-002, lan-cmp-005, vit-sci-002), gold lost 0 — still under the bar, and that variant inherits VITALADD's finding that the judge does not reward an added intro.

| kit | two-sided items (split fired) | both sides kept off → on | gold gained / lost | kept lists changed on vs off |
|---|---|---|---|---|
| curated (B7 as written) | 7 | 1 → 2 (vit-sci-002) | 1 / 0 | 2 |
| curated + wiki-vital5 (labelled) | 7 | 2 → 5 (+ lan-cmp-002, vit-sci-002, lan-cmp-005) | 3 / 0 | 4 |
Default-off byte-identical to dt512: 60/60 on the curated kit (vs the cut-7 base 54/60: FACTS items, not the patch).

Mechanism (port, `synthdeep.vs-dt512.patch` 41a37bc2…, tree 96e92a80…, default off, differential 9/9, tsc 0, vitest 591/593 + 249/249): side detection on the question ("A or B", "A vs B", "difference between", comparatives; never health), one retrieve per side (3 hits), the side's best passage gets one of the k = 6 slots and is pinned through compression and the topic filter; codes `cmpsplit:sides-N` / `pinned-A-B` / `off-topic-N`. Trigger = side detection, not route task (only 1/7 two-sided items routes as `compare`).
Reading: comparison items lose on *wrong* facts about the two sides (LOSSMAP: 4/7 primary wrong); the curated kit cannot supply the sides, and an encyclopedia intro supplies the article but not the rubric's fact (VITALADD). The B7 mechanism is closed at step 0 for this kit; it reopens only with a kit that holds the sides' specific facts.
Exposure: v0.1 public only; 0 judge calls; nothing on the mini.

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file; the gate was pre-stated in LOOP-PROGRAM §3 B7 — nothing to freeze (a sha now would fake a pre-registration).
