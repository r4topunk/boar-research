# DEEPBO2 result (coordinator-run with one Opus tooling agent, 2026-10-10 10:5x–11:5x). Criterion DEEPBO2-criterion.md sha256 c7e2232f34f9c34c8d5168aa0ac87a0a7bed515dbf95c84284ccb8145c34ed11 (not edited). Tools: cb79a093… build.py,6a941855… select.py,674258b1… score.mjs,23b2f265… run-selector.sh
**Verdict: NO for every selector.** The deep tier's two seeds (DT512 arm H, V-para 51 judged ids, Opus judge.v1 rows) differ by +0.039 raw (s43 0.572 vs s42 0.533) and a judge-informed oracle reaches **0.590** (+0.038 over the expected single seed 0.553, +0.018 over s43). No selector that does not see the judge captures any of it: the 35B choosing between its own two answers (S1) and the 4B as verifier (S2) agree with themselves across the two presentation orders on only **33 % / 43 %** of items and with the oracle's strict winner on **49 % / 46 %** (chance); the free heuristics "longer answer" and "more citations" sit at the single-seed level. Best-of-2 at generation time (≈ ×2 the deep answer time) is closed: the gain exists only with the judge in the loop.

## Identity
| item | value |
|---|---|
| candidates | `blind/V-para/runs-dt512/dh-H-vpara-s{42,43}.traces.jsonl` (cut 6 + Qwen3.6-35B + thinking 512), scored by their existing Opus rows (both orders, judge-core combineOrders; 0 new judge calls) |
| pairs / prompts | `build.py` → `runs-deepbo2/pairs.jsonl` 10b868fa…, `prompts.jsonl` affdd1ab… (51 ids × 2 orders = 102 per selector; median 1,267 chars, 211–308 prompt tokens); frozen prompt in `select.py` 6a941855… ("reply with exactly one letter: A or B"); pick = both orders agree, else fallback to s42 |
| selectors on the mini | `run-selector.sh` under the heavy lock, llama-server b11010 CPU `-t 4 -tb 4 -c 4096 --jinja --reasoning-format deepseek` on :8097, temperature 0, max 8 tokens, thinking off (`enable_thinking=false`), seed 7, detector untouched. S2 = Qwen3-4B-Instruct-2507 Q4_K_M (sha 36058033…): 102 calls, 2.2 s median, 3.8 min. S1 = Qwen3.6-35B-A3B UD-Q2_K_XL (sha 96b9c0af…): 102 calls, 17.6 s median, 28.3 min. Parse failures 0/204 |
| scoring | `score.mjs` = paired.mjs conventions (ratio Σboar/Σref, floor-adjusted Σ(boar−1)/Σ(ref−1), paired Δ with items resampled jointly, 2000 boots) |

## Results (n = 51; win/tie/loss vs the reference 0/0/51 for every row)
| set | ratio (CI) | floor-adj (CI) | Δ vs s42 (CI) | Δ vs s43 (CI) | Δ vs oracle (CI) | oracle agreement | both orders agree | picks s42 / s43 / fallback | verdict |
|---|---|---|---|---|---|---|---|---|---|
| s42 single | 0.533 (0.500–0.563) | 0.412 (0.375–0.450) | 0 | −0.039 (−0.072…−0.011) | −0.057 | — | — | — | — |
| s43 single | 0.572 (0.538–0.607) | 0.460 (0.418–0.504) | +0.039 (+0.011…+0.072) | 0 | −0.018 (−0.027…−0.009) | — | — | — | — |
| expected single (mean) | 0.553 | 0.436 | — | — | −0.038 | — | — | — | — |
| oracle (judge-informed) | **0.590** (0.559–0.622) | 0.483 (0.445–0.524) | +0.057 (+0.034…+0.087) | +0.018 (+0.009…+0.027) | 0 | strict winner on 41/51 | — | — | upper bound |
| anti-oracle | 0.514 (0.482–0.545) | 0.388 (0.349–0.427) | −0.019 | −0.058 | −0.076 | 0 | — | — | lower bound |
| longer answer | 0.539 (0.505–0.575) | 0.419 | +0.006 (−0.008…+0.022) | −0.033 (−0.063…−0.009) | −0.051 | 0.41 | — | — | NO |
| more citations (tie → longer; 44/51 equal counts) | 0.540 (0.504–0.576) | 0.419 | +0.007 (−0.008…+0.023) | −0.033 (−0.063…−0.009) | −0.050 | 0.41 | — | — | NO |
| **S2 4B verifier** | 0.541 (0.508–0.572) | 0.421 (0.382–0.460) | +0.008 (−0.001…+0.019) | −0.031 (−0.063…−0.005) | −0.049 (−0.078…−0.026) | **0.46** | **43 %** | 10 / 12 / 29 | **NO** |
| **S1 35B self-selection** | 0.545 (0.512–0.577) | 0.426 (0.386–0.466) | +0.012 (−0.001…+0.030) | −0.028 (−0.057…−0.003) | −0.046 (−0.072…−0.025) | **0.49** | **33 %** | 8 / 9 / 34 | **NO** |
Rule (criterion): USEFUL needs Δ vs both seeds with CI low > 0 and mean ≥ +0.015; no row qualifies (every Δ vs s43 is negative).

## Reading
- Both models are position-driven: with the order flipped they change their pick on 57–67 % of items, and where they are consistent they match the oracle at chance. The oracle's +0.038 is mostly judge noise plus a real seed gap that a non-judge selector cannot see; the s43 > s42 gap itself (+0.039, CI excluding 0) says single-seed deep numbers carry ≈ ±0.02 seed variance, which the two-seed claim rows already absorb.
- For the device plan: no best-of-2, no verifier pass; one deep answer with thinking 512 remains the recommendation. The 4B "verifier" role in the engine has no measured value on this task.
- Caveats: one prompt (frozen, no iteration), temperature 0, answers only (no sources shown to the selector), V-para development-style data, 51 items.

## Exposures (script-only; no blind content in any context)
V-para: 0 generations, 0 judge calls; pairs/prompts built from H's traces by script; the two selector models read 51 questions + 2 answers × 2 orders each (model read, logged). Outputs: `blind/V-para/runs-deepbo2/` (pairs, prompts, raw replies, server/select logs), aggregates here (picks by id only). Cost: Haiku 0, Opus 0, mini 32 min, 1 Opus agent run (tooling).
