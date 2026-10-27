# PACKCOND P4 step 0 replay gate: packGround (2026-10-12; 0 LLM, 0 judge calls)

**Verdict: FAIL.** The F0 article is kept on 14/32 items with the setting on; the gate needs ≥ 16. Control kept lists change on 6/20; the gate allows ≤ 4.

Setup: `tools/replay-pg.sh` (copy of deepcovfb replay-deep.ts plus `--pack-ground` and `--diag`). Options: `--deep --gate rules --k 6 --pool 20 --tree wt/packcond --tasks-from` the H v0.2 traces. Packs: crypto + wikivoyage. Cache: deepcovfb. Raw lists are identical to the H traces (32/32 and 20/20). Outputs: blind/bench-v02/runs-packcond/ for v0.2 and arms/packcond/replay/ for v0.1. Aggregates: `aggregates/p4-gate.json` and `aggregates/p4-diag.json`.

Loss classes on the in-pack items (diagnosis; see PATCH-DESIGN.md):
- H, n 32: not in raw 15 (14 not in the top-20 pool), grounding 3, health filter 1, compression 2, kept 11.
- K, n 20: not in raw 11, grounding 1, health filter 1, ambiguous between grounding and compression 1, kept 6.

| metric | off | on |
|---|---|---|
| H32: F0 article in kept | 11/32 | **14/32** (enters crypto-B05, travel-practical-B01, travel-practical-B02; leaves 0) |
| H32: kept lists changed | – | 13/32 |
| H32: empty kept / kept slots | 11 / 48 | 6 / 63 |
| R20 control: kept lists changed | – | **6/20** (comparison-A03, crypto-B05, health-A04, honesty-refusal-B01, reasoning-B04, synthesis-B02) |
| R20: empty kept / kept slots / pack share | 10 / 17 / 0.82 | 5 / 25 / 0.84 |
| v0.1 public (39 gold items): gold in kept | 13 | 14 (enters lan-exp-004, leaves 0) |
| v0.1: kept lists changed / empty kept | – / 15 | 27 of 60 / 7 |
| default off vs the pre-patch (dt512) replay | identical (H32 and R20, all fields except timing) | – |

Reading:
- The gate is out of reach for any grounding lever. Grounding plus compression lose only 6 of the 21 missed articles, so the ceiling is 16/32, and only if every loss is recovered, including the health-filter item and a passage with 0.09 coverage. The largest loss is upstream: on 15/32 items the fact-holding article never reaches raw, and on 14 of those it is absent from the top-20 pool.
- On the control set, 5 of the 6 changes fill an empty context. Of all the lever's changes, only 3/32 hit the target article, so it is noisy as a general rule.
- Next lever, if the line continues: retrieval-side, so the question's words reach the pack article. Candidates: pack-aware query expansion with title/section, or a pack router (O1). This needs a different gate than the grounding one. packGround stays off and is not promoted to judge calls.

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file; the gate is stated only with the result (no pre-registration).
