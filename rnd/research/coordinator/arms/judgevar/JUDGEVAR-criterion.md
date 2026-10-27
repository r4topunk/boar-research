# JUDGEVAR: Opus judge test-retest noise on unchanged traces (measurement; frozen 2026-10-11 03:0x, coordinator)

## Tags
Tags: none

## Question
RND-REVIEW-2026-10-10 §2.C C1: the paired CIs absorb per-item noise but not run-level judge noise; σ_judge was never measured. Re-judge the H s42 V-para traces (unchanged answers, unchanged references, same judge.v1 Opus, N = 4 shards, same ids) once more and compare to the frozen rows: run-level Δ of the raw and floor-adj ratios, per-item mean-rubric agreement (r, mean |Δ|), winner agreement, position consistency. Output σ_judge (the SD of the run-level ratio from two draws = |Δ|/√2) for the common-mode CI term `sqrt(SE_item² + 2σ_run² + 2σ_judge²)`.

## Fixed inputs
- Traces: `blind/V-para/runs-dt512/dh-H-vpara-s42.traces.jsonl` (DT512 arm H, frozen); references: original `refs/refs.jsonl`; ids: `runs-cut6/judged.ids` (51).
- Control rows: `runs-dt512/dh-H-vpara-s42.judgments.jsonl` (Opus judge.v1, 2026-10-09).
- New rows: `runs-dt512/dh-H-vpara-s42.judgments.retest.jsonl`, system `judgevar-H-retest`, `shard_judge.sh` N = 4 opus (102 calls), fail-closed check.

## Power
expected_delta: run-level |Δ raw| ≈ 0.01–0.02 (source: OPUSSHARD probe −0.014 on 10 ids; SEEDVAR per-item r 0.5–0.7 across seeds bounds judge+seed noise together); measurement, no verdict
n: 51 ids, both orders (102 calls)
seeds: judge seed 7 as always (the API is non-deterministic at temperature; this measures that)
mde: n/a (measurement); reported with the item-bootstrap CI of the paired Δ
slice: none (re-judge of existing traces)
l1_futility: n/a
reopen: n/a

## Stages and rules
1. Judge (102 Opus). 2. `deepvpara/tools/paired.mjs` retest vs original (same ids) → Δ raw, Δ floor-adj, per-item rows; `tools/agree.mjs` → r, mean |Δ| per item, winner agreement, order consistency. 3. σ_judge = |Δ raw| / √2 and |Δ floor-adj| / √2; write into BAR-TABLE as a note on CI width (together with SEEDVAR's σ_run 0.020 / 0.025). 4. No decision changes; if |Δ| > 0.03 the claim CIs are widened in CLAIM-DRAFT at the next weekly batch (independent reviewer).

## Stop rules and budget
≤ 102 Opus (week: 295 spent before this). Rate limit → resume, never skip a shard.

## Outputs and exposure
`arms/judgevar/JUDGEVAR.md`, `aggregates/`; one EXPOSURES row (re-judge of existing H s42 traces, 102 Opus, 0 generations).
