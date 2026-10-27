# PACKROUTE: with many packs installed, does routing the question to ONE relevant pack (or none) beat today's "all installed packs as peers"? (frozen 2026-10-13 12:4x, coordinator; direction from r4to: small specialised packs instead of a giant one)

## Tags
Tags: none

## Question
Realistic user setup = several Knowledge Packs installed at once. Today the engine searches every installed pack as a peer and fuses the hits (T-K4a: the 5 SE packs together take 0.479 of the kept slots and displace the kit's gold; simplewiki 0.83). Arm **R = router**: before `searchWikiPacks`, a deterministic router scores each installed pack for the question — vote of (i) the pack whose lead-cosine top-1 article is highest, (ii) the pack with the largest share of the top-20 FTS hits over all packs, (iii) exact title/alias match in the pack — and selects the top-1 pack when its score clears a margin, else "none" (then only the two kit packs crypto + wikivoyage are searched, as the shipped build does); the selected pack is searched with the normal k; the kit packs are always searched. Arm **Q = per-pack quota**: all packs searched, but each pack may hold at most 2 of the k = 6 raw slots (declared second variant, measured in the same replay). Control **P = peers** (today's engine with all 9 wave-1/2 packs + the kit installed). Reference **S = single**: the one-pack-installed replays/traces of SELFTEST-SCORES (upper bound). Reader = the shipped 4B (cut 7, greedy); judge = Haiku 5.5-low N=4 both orders; Opus L2 on a near-miss. packDense2 off (ST2 not adopted).

## Fixed inputs
- Items: the 180 public self-test items (9 packs × 20); kit dev sets for no-harm: v0.1 public (60) and v0.2 (110, script-only on blind).
- Packs: the 9 published files (shared-data/packs/wave1, wave2; published shas) + kit crypto/wikivoyage; engine tree wt/packs (T-K2 patch) + the router/quota patch (default off = byte-identical).
- Baselines: S = SELFTEST-SCORES OFF traces/judgments (st-<pack>-cut7-s42); P requires its own generation (all 9 installed) and judging — P is the control of this arm.
- Replay tooling: arms/densechunk-st/tools (replay-st / run_st) adapted to install all 9 packs.

## Power
expected_delta: +0.04 raw R vs P on the 180 (source: SELFTEST-SCORES with-pack lift +0.032 over no-pack tracks kept-from-pack share; T-K4a multi-pack crowding 0.479 → the peers setup is expected to lose part of the single-pack lift; R recovers it if the router is right on ≥ 85 % of items)
n: 180 (+ 60 / 110 no-harm)
seeds: 1 (greedy 4B; generation noise measured by the unchanged-sources Δ as in ST2)
mde: ≈ 0.03 raw paired at n 180
slice: n/a
l1_futility: n/a (Haiku no cap)
reopen: n/a (new family: pack routing; PACKCOND O1/O2 never tested; DEEPROUTE was tier routing, not pack routing)
split: paired Δ by pack family (SE vs topic); router accuracy by family (declared)

## Stages and rules
0. Step 0 (0 judge calls): replays on the 180 (all 9 installed) for P, R, Q and the reference S.
   - **G1 routing accuracy:** R selects the item's own pack on ≥ 85 % of the 180 (and "none" on ≥ 85 % of v0.1 + v0.2 kit items whose gold is not in a wave pack).
   - **G2 reach:** fact chunk in raw top-6 and fact article in kept under R ≥ 90 % of S's counts (S: chunk 67, article kept 68 → R ≥ 60 / ≥ 61) and ≥ P's; Q reported.
   - **G3 no-harm:** kit items: lost-context 0 vs kit-only (RULE 26), gold-in-kept not lower than kit-only; cost p50 R ≤ 1.5 × P.
   All pass → stage 1 (R and P generated; Q only if it beats R at step 0). FAIL → report; a learned router (4B classifier) is a separate criterion.
1. Generation: 4B cut 7, 180 items, arms P and R (and Q if selected), kit + all 9 packs installed.
2. Haiku N=4 both orders on P and R; paired Δ R−P over 180 and by family; also R−S (how much of the single-pack upper bound the router recovers).
3. Verdict: LEVER (CI low > 0, Δ ≥ +0.03), SMALL, NO, "not decided at MDE 0.03"; near-miss → Opus L2 (720).

## Stop rules and budget
0 paid API; MacBook only (no mini); disk ≥ 8 GiB; never two generation jobs at once (coordinate with the ST2 Opus L2, which only judges).

## Outputs and exposure
arms/packroute/{STEP0.md, PACKROUTE.md, tools/, aggregates/, packroute.vs-dt512.patch + .sha256, runs/}; v0.2 replay under blind/bench-v02/runs-packs/packroute-* (script-only; EXPOSURES row); QUEUE rows per stage.
