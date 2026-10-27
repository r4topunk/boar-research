# DEEPTHINK-2 result (runner Kiln, 2026-10-08 18:30–23:05). Criterion DEEPTHINK2-criterion.md sha256 5af5b0132527cb90af38922f99f108cc369b548ff475279f64d8351968d89663 (`shasum -c` OK at start and close; not edited)
**Stage 1 (V-para s42, L1 Haiku): NOT PROMOTED.** Δ T2−T **+0.010 (−0.014…+0.041)** < +0.03; wins vs ref T2 0 vs T 0 (rule needs ≥ 3). Per the rule, the 1024 budget stays the reference thinking configuration. No Opus L2, no seed 43 (rule). No blind content entered the runner's context (ids, counts, hashes, route codes, timings, aggregates only).

## Identity / pre-checks
| item | value |
|---|---|
| tree | mini `be-0cfd4a77-deepthink2` = rsync copy of `be-0cfd4a77-detmax` (cut 6, PATCH_SHA256 824e0b35…; run dirs excluded) + `deepthink2-on-cut6.patch` sha256 **e813da6d480d5983eca97980e5575a199fad70e84656897e2ce0f5f7cc94fe95** (`patch -p1`, 2 files: depth.ts deep branch `thinking: true` + `generate:deep-thinking-3072`; answer.ts `DEEP_THINKING_BUDGET = 3072`); DEEPTHINK2_PATCH_SHA256 file checked by remote-run.sh |
| tsc | `tsc --noEmit` **0 errors** (wt/detmax node_modules + the mini tree's patched src/; src diff vs wt/detmax = exactly answer.ts, depth.ts) |
| adapter | committed boar-eval **2cbddfc** runner deployed into `be-repo/` by the setup.sh rsync (same excludes); `be-repo/adapter.ts` sha256 **da424129ca434973e19179446befe34927e485a00fb98abaa6fe6ef91c08657d** (gate/server/trace.ts identical to the old be-repo; only adapter.ts differs = BOAR_SERVER_CTX); trace adapter id desktop-node@0428b0f6b0b3 |
| context | env `BOAR_SERVER_CTX=8192`; llama-server cmdline `-c 8192` and server log `n_ctx_slot = 8192` (smoke and s42) |
| rest | as T/D: `--backend server --deep-model qwen3.6-35b-a3b-ud-q2kxl` (sha 96b9c0af5c77), `--threads 4 --timeout-ms 600000` (DEEPTHINK deviation 1), ship profile, detector v3b :8094 (up throughout, never stopped), places kit-vexact, heavy lock (0 s wait), Docker untouched |
| start gate | dt-T-vpara-s43 STATUS `end … rc=0` at 20:13 and no 35B server → smoke 20:15. Mini: disk 34 GiB free, swap 0.89–1.11 GB |
| requests | dt-T requests with runId + config.arm rewritten only (item sha 10675dae0530; all other fields identical to T s42/s43); s42 request sha 8eec78e7a5a7 |
| smoke | v0.1 vit-hum-001, lan-exp-001: both `generate:deep-thinking-3072`, reasoning 1609 / 1438 tokens (> 1024), `-c 8192` in server log, 0 errors, ≈ 212 s/item → PASS |

## Generation dt2-T2-vpara-s42 (20:31–22:54, 2.38 h, rc 0)
58 traces, 0 errors, 51 deep (all judged ids, all `generate:deep-thinking-3072`), 7 venue items `task:places` (instant), detector consulted 51, 0 gate events. Traces sha 6ba8b8a2284c.

## Thinking stats (51 judged ids)
| arm | budget | reasoning tok median (p10 / p90 / max) | budget hits | answer tok median | total p50 / p90 s | ttft p50 s |
|---|---|---|---|---|---|---|
| T (DEEPTHINK) | 1024 | 1034 (644 / 1034 / 1034) | 36 (≥ 1024) | 89 | 142.9 / 164.9 | 131.3 |
| **T2** | 3072 | **1294 (503 / 1753 / 2856)** | **0 (≥ 3000)**; 0 budget-exceeded | 87 | **176.3 / 239.8** | 162.4 |
35/51 T2 items thought past T's 1034-token cap, only 2 past 2048: the model stops on its own at ≈ 1.3k tokens. Unbounded thinking costs +23 % p50 / +45 % p90 wall over T for no measurable quality gain.

## L1 (Haiku 5.5-low judge.v1-low, sharded N = 4, both orders, `--system deepthink2-T2-haiku55-low`; judge log `refs 952e2c44d978, questions aa604be6aa3f` = cut 6 / T)
| view | T2 ratio (CI) | other ratio | **Δ T2−other (CI)** | Δ floor-adj (CI) | wins vs ref | h2h T2> / = / T2< (descr.) |
|---|---|---|---|---|---|---|
| T2 vs **T** (rule) | 0.523 (0.495–0.549) | 0.512 | **+0.010 (−0.014…+0.041)** | +0.013 (−0.018…+0.054) | 0 / 0 | 17 / 17 / 17 |
| T2 vs D (descr.) | 0.523 | 0.467 | +0.056 (+0.030…+0.087) | — | 0 / 0 | 31 / 10 / 10 |
Floor-adj (Haiku): T2 0.390, T 0.377. Rule: wins 0 ≥ 0 + 3 FAIL; Δ +0.010 ≥ +0.03 FAIL → **NO**.

## Per category (Haiku, T2 vs T; ratio Δ, items better / same / worse)
explanation (17) +0.004 5/7/5 · comparison (7) **+0.046 6/1/0** · synthesis (7) −0.032 0/5/2 · reasoning (7) +0.009 3/1/3 · crypto (5) **−0.060 1/0/4** (correctness 2.3 vs 3.2) · travel-practical (5) +0.124 2/1/2 · travel-local (3) −0.027 0/2/1. Small cells; descriptive only.

## Exposures (log in QUEUE)
V-para (blind/V-para), scoped script-only exception: generation dt2-T2-vpara-s42 (58 items); Haiku judging 51 ids (102 calls). Per-category script read items.jsonl categories (labels/counts only). v0.1 (dev): smoke 2 items (boar-eval/runs/kiln/deepthink2). s43 request file prepared but not run. Mini run dirs removed after sha-checked fetch.

## Spend
Haiku 102 calls (cap 120), 0 failures, 0 reruns, wall 158 s. Opus 0 (no promotion). Mini 2.5 h heavy (smoke 7.5 min + s42 2.38 h).

## Deviations
1. tsc ran on the MacBook (wt/detmax node_modules over the mini tree's patched src/), because the mini tree has no typescript; src identical to the mini tree.
2. `--timeout-ms 600000` kept from DEEPTHINK (ratified; coordinator re-confirmed at launch).
3. Budget-hit threshold ≥ 3000 reasoning tokens + engine `thinkingBudgetExceeded` flag; the budget message string never appears in traces (as in T).

Tools: tools/remote-run.sh (mini copy <runner>/kiln/deepthink2-remote-run.sh, sha 5d47cd54…), dt2.sh (mkreq/launch/status/fetch/think/ctx), l1.sh, l2.sh (unused), shard_judge.sh, paired.mjs, l2-scales.sh, dt2cat.py. Aggregates: aggregates/*.json (no per-item text). Outputs: blind/V-para/runs-deepthink2/. Not committed.
