# FACT-AVAIL (2026-10-21): the answer is in the A-union packs for 19 of 71 headline items (15 strict); for 27 (33 strict) no pack holds any key point

Criterion FACT-AVAIL-criterion.md (sha b9527555, rnd c32e08ef, before any call) + addendum 1 (sha b8fcadae, before its calls). Spec RULER-SPEC-v1-r4 (sha be8d7554) frozen before the counts were read. Labels file out/factavail-items.json **sha 7e0b9345f1c7110b37f7ac16df87d6649fcc6da5db82720f7a1efd0840c26d8e** (QUARANTINED, spec r4 §2.4 H2: coordinator-only, not in git; sha in out/factavail-items.sha256).
Cost: 329 Haiku 5.5-low + 108 Opus (40 validation + 68 strict) labelling calls; 0 generation; 0 app answers; 0 paid.

| stratum (H = 71 headline items) | primary (Haiku, validated) | strict (Haiku and Opus agree) |
|---|---|---|
| AVAILABLE (>= half the key points stated in a pack passage) | 19 | 15 |
| PARTIAL | 25 | 23 |
| NONE | 27 | 33 |
All 75: primary 21 / 25 / 29, strict 17 / 23 / 35. By family (primary, all 75): place 7/6/2, tech 6/6/3, science 5/3/5, travel 2/8/6, humanities 1/2/13. Supporting points by pack: wikivoyage 37, crypto 27, factbook 10, firstaid 8, medlineplus 6 (visa 0). Key points stated: 88 of 329 (27 %).

- Validation: Haiku vs Opus 34/40 (bar 34, met at the edge); all 6 disagreements are Haiku "yes" / Opus "no". Opus confirms 75 of 88 Haiku-yes points overall. Item-level agreement on validated items 30/36.
- Reading: even with every persona pack installed, the packs hold the answer to about a quarter of the items (19-21 of 71-75) and nothing for 27-35. Lexical candidate search can miss passages (recall unmeasured), so "NONE" may be slightly overstated; Haiku over-calls "yes", so the strict column is the safer AVAILABLE count.
- What this enables (spec r4): U on AVAILABLE vs NONE per arm, ORACLE (same model handed these passages) and ORACLE-0 (same model, no passages) on the 44-46 AVAILABLE + PARTIAL items: the same-item information effect.
