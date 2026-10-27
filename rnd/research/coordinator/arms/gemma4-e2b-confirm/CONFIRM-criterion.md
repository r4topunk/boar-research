# GEMMA4-E2B-CONFIRM criterion (frozen 2026-10-20 before any generation)

TL;DR: two confirmation measurements of the GEMMA4-E2B arm (engine-sampler variant E), requested by the coordinator. They are **evidence only**. They do **not** change the frozen GEMMA4-E2B stage-2 verdict (FAIL: dU +0.0281 < +0.03; stage2/verdict.json, criterion sha 690eeead...). There is **no pass/fail clause** in this file; the result is reported to r4to as numbers.

## System under test (unchanged from GEMMA4-criterion.md)
Gemma 4 E2B-it Q4_K_M (sha256 740185b2...4b8b) swapped for Qwen3-1.7B on the LITEPACKS mini tree, engine sampling 0.7/40/0.95/0.05, `--reasoning off`, compact tier, same requests (arms/litepacks, MAIN 97 ids = lp-screens/main-97.ids, sha 9664d81f...a2). Judge: Haiku 5.5-low, judge.v1-low, both orders, N = 4 shards, via lp-screens/tools/run_arm.sh (unchanged). Labels: null-cal/tools/labels.py (GATE v2). Generation on the Mac mini only, through the gen1/gen2 slot lock in lp-screens/tools/mini_gen.sh (shared; the job waits if both slots are busy).

## Measurements
| Id | What | Candidate run | Control |
|---|---|---|---|
| M1 | MAIN 97, pack set **K0**, sampler **seed 43** (both sides) | `gemma4-e2b-confirm-g43`: patches/g43.patch = gemma4-e2b-engsamp.patch (095ca9d7...) followed by null-cal/null-s43.patch, sha256 c35fbaf1a053f1e961be369c158420a4d3d4310d8d81e4f42d0d6a76616507da | `gemma4-e2b-confirm-c43` (1.7B, new, generated here): patches/c43.patch = null-cal/null-s43.patch, sha256 428d9f36e54b785950dad18b3daccc67dd53aa1d0a0c188b2a328c38435ea83a |
| M2 | MAIN 97, pack set **K1**, seed 42 | `gemma4-e2b-confirm-gk1`: patches/g42.patch = gemma4-e2b-engsamp.patch, sha256 095ca9d71b6f8814bf8e77e796531936cfe9f8f85559bdde5d8ba26b4fc2b248 | cached mini K1 MAIN control lp-screens/control/aggregates/lpctl-K1-main-s42.json (sha256 d370042b...bd; exists, not regenerated); also reported against the K0 control lpctl-K0-main-s42.json (sha256 36881814...9c) |
| ref | MAIN 97, K0, seed 42 (already run, not repeated) | stage2/aggregates/gemma4-e2b-eng-K0-main-s42.json (sha256 f51292b0...d4) | lpctl-K0-main-s42 |

- null-s43.patch changes only `samplerFor`'s seed (42 -> 43) in be/server.ts; the request seed (42) stays in the trace's `sampler` field, so a trace shows seed 42 while llama-server received 43. Health items run at temperature 0 and are unaffected by the seed. The 1.7B seed-43 control did not exist on MAIN (null-s43 ran only on the old K0 screen), so it is generated here.
- run_arm.sh names runs `<arm>-<K>-main-s42` whatever the seed; the run dirs are `arms/gemma4-e2b-confirm/runs/{c43,g43,gk1}` (the runner writes through temporary symlinks `arms/gemma4-e2b-confirm-{c43,g43,gk1}`, removed after the runs).
- Judge reuse (the harness rule, unchanged): an answer whose text is byte-identical to the s42 K0 / K1 control's reuses that control's judgment; only changed answers are judged. Judge noise on re-judged identical text is known (lp-screens/SCREENS.md: equal correctness on 24/37).
- Order of runs: c43, g43, gk1, sequentially (each waits for a mini slot). Sanity per run (void and repeated once if violated): traces n/n = 97, 0 error rows, 0 generation_failed, model.sha256 b139949c... on the control and 740185b2... on Gemma traces, 0 thought markers/reasoning tokens on Gemma; c43 and g43 must have >= 10 answers whose text differs from their seed-42 counterpart (lpctl-K0-main-s42 / the stage-2 Gemma run), else the seed patch did not act.

## Reported per measurement (tools/confirm_report.py, sha256 9749e229826c99e12fd58ece45c2f70978a029b0919717a394a929e1b978e585; B 2000, seed 11, items resampled, 95 % percentile CI as stage2_verdict.py; reproduces the stage-2 numbers on the seed-42 K0 pair)
1. dU = U_cand - U_ctl with the paired bootstrap CI (U = agg_run.py U, declined := 0), plus U_ctl, U_cand.
2. CE-unwarned rate (CE and not warned), control vs candidate, with counts, and dCEu.
3. Declines (labels.decline), warned, default-mode refused R (decline or warned) counts, control vs candidate; default-mode U (R := 0) and its delta with CI.
4. U on covered items (items the control shows, i.e. not declined/warned; refused := 0 for the candidate), delta with CI (GATE v2's U_cov definition, on MAIN).
5. Pooled two-seed K0 estimate: seed 42 (stage 2) + seed 43 (M1) stacked, items paired within seed, U_pooled = sum s / sum sref over both seeds' rows, dU_pooled with a cluster bootstrap over the 97 items (both seeds' rows of a resampled item move together); also CE-unwarned pooled rate and its delta with CI, and the plain mean of the two per-seed dU.
6. M2 is reported against the K1 control (same pack set) and against the K0 control (cross pack set), both paired on the 97 ids.

## Reading rule
Numbers are reported as measured, with the stage-2 verdict left standing. No threshold is attached to M1, M2 or the pooled estimate; if a reader wants to apply the +0.03 bar to them, that is a new, separate pre-registration by the coordinator, not this file.

## Budget
calls_cap: Haiku 600 (each run <= 2 x 97 = 194 calls, three runs <= 582; fewer in practice because byte-identical answers reuse control judgments). 0 Opus, 0 paid APIs. If the cap would be exceeded, the remaining run is not judged and the report says so. The Gemma GGUF stays on the mini (`<runner>/shared-models/lite/gemma-4-E2B-it-Q4_K_M.gguf`); mini disk guard >= 25 GiB is enforced by mini_gen.sh.
Tools used unchanged: lp-screens/tools/run_arm.sh (sha256 3285c023...4b), lp-screens/tools/agg_run.py (sha256 7fc23c00...d2), lp-screens/tools/mini_gen.sh.
