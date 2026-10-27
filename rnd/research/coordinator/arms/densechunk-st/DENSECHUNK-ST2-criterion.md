# DENSECHUNK-ST2: dense chunk hits as EXTRA slots (never displacing the lexical list) — does the reach gain survive without the empty-kept harm? (frozen 2026-10-13 11:2x, coordinator)

## Tags
Tags: none

## Question
Arm **X = packDense2 mode "extra"**: identical sidecars and two-stage candidates as DENSECHUNK-ST (lead top-50 → chunk cosine top-12 at ≥ 0.55), but instead of entering the 0.5/0.5 fusion, the top-D dense chunks (D = 2) that are not already in the OFF raw list are APPENDED to the OFF raw list (k = 6 + up to 2), in dense-score order, after the named hits and the OFF list; compression (400-token deep cap / the 4B cap) and grounding run unchanged on the longer list. Control **C** = packDense2 off (byte-identical to the published build). Why: DENSECHUNK-ST (FAIL at step 0) showed the two-stage path raises fact-chunk reach +42 % but, in the fusion, dense candidates displaced lexical hits that would have passed grounding, raising empty-kept by 2 per set and dropping one resolvable gold item from raw6. "Extra slots" cannot remove anything from the OFF list by construction, so the only open questions are whether the extra chunks still reach the kept context (compression may cut them) and whether they crowd the kept slots of the kit on the dev sets.

## Fixed inputs
As DENSECHUNK-ST (sidecars in shared-data/packs/v3proto/, wt/packs + the packdense2 patch with the new mode flag, the 180 public self-test items, the v0.1 public 60 and v0.2 110 no-harm replays with sidecars on the kit packs, the replay tooling arms/densechunk-st/tools/, Haiku 5.5-low N=4 both orders for stage 2, Opus L2 only for a claim-grade number).

## Power
expected_delta: +0.04 raw on the 180 items (source: DENSECHUNK-ST D0 — fact chunk reach 67 → 95 and article kept 68 → 95 under fusion; appending keeps the OFF hits so the reach gain is expected to be ≥ 60 % of that; SELFTEST-SCORES: with-pack lift tracks kept-from-pack share)
n: 180
seeds: 1 (greedy 4B; Haiku both orders)
mde: ≈ 0.03 raw paired at n 180
slice: n/a
l1_futility: n/a (Haiku has no cap; both OFF and ON judged on all 180)
reopen: DENSECHUNK-ST FAIL at step 0 (G2): the new mechanism is "extra slots, no displacement" — it removes the failure mechanism by construction rather than tuning a threshold
split: paired Δ by pack family (SE Q&A vs topic packs), declared; expected larger on topic packs

## Stages and rules
0. Step 0 (0 judge calls): the same replays (180 self-test items; v0.1 public; v0.2 script-only) with mode "extra":
   - **G1 reach:** fact chunk in raw top-8 (the appended list) on ≥ 84/180 AND fact chunk in kept ≥ 43 + 8 (≥ 51) AND fact article in kept not lower than 68.
   - **G2 no-harm:** v0.1 gold-in-kept ≥ 12 and v0.2 resolvable gold raw/kept not lower than OFF (6 / 4); **empty-kept not up** on either set (≤ 11, ≤ 28) — by construction this must hold; kit kept-slot share taken by the appended dense chunks reported (≤ 0.40).
   - **G3 cost:** p50 ≤ 2 × OFF; scan as before.
   All pass → stage 1; any FAIL → FAIL at step 0 (one declared variant: D = 2, floor 0.55, M 50, K2 12).
1. Generation: 4B cut 7 on the MacBook, ON for the 180 (OFF traces exist for all 9 packs with the pack installed: arms/packs/selftest-runs/st-<pack>-cut7-s42.traces.jsonl).
2. Haiku 5.5-low N=4 both orders on ON (OFF judgments exist from SELFTEST-SCORES); paired Δ raw/above_min over 180, by pack family.
3. Verdict: LEVER (CI low > 0 and Δ ≥ +0.03), SMALL (CI low > 0, Δ < 0.03), NO otherwise; "not decided at MDE 0.03" when |Δ| < 0.03 with CI through 0. LEVER → Opus L2 both orders on the 180 (720) before any pack-format statement to r4to (ship chunk_vecs: +~60 % pack size; two-stage 0.3–0.7 s on a phone).

## Stop rules and budget
0 paid API. MacBook disk ≥ 8 GiB; no mini. Never two generation jobs on the MacBook at once (the SELFTEST-DEEP watcher only fetches/judges).

## Outputs and exposure
arms/densechunk-st/{ST2-GATE.md, DENSECHUNK-ST2.md, tools/ (mode flag + reuse), aggregates/d0-st2.json, gate-st2.json, runs/st2-*.jsonl}; v0.2 replay under blind/bench-v02/runs-packs/densechunk-st2-* (script-only; EXPOSURES row). QUEUE rows per stage.
