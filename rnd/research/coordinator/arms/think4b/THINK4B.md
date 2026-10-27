# THINK4B result (coordinator-run, 2026-10-10 10:33–11:31). Criterion THINK4B-criterion.md sha256 d3fe252253af80cc81137f8ee6b27ac28b01bb498e03cd6d4af0587548bda340 (not edited); 512 patch 6a977a29…; adapter boar-eval 796add7 (adapter.ts 1860ef9b…, server.ts 0d069273…)
**Verdict: NO (near-lever) for both budgets.** The thinking twin of the claim's 4B (Qwen3-4B-Thinking-2507 Q4_K_M) on the claim's fast path: at the engine's own budget 256 (**Y**) it scores no better than the instruct 4B (slice Δ −0.012); at 512 (**Z**) it reaches the full set and lands at Opus raw **0.439 vs K 0.413, Δ +0.026 (−0.013…+0.068)**, floor-adj **0.293 vs 0.261**, h2h 17/13/21, win 0/51, at **×3.7 the time** (p50 23.6 s vs 6.3 s on the desktop proxy). Under the frozen rule (Opus Δ ≥ +0.03 to continue; LEVER = CI low > 0 and ≥ +0.03) the arm stops after seed 42: the 4B-side stays closed, with the note that a thinking 4B is the first 4B arm since FACTS whose point is positive on V-para.

## Identity
| item | value |
|---|---|
| trees | mini `be-0cfd4a77-think4b` = rsync of `-detmax` (cut 6, PATCH_SHA256 824e0b35…) + be-repo adapter/server from boar-eval 796add7 (model entry + catalog entry roles general + fast, answerTier default) + ARM; `diff -rq` vs detmax: ARM, adapter.ts, server.ts. `be-0cfd4a77-think4b512` = rsync of think4b + `think4b512-on-cut6.patch` 6a977a29… (answer.ts FAST_THINKING_BUDGET 256 → 512); diff vs think4b: ARM, THINK4B512_PATCH_SHA256, answer.ts |
| model | `Qwen3-4B-Thinking-2507-Q4_K_M.gguf`, unsloth @ f40adb104d, sha ddd52e18… (= HF LFS oid; MODELS.md row), 2.5 GB, fetched to the mini 10:33 |
| runner / backend | `tools/remote-run.sh` (deepvpara runner + sha checks), llama-server b11010 CPU `-t 4 -c 4096 --jinja --reasoning-format deepseek`, settings `{quickFirst, alwaysComplete: false}` = C's, `--places` kit-vexact, detector v3b up throughout, `--timeout-ms 600000` (0 items > 120 s: max 29.8 s), heavy lock |
| controls | C = DEEPVPARA dv-C-vpara-s42 (4B instruct, same backend; Haiku rows; Opus 20-id rows judged here), K = cut6-vpara-s42 (claim rows, Opus), D = dv-D-vpara-s42 (deep tier, Opus) |
| budget enforcement | llama-server `thinking_budget_tokens` + budget message; the Qwen3-Thinking template pre-opens `<think>` and the budget sampler accepts the prefill tokens: Y max 264 = 256 + 8 message tokens, Z max 520. **DEVIATION 1:** the adapter flag `thinkingBudgetExceeded` = reasoningTokens > budget counts those message tokens, so the criterion's "budgetExceeded false" smoke clause was wrong; the flag is printed, not gated (gate.py); route, 0 errors, 1 ≤ reasoning ≤ budget + 10 and non-empty answers were gated as written |
| requests | smoke Y 30c9d2ca…, Z a4b5c2c7… (2 v0.1 items); slice Y cd3502eb…, Z e67a6715… (signal20-vpara 6e707734…); full Z s42 e4ee5f61… (58 = C's rewritten); s43 82befe13… prepared, not run |

## Stage 1–3: smokes and slices (seed 42; Haiku 5.5-low N = 4 vs C; L2 = Opus judge.v1 N = 4 on the same 20 ids, near-miss rule)
| arm | smoke | Haiku ratio (CI) | C Haiku | Δ vs C (CI) | h2h >/=/< | reasoning tok p50 (cap hits /20) | total p50 (C 6.4 s) | rule |
|---|---|---|---|---|---|---|---|---|
| Y (256) | 2/2, reasoning 264 / 220 | 0.346 (0.299–0.402) | 0.358 | **−0.012 (−0.050…+0.025)** | 9 / 5 / 6 | 264 (17) | 16.9 s (×2.6) | NO |
| Z (512) | 2/2, reasoning 303 / 220 | 0.387 (0.321–0.458) | 0.358 | **+0.029 (−0.045…+0.115)** | 7 / 4 / 9 | 513 (10) | 26.3 s (×4.1) | near-miss → Opus |
| Z (512) Opus 20 ids | — | 0.397 (0.319–0.483) | 0.306 | **+0.091 (+0.010…+0.185)** | 12 / 5 / 3 | — | — | CONTINUE |

## Stage 5: Z full 51 ids, seed 42
| judge | Z ratio (CI) | control | Δ (CI) | floor-adj Z / ctl | h2h >/=/< | win | rule |
|---|---|---|---|---|---|---|---|
| Haiku vs C (102 calls) | 0.453 (0.418–0.490) | C 0.431 | **+0.022 (−0.010…+0.060)** | 0.301 / 0.274 | 21 / 14 / 16 | 0 | near-miss → Opus |
| Opus vs K (102 calls on Z; K's rows reused) | **0.439 (0.401–0.476)** | K 0.413 (0.381–0.446) | **+0.026 (−0.013…+0.068)**; floor +0.032 (−0.016…+0.088); two-level gap +0.026 (−0.010…+0.067) | **0.293** / 0.261 | 17 / 13 / 21 | 0/51 | **NO** (< +0.03) |
| Opus vs D (ladder) | 0.439 | D 0.460 | −0.021 (−0.060…+0.025) | 0.293 / 0.320 | 13 / 9 / 29 | — | — |
Time (desktop proxy, 51 judged): p50 **23.6 s** (p90 29.8) vs C 6.3 s and K's node-backend run; ttft 19.9 s (the whole thinking block precedes the first visible token); reasoning median 370 tokens, 15/51 at the 512 cap; answer tokens median 66 (C 77). 58/58 rc 0, 0 errors, 7 venue items routed instant/places as in C.

## Reading
- Budget 256 is too short for this model: 85 % of items hit the cap mid-thought and the answers are no better than the instruct twin's. At 512 the gain is real but small on the claim scales (+0.026 raw, +0.032 floor-adj, Opus; K higher on 21 items vs Z on 17): below the +0.03 continuation bar, CI straddles 0, win-rate still 0. The slice (20 hardest items) overstated it (+0.091): the gain concentrates on the hard, reasoning-style items.
- Cost on a phone: ≈ 370 extra tokens per answer at the 4B's decode rate; on the 8 GB Galaxy A15 the 4B decodes at 2.0–2.7 tok/s (QUEUE l.695; review v3.8 finding 1), so ≈ 2–3 min of thinking before the first visible token; faster chips (Dimensity 8300 class) are unmeasured. Not shippable as the default fast path; a per-task route ("reason only on compare/calculate/research") was not tested (would be a new arm; the per-category split is in `aggregates/cat-ZvsK-1seed.opus.json`).
- Ladder (V-para raw, Opus, s42): K 4B 0.413 → **Z thinking-4B 512 0.439** → D deep no-think 0.460 → deep + think 512 ≈ 0.55 (DT512). A thinking 4B at 24 s recovers about half of the no-think deep tier's gain over the 4B on a 2.5 GB model.
- Claim text: unchanged (cut 7 stays the claim build). CLAIM-DRAFT gets one levers row: "thinking 4B (Qwen3-4B-Thinking-2507, budget 512): +0.026 raw (−0.013…+0.068) at ×3.7 time, one seed, not adopted".

## Exposures (script-only; no blind content in any context)
V-para: slice 20 × 2 gens (Y, Z s42) + full 58 × 1 gen (Z s42); Haiku 20 + 20 + 51 ids (182 calls); Opus 20 (Z) + 20 (C) + 51 (Z) ids (182 calls); K/D Opus rows re-read by scripts. Smokes on v0.1 (dev). Outputs: `blind/V-para/runs-think4b/` (+ `runs-deepvpara/dv-C-vpara-s42.judgments.opus-slice20.jsonl`), smoke in `boar-eval/runs/kiln/think4b/`, aggregates here (no per-item text). Cost: Haiku 182, Opus 182, mini ≈ 45 min (download 3 min, smokes 4, slices 14, full 20), agent runs 0.

## Addendum: THINK4B-V02 (2026-10-10 14:44–15:3x; criterion THINK4B-V02-criterion.md sha256 bfdcfbe01a6ced5abba8d9c1023916ecfd2b55df5553676482136f99cbe69fc0, not edited)
**Verdict: NO on v0.2 too.** The thinking 4B at budget 512 (same tree, `noplaces` as the claim's Run A) on the seed-stable v0.2 set, seed 42, Haiku 5.5-low N = 4 paired vs C (4B instruct, same backend):
| stage | n | ZV ratio (CI) | C | Δ (CI) | h2h >/=/< | rule |
|---|---|---|---|---|---|---|
| slice (signal20-v02, 20 hardest cut-6 items) | 20 | 0.318 (0.258–0.392) | 0.229 | **+0.089 (+0.031…+0.160)** | 11 / 7 / 2 | CONTINUE |
| full | 110 | 0.485 (0.453–0.517) | 0.475 | **+0.009 (−0.015…+0.035)** | 40 / 35 / 35 | **NO** (not a near-miss) |
Generation: 110/110, 0 errors; reasoning median 266 tokens (13/110 at the 512 cap; 4 items routed instant with 0), answer tokens median 54 (C ≈ 77), p50 **17.6 s** (p90 27.2; ttft 15.0 s) vs C ≈ 6 s. No Opus pass (the rule stopped at Haiku; the v0.2 Haiku–Opus gap on 4B arms is ≈ +0.02 at most, which would still leave the point under +0.03).
Reading: on both sets the thinking 4B lifts the hardest 20 items by ≈ +0.09 and the full set by +0.01 to +0.03; the gain is real where the instruct 4B fails outright and absent elsewhere, and it costs ×3 the answer time everywhere. Together with THINK4B (V-para, one seed, +0.026) the thinking twin is closed as a claim lever. Exposure: v0.2 (dev) 1 slice gen + 1 full gen; Haiku 20 + 110 ids (260 calls); Opus 0.
