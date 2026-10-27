# VITALPACK-ADD: one Vital-Articles intro added to the deep thinking tier's kept sources, never displacing a curated chunk (frozen 2026-10-11 13:0x, loop coordinator)

## Tags
Tags: none

## Question
Arm **A** = the recommended deep configuration H (dt512 tree: cut 6 + DEEPTHINK + DT512, Qwen3.6-35B-A3B UD-Q2_K_XL, thinking 512, succinct, ctx 400, k = 6) + the VITALPACK-ADD engine patch with `settings.addPack = {"id":"wiki-vital5","k":1,"pool":6}` and `wiki-vital5` (sha d3b87d562baba3489f6878bf99783f50d504db94c347029771e53f6d1aecc666) in `config.kit`: after the curated retrieval and grounding, one extra retrieve restricted to the vital pack (pool 6) is compressed on its own 150-work budget, passed through the same onSubject / health-strict grounding, and the first surviving chunk is appended to the kept sources. Does this move the deep tier's score on v0.2 (direction) and V-para (confirmation)?
Mechanism evidence (VITALPACK.md step 0, 0 calls): the plain-peer pack fails the crowding gate on v0.2 (61 %); the additive q = 1 variant keeps the pack at 19–31 % of kept slots, fills 13/28 V-para and 22/47 v0.2 empty-kept items (the LOSSMAP no-kept bucket = 55 % / 50 % of H's loss), puts gold into 6/39 v0.1 items; the patched engine reproduces the simulation on 57/60 v0.1 items (ADD-PATCH.md), default-off byte-identical 60/60.
reopen: DEEPWIKI closed "corpus size as a plain pack" (crowding); this is additive with a quota, a different mechanism; DEEPCOV-FB closed "pack only on R2 items" (gold entered 1); this adds on every deep item (gold enters 6).

## Fixed inputs
- Tree on the mini `<runner>/kiln/be-0cfd4a77-vitaladd` = dt512 tree + `arms/vitalpack/vitaladd.vs-dt512.patch` (sha in its `.sha256`; cut-7 form `vitaladd.vs-cut7.patch` 78b94478…); adapter boar-eval 684235f (forwards retrieve opts); runner `vitaladd-remote-run.sh` (dt512 runner + sha checks). Requests = H's with the kit entry and the setting; `config.arm` = `vitaladd`.
- Control **H** = dt512 rows: v0.2 Haiku `dhv-H-v02-s42` (slice ids from the 110), Opus `L2-H-1seed`; V-para Opus s42/s43 (`dh-H-vpara-s{42,43}`). K = cut 6 rows for the ladder.
- Blind sets script-only (runner + judge); exposures logged.

## Power
expected_delta: +0.02 raw on V-para, +0.02 on v0.2 (source: VITALPACK step 0 fills ≈ 46 % of the no-kept items, which hold 55 % / 50 % of H's loss at mean ratio 0.55 / 0.60; DEEPNORAG values the whole curated kit at +0.045 for this tier; one relevant intro on half the empty items ≈ a quarter of that effect → +0.01…+0.03)
n: 110 (v0.2, s42) for direction; 51 × 2 seeds (V-para) for confirmation
seeds: 1 on v0.2; 2 on V-para
mde: v0.2 one seed ≈ 0.025 raw; V-para two seeds ≈ 0.03 → expected_delta ≈ mde: a LEVER can only be shown at the full two-seed V-para stage; the slice screens futility only
slice: random20-v02.ids (sha a3e43672…)
l1_futility: stop only if Haiku delta <= 0 AND h2h <= control; any Haiku delta > 0 -> Opus N=4 on the same 20 ids
reopen: see Question

## Stages and rules
1. Smoke (3 v0.1 items: vit-hum-001 = H's smoke item, lan-cmp-004 = gold enters, dng-002 = health item whose added chunk passed the health filter): pack resolves (sha check), 3/3 `generate:deep-thinking`, 1 ≤ reasoning ≤ 522, 0 errors, non-empty answers, `addpack:*` code present on 3/3 and `addpack:kept-1` on ≥ 2/3; record retrieval time vs H's smoke (ttft 78 / total 87 s). Else FAIL-INFRA (fix and rerun the smoke only).
2. L1 slice random20-v02 s42 (Haiku 5.5-low N=4, both orders) vs H's Haiku rows on the same 20 ids; rules above; near-miss rule (L1-PROTOCOL 10-10) applies.
3. v0.2 full 110 s42: Haiku vs H → Opus N=4 (220) vs L2-H-1seed: direction (CONTINUE if Opus Δ > 0 or CI low > −0.01).
4. V-para s42 + s43 (Opus N=4, 204) vs H two seeds (`paired.mjs --common-mode 0.020,0.025`).
Verdict: **LEVER** (V-para two-seed Δ ≥ +0.03, CI low > 0) / **SMALL** (CI low > 0, Δ < 0.03) / **NO**; "not decided at MDE" when |Δ| < 0.03 with the CI through 0. One generation per seed and stage; no rerun except an infrastructure error before the first token.

## Stop rules and budget
Mini: disk ≥ 25 GiB, swap ≤ 8 GB, heavy lock, one MoE server, detector untouched; smoke ≤ 15 min, slice ≤ 1 h, v0.2 full ≤ 4 h, V-para ≤ 2.5 h per seed. Judge calls only from Mon 2026-10-12 (week caps): Haiku ≤ 40 (slice) + 220 (full) (+ 40 near-miss); Opus ≤ 40 (near-miss) + 220 + 204.

## Outputs and exposure
`arms/vitalpack/VITALADD.md`, `aggregates/`, blind traces/judgments under `blind/<set>/runs-vitaladd/`. One EXPOSURES row per set and stage.
