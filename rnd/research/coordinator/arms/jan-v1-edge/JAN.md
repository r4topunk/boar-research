# JAN-V1-EDGE result (2026-10-21): NO-GO on all 4 gate v2 screens; no stage 2

TL;DR: janhq/Jan-v1-edge (Qwen3-1.7B base, SFT + RLVR, Apache-2.0, Q4_K_M) as a drop-in for the Qwen3-1.7B lite engine, thinking off, fails GATE v2 on K0 and K1 for both samplers. It answers 3x longer (out tokens ~118-153 vs 41-44), leaks visible reasoning / `</think>` in ~half the answers (22-24 per run), drops `[n]` citations (10-20 of 17-28 control-citing items keep one), and loses utility on covered items (U_cov -0.065 to -0.134, all below the bar). Stage 2 does not run (needs GO on K0). Line closed; GGUF deleted from the mini (class A).

Criterion: JAN-criterion.md sha256 3a1740ea30ec3b25de835f3999d146bb7e4f956e4f0ba6aa273ade8653f44085 (checked unchanged), gate arms/null-cal/GATE-V2.md + screen_gate_v2.py. Onboarding: ONBOARDING.md (template identical to Qwen3 stock; the empty-think prefill does not hold under sampling).

## Per-screen gate lines (screen_gate_v2.py, verbatim numbers)
| Run | net (bar) | false ref (max) | U_cov delta (min) | new CEu | CE cand/ctl | Verdict |
|---|---|---|---|---|---|---|
| V jan-v1-edge K0 (n 50) | 8 (10) | 2/20 (2) | -0.0655 [-0.1128, -0.018] (-0.059) | 3 | 25/30 | NO-GO |
| E jan-v1-edge-eng K0 (n 50) | 7 (10) | 2/20 (2) | -0.0793 [-0.1263, -0.0362] (-0.059) | 4 | 28/30 | NO-GO |
| V jan-v1-edge K1 (n 41) | 10 (9) | 5/20 (4) | -0.1336 [-0.2066, -0.0676] (-0.071) | 0 | 17/21 | NO-GO |
| E jan-v1-edge-eng K1 (n 41) | 9 (9) | 4/20 (4) | -0.0969 [-0.1711, -0.0224] (-0.071) | 1 | 17/21 | NO-GO |
K0 fails net and U_cov on both variants; K1 fails U_cov on both (and false refusals on V).

## §2 extras (tools/report.py, tools/sanity.py; 0 LLM)
| Run | think-marker answers | [n] compliance | out tok cand / ctl (p50) | totalMs cand / ctl (ratio) | at 768 cap |
|---|---|---|---|---|---|
| V K0 | 23/50 | 11/17 | 141.4 / 41.2 (96) | 3964 / 2130 (1.86x) | 1 |
| E K0 | 24/50 | 10/17 | 117.5 / 41.2 (95) | 4144 / 2130 (1.95x) | 0 |
| V K1 | 24/41 | 17/28 | 150.4 / 44.0 (119) | 5629 / 3625 (1.55x) | 0 |
| E K1 | 22/41 | 20/28 | 152.7 / 44.0 (94) | 5707 / 3625 (1.57x) | 1 |
Sanity (all 4): traces n/n, 0 error rows, 0 generation_failed, model.sha256 = bdde4346... on every trace, reasoningTokens 0. Runs valid.

## Calls
Haiku 5.5-low, N 4 shards, both orders: K0 100 + 100, K1 82 + 82 = 364 screen calls (calls files) + 30 onboarding = 394 of the 700 cap. 0 Opus, 0 paid.
Resume note: the K1 v01 judge passes died at 01:20 (the previous account hit its session limit; shards wrote STOP, partial rows 7/14 V, 1/14 E). run_pool.sh's preflight then refused the resume (planned remaining 8 != declared 2m = 14). Fix: STOP files removed, shard_judge.sh run directly on the same args for v01 (judge.mjs resumed the ok rows; 14/14 rows each), then run_pool.sh K1 judged the other 11 units. The calls files count v01 as 14 per run (the old account's partial rows included). Runner gap for the coordinator: run_pool.sh declares 2m even when resuming partial rows.

## Paths
- Gate: screens/<arm>/aggregates/<arm>-<K>-screen2-<K>-s42.gate2.{txt,json}; aggregates .json beside them
- Traces: screens/<arm>/traces/; judgments: screens/<arm>/judgments/; logs: screens/logs/, screens/<arm>/runs/logs/
- Arms: jan-v1-edge (V, jan-v1-edge.patch), jan-v1-edge-eng (E, jan-v1-edge-engsamp.patch)

## Disk
Jan-v1-edge-Q4_K_M.gguf deleted from the mini (class A); recipe row in rnd/kiln/MODELS.md, DISK-LOG line. Pending: none.
