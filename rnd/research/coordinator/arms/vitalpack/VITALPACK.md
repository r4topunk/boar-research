# VITALPACK-DEEP step 0 — wiki-vital5 (49.8k Vital Articles intros) as a peer pack in the deep tier's kit: 0-call replay gate (2026-10-11, loop tick 2; criterion `VITALPACK-criterion.md` sha 40191652…; 0 judge calls, 0 generations, 5 retrieval replays ≈ 3 min on the MacBook)

**Verdict: the frozen arm (pack as a plain peer) FAILS gate (b) on v0.2 and is closed at step 0; the labelled post-hoc hypothesis "additive, quota-capped" (q = 1) passes all three gates on all three sets and becomes a new arm, VITALPACK-ADD, needing an engine patch before any run.**

## Gate (frozen): (a) v0.1 gold enters kept ≥ 5 and 0 emptied; (b) pack share of kept slots ≤ 40 % on every set; (c) ≥ 30 % of the base replay's empty-kept items keep ≥ 1 source with the pack
| set (n judged) | retrieving | empty kept base → vital | (c) filled | (b) pack share of kept slots (slots base → vital) | items with a pack chunk (of which already had curated kept) | (a) gold enters / leaves / emptied | recall@kept base → vital | retrieve p50 ms base → vital |
|---|---|---|---|---|---|---|---|---|
| v0.1 (60; 39 gold) | 46 | 13 → 8 | 5/13 = **0.385** ✓ | **0.358** ✓ (90 → 109) | 20 (15) | **7** / 0 / 0 ✓ | 0.205 → **0.359** (raw@6 0.256 → 0.538) | 115 → 176 |
| V-para (51) | 50 | 28 → 15 | 13/28 = **0.464** ✓ | **0.333** ✓ (64 → 84) | 17 (4) | — | — | 152 → 215 |
| v0.2 (110) | 107 | 47 → 24 | 23/47 = **0.489** ✓ | **0.612 ✗** (140 → 206; 34 items with curated kept also took pack chunks) | 56 (34) | — | — | 163 → 196 |
Fidelity of the replay's empty-kept set vs the H traces' no-kept items (LOSSMAP): V-para 28/29, v0.2 47/54 (4 of the 54 keep something in the replay: gate/detector differences).
Reading: on bounty-style V-para the pack behaves (one third of the slots, fills 13 of 28 empty items, displaces curated chunks on 4 items only); on v0.2 it crowds exactly as the enwiki pack did on DEEPWIKI (61 % vs 62 %), because v0.2's explanation/comparison/crypto items pull general-knowledge intros next to the crypto pack's own Wikipedia articles. The frozen rule says every set ≤ 40 % → **FAIL, no judge call.**

## Post-hoc hypothesis (the one allowed; labelled, not a verdict): additive quota — kept' = curated kept + the first q vital chunks of the pack run's kept list, never displacing a curated chunk (`tools/quota.py`, `aggregates/quota-hypothesis.json`)
| q | v0.1: gold enters · pack share · recall@kept | V-para: filled · pack share | v0.2: filled · pack share |
|---|---|---|---|
| 1 | **6** · 0.191 · 0.321 | 13/28 · 0.210 | 22/47 · **0.311** |
| 2 | 7 · 0.276 · 0.359 | 13/28 · 0.273 | 22/47 · 0.426 ✗ |
| 3 | 7 · 0.299 · 0.359 | 13/28 · 0.297 | 22/47 · 0.466 ✗ |
q = 1 passes (a) 6 ≥ 5, (b) ≤ 0.31 everywhere, (c) 0.39–0.47. It is not the engine's behaviour: implementing it means a second, pack-restricted `retrieve(q, 1)` after the curated retrieval, appended after grounding, with the deep context cap raised by ≈ 150 tokens (DEEPCTX: the cap barely binds; +1 chunk on every item adds ≈ 40 % kept slots on v0.2). That is the new arm **VITALPACK-ADD** (engine patch on dt512; replay fidelity check; then the criterion's stages 1–4). It is not a rescue of this arm's verdict.

## Caveats
- "Kept" = the engine's pre-answer sources as the replay reproduces them (compressContext under the deep 400-token cap, onSubject/health grounding); the additive variant's kept' bypasses the cap, so its real kept list will be shorter unless the cap is raised.
- Pack attribution: the engine reports formatVersion-1 pack chunks with `source` null; rule = null/Wikipedia source ∧ title ∈ wiki-vital5 ∧ title ∉ crypto pack's Wikipedia articles (base run: 1 seed-corpus collision on v0.1, 5 on v0.2).
- Gold exists for 39/60 v0.1 items only; V-para/v0.2 have no gold (coverage judged by "fills an empty kept list", not relevance).
- Replays with query text stay under `blind/<set>/runs-vitalpack/`; rnd holds counts and ids (`aggregates/gate-*.json`, `H-nokept-*.ids`).
