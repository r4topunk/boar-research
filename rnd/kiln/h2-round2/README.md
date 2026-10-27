# H2 round 2: items selected by the OFF arm's outcome

Date: 2026-10-01 · Kiln · Coordinator-approved procedure · Rule: the frozen H2 (`../exp-09-instant-tier-gap/FROZEN-h2.sha256`, `3898ad80…`) and its criterion (§7 there) are NOT changed.

## TL;DR

The procedure, declared BEFORE the pool exists (08:23 -03):

1. **Forms only:** Veil gets only the question forms that end on an instant final answer (`forms-for-veil.md`: route triggers + templates, nothing about H2 or any result). He writes a pool of ≥ 60 items.
2. **OFF arm only:** `select-off.sh` runs H2-off on the pool, with the frozen off-arm arguments, in both profiles.
3. **Selection:** items whose OFF answer is an **instant final** (`tier: instant` + `instant:final`) in **both** profiles. The instant route is model-independent; if the profiles disagree on an item, it is dropped and reported. H2's decision is never computed at this step.
4. **Labels before H2:** hand labels of the selected OFF answers (pass / fail / cw / unsafe / refused) + Jev v2, written to `labels-before-<tag>.json` and **hashed** (sha256 sent to the coordinator) before step 5.
5. **Frozen run on the subset:** `run-h2-fresh.sh` on the selected subset (off / off-rep / on, both profiles). The re-run OFF must equal the selection OFF (determinism), else INVALID.
   - Labels of the H2-on answers that changed are added after (the "after" field). The before labels stay byte-identical (checked against the hash).
   - Then `analyze_h2_fresh.py`, criterion as frozen.
6. **Timebox:** if the selection yields < 10 instant finals by ~10:00, record INCONCLUSIVE and stop.
