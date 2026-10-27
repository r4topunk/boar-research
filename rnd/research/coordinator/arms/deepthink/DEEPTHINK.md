# DEEPTHINK result (runner Kiln, 2026-10-08 16:02–20:20). Criterion DEEPTHINK-criterion.md sha256 1d988821da155b1f3fd053af43675db4eeb554649b64ed9d9469b9a99a6da366; patch deepthink-on-cut6.patch sha256 eb3f464b38782c7aabb950cb9c658102e92620f4e4a40dc54a5976eaa8d27ba6 (both `shasum` OK at start and close; not edited)
**L1: PROMOTED** (Haiku Δ T−D +0.046 ≥ +0.03; wins clause 0 ≥ 3 FAIL). **L2 (Opus, 2 seeds): T raw 0.542, floor-adj 0.422 vs D 0.467 / 0.329; paired Δ raw +0.075 (+0.040…+0.110), floor-adj +0.093 (+0.050…+0.137).** Bar ("floor-adj CI low > 0.50 and win-rate > 0"): below by 0.078 (point; CI low short by 0.115), win-rate 0/51 ×2. Cost: desktop p50 total **143 s vs 34 s (×4.2)**. No blind content entered the runner's context.

## Identity / pre-checks
| item | value |
|---|---|
| tree | mini `be-0cfd4a77-deepthink` = rsync of `-detmax` (minus be-repo/runs, .cache; node_modules symlinks kept; PATCH_SHA256 824e0b35… kept) + patch via `patch -p1`; `diff -rq` vs detmax: only `src/routing/depth.ts` (+ ARM, DEEPTHINK_PATCH_SHA256). src hash after patch 69d01a38… identical to the MacBook typecheck copy |
| typecheck | mini tree has runtime-only node_modules (no typescript/expo base) → `tsc --noEmit` on `git archive` of wt/detmax 5e5567ca (src hash db147fbe… = mini detmax) + same patch: **rc 0, 0 errors**. `vitest run src/routing/depth.test.ts`: 24/25 pass, **1 expected fail** ("uses the deep model in one pass over more context…", asserts `thinking: false`). Full suite not run |
| runner | tools/remote-run.sh (= deepvpara's on the deepthink tree; + checks `generate:deep-thinking` and `thinking: true, // DEEPTHINK` in depth.ts and the patch sha) → adapter 7a0282ae, `--backend server --deep-model qwen3.6-35b-a3b-ud-q2kxl`, settings {quickFirst, alwaysComplete, deepModelId}, detector v3b :8094 (51/51), ship profile, `--places` kit-vexact, llama-server b11010 CPU `-t 4`. Requests: cut6 V-para s42/s43 rewritten by mkreq; item sha 10675dae0530 and config (minus arm label) a7bbc7e3… identical to DEEPVPARA D |
| model / mini | GGUF sha 96b9c0af5c77… (shasum on mini + trace). Disk 35 GiB free throughout, swap 0.89–0.92 GB, load 1.5–3.5, no 35B server at start; detector up, never stopped; Docker untouched; heavy lock 0 s waits |
| smoke (v0.1 vit-hum-001, lan-exp-001) | try 1 (adapter default `--timeout-ms 120000`): 2/2 deep-thinking, reasoning 897/740, **both aborted by the adapter timeout before any answer token** (answer empty, `adapter:generation-timeout`). Try 2 (`--timeout-ms 600000`, Deviation 1): 2/2 `generate:deep-thinking`, reasoning 1034/1034 (budget hit), answer ≈ 92 tok, 0 errors, 136/163 s → PASS |

## Generation (V-para; desktop-proxy; medians over the 51 judged ids unless noted)
| run | n / errors / timeouts / empty | deep-thinking | reasoning tok p50 (p10) | budget hits /51 | answer tok p50 | reasoning ms p50 | total p50 (p90) | D total p50 | mini wall |
|---|---|---|---|---|---|---|---|---|---|
| dt-T-vpara-s42 | 58 / 0 / 0 / 0 | 51/51 (7 venue items `task:places`, no generation, as D) | 1034 (644) | **36** | 89 (D 81) | 104 s | **142.9 s** (164.9) | 34.2 s | 1.98 h |
| dt-T-vpara-s43 | 58 / 0 / 0 / 0 | 51/51 | 1034 (497) | **31** | 91 (D 78) | 105 s | **146.0 s** (171.5) | 32.1 s | 1.90 h |
All 58: T p50 141.5 / 142.0 s vs D 33.3 / 30.9 s. Budget hit = reasoning tokens ≥ 1024 (observed max 1034 = 1024 + the budget message; `thinkingBudgetExceeded` true on exactly those items). The message text itself is in neither trace nor server log (0 string hits), so hits are counted from tokens.

## L1 (Haiku 5.5-low, judge.v1-low, sharded N=4, both orders, 51 ids, refs 952e2c44d978 / questions aa604be6aa3f)
| seed | T ratio (CI) | D ratio (CI) | **Δ T−D (CI)** | Δ floor-adj (CI) | wins vs ref T / D | h2h T>D / = / T<D (descr.) |
|---|---|---|---|---|---|---|
| 42 | 0.512 (0.486–0.539) | 0.467 (0.437–0.498) | **+0.046 (+0.007…+0.081)** | +0.059 (+0.008…+0.107) | 0 / 0 | 31 / 8 / 12 |
Rule: "T wins ≥ D wins + 3": 0 ≥ 3 FAIL (read as wins vs ref, as DEEPVPARA; read as head-to-head it is 31 ≥ 15, also pass). "Δ ≥ +0.03": +0.046 PASS → **promote**.

## L2 (Opus judge.v1, sharded N=4 `--gap-ms 0`, `--system deepthink-T-opus`; scales as DEEPVPARA: floor_metrics stratified by items.jsonl, D_decl 0.306)
| view | T raw | T floor-adj | T win-rate | D raw | D floor-adj | Δ ratio T−D (paired.mjs) | h2h T>/=/< |
|---|---|---|---|---|---|---|---|
| s42 | 0.518 (0.486–0.550) | 0.392 (0.352–0.432) | 0/51 | 0.460 | 0.320 | +0.058 (+0.013…+0.103) | 29/9/13 |
| s43 | 0.566 (0.536–0.594) | 0.452 (0.414–0.489) | 0/51 | 0.474 | 0.338 | +0.091 (+0.056…+0.134) | 36/5/10 |
| **s42+s43** | **0.542 (0.513–0.571)** | **0.422 (0.385–0.459)** | **0/51 ×2** | 0.467 | 0.329 | paired_gap 2-level: raw **+0.075 (+0.040…+0.110)**, floor-adj **+0.093 (+0.050…+0.137)**, above-decl +0.107 | — |
T above-decline 0.340 (0.298–0.382). Haiku-no-web anchor 0.588 (Opus): T −0.046 (D −0.121). D values reproduce DEEPVPARA (s42 0.460/0.320, 2-seed 0.467/0.329).

## Per-category (Opus s42+s43, ratio T vs D, items T better/same/worse; counts only)
| category | n | T | D | Δ | b/s/w | correctness T / D |
|---|---|---|---|---|---|---|
| explanation | 17 | 0.548 | 0.523 | +0.025 | 11/1/5 | 3.78 / 3.72 |
| comparison | 7 | 0.529 | 0.440 | +0.089 | 6/0/1 | 3.36 / 2.75 |
| synthesis | 7 | 0.511 | 0.429 | +0.083 | 5/1/1 | 3.18 / 2.75 |
| reasoning | 7 | 0.568 | 0.424 | **+0.144** | 4/0/3 | 3.54 / 2.50 |
| crypto | 5 | 0.448 | 0.333 | +0.115 | 4/1/0 | 3.00 / 2.50 |
| travel-practical | 5 | 0.619 | 0.566 | +0.053 | 3/1/1 | 3.75 / 3.45 |
| travel-local | 3 | 0.564 | 0.462 | +0.102 | 3/0/0 | 3.58 / 2.67 |
Gain concentrated where DEEPVPARA-CATS flagged correctness ≈ 2.5–2.75 (comparison/synthesis/reasoning/crypto); explanation ≈ flat. Haiku s42 agrees in sign except travel-practical (−0.102, n=5).

## Deviations
1. **Adapter `--timeout-ms 600000`** (criterion: "everything else exactly as D"). The adapter's default 120 s is a desktop-harness cap; the app's planAnswer path has no per-generation timeout (LlamaEngine.ts), and D never reached it (0/51 timed out, max 62 s). Kept at 120 s, T aborts before the first answer token (smoke try 1), which measures the harness, not thinking. Tokens stay bounded by nPredict 200 + budget 1024. Result: 0 timeouts in T.
2. tsc ran on an identical-src MacBook copy, not on the mini tree (no typescript there). Opus via tools/shard_judge.sh (deepvpara's shard script + model arg; same judge.mjs flags as parjudge shard_run.sh) instead of parjudge's hard-wired shard_run.sh.
3. No Haiku on T s43 (not required). L2 D rows reused from DEEPVPARA (no D re-judge).

## Exposures (log in QUEUE)
V-para (blind/V-para), 58 items each: dt-T-vpara-s42, dt-T-vpara-s43 (generation); judged 51 ids: T s42 Haiku, T s42+s43 Opus; D s42/s43 judgments re-read by scripts (paired/scales/category). v0.1 (dev): smoke dt-smoke-T ×2 (2 items). Outputs: blind/V-para/runs-deepthink/ (+ smoke in boar-eval/runs/kiln/deepthink). Mini run dirs kept under the deepthink tree.

## Spend
Haiku 102 calls (≈ USD 0.08 list), Opus 204 calls (≈ USD 5.20 list; 0 failures, 0 exit-3/429, 201/211 s wall per seed). Mini ≈ 4.0 h heavy (s42 1.98 h, s43 1.90 h, smokes 10 min).

Tools: tools/remote-run.sh, dt.sh (mkreq/launch/status/fetch/think), shard_judge.sh, dtcat.py; reused deepvpara paired.mjs, l2-scales.sh, bench/v0.3/plan/paired_gap.py. Aggregates: aggregates/*.json (no per-item). Not committed.
