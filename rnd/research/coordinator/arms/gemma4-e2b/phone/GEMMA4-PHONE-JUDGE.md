# GEMMA4-PHONE-JUDGE (2026-10-21): Gemma 4 E2B on the Pixel 8a = desktop Gemma = the 1.7B level; the 4B on the same phone is +0.083 above it

TL;DR (Haiku 5.5-low, 57 device-parity v0.1 dev ids, raw ratio vs the reference): phone Gemma **0.452 (0.402-0.500)** vs phone 4B cut 7 **0.535 (0.492-0.583)**: Gemma - 4B **-0.083 (-0.123...-0.047)**, items better/worse 12/36 -> "4B better" (rule 1). Phone Gemma = desktop Gemma (two-seed): **+0.001 (-0.016...+0.017)** -> phone = desktop within noise (rule 2), inside the desktop two-seed band (s43 - s42 -0.008, CI -0.027...+0.008). Phone Gemma vs desktop 1.7B K0 (two-seed): **+0.008 (-0.020...+0.039)**, not distinguishable; vs the phone 1.7B (cmp30-q17, same phone and config, n 26 subset): +0.055 (-0.005...+0.117), not distinguishable (one run each; < 0.05-scale deltas are not robust orderings).

Criterion: JUDGE-criterion.md, sha256 36a0dbb870bdd51d..., committed 761ce3e0 before any judge call. Estimator: arms/device-x6/tools/agg_device.py functions imported unchanged (judge/tools/agg_gemma_phone.py) -> judge/aggregate.json. Calls: 228 Haiku (114 phone Gemma + 114 phone 4B), 0 failures, 0 Opus, 0 paid; cap 300. Dev ids only (no blind, no veil, no v0.4).

## Inputs
- Phone Gemma: gemma73-a/rows.jsonl (engine cut7-cmp30off-batchret, overrides off = cut 7 behaviour, claim kit, gemma-4-e2b-it Q4_K_M, thinking off) -> convert_device.py -> boar-eval/runs/device-pixel8a/gemma73-a/traces.jsonl (sha 1aad49b7...).
- Phone 4B: handoff/pixel8-2026-10-20/bench/results/final-cut7-v01 (Pixel 8a, 2026-10-20, cut 7, claim kit, Qwen3-4B Q4_K_M), judged here for the first time (the repo's earlier final-cut7-v01 judgments are the POCO X6 run) -> boar-eval/runs/device-pixel8a/final-cut7-v01/ (traces sha a9cb9653...).
- Desktop Gemma: stage-2 s42 + confirm g43 (MAIN 97, K0 litepacks, headpass-x2 engine, mini); desktop 1.7B: lp-screens/control lpctl-K0-main-s42 + confirm c43. Unjudged ids reuse the control rows (byte-identical answers: 15, 15, 20).
- Phone 1.7B: only cmp30-q17 (cut 7 product rules, 26 of the 57 ids) exists judged; no 57-id phone 1.7B run exists.

## Sets (n 57, raw (CI95), above_min, win/tie/loss vs the reference)
| set | raw | above_min | w/t/l |
|---|---|---|---|
| phone Gemma E2B (Pixel 8a) | **0.452 (0.402-0.500)** | 0.306 | 0/1/56 |
| phone 4B cut 7 (Pixel 8a) | **0.535 (0.492-0.583)** | 0.410 | 1/1/55 |
| phone 4B cut 7 (POCO X6, 10-14, context) | 0.529 (0.480-0.579) | 0.403 | 2/1/54 |
| desktop 4B cut 7 (stack OFF s42, context) | 0.529 (0.483-0.576) | 0.402 | 1/2/54 |
| desktop Gemma s42 / s43 / two-seed | 0.455 / 0.447 / **0.451 (0.404-0.501)** | 0.305 | 0/2/55 |
| desktop 1.7B K0 s42 / s43 / two-seed | 0.443 / 0.445 / **0.444 (0.399-0.492)** | 0.295 | 0/1/56 |

## Paired (A - B raw, 95 % CI, items better/worse)
| comparison | n | delta raw | above_min | better/worse | reading |
|---|---|---|---|---|---|
| (1) phone Gemma - phone 4B | 57 | **-0.083 (-0.123...-0.047)** | -0.104 | 12/36 | 4B better |
| phone Gemma - X6 phone 4B (context) | 57 | -0.077 (-0.120...-0.037) | -0.097 | 12/33 | 4B better |
| phone Gemma - desktop 4B cut 7 (context) | 57 | -0.077 (-0.115...-0.041) | -0.096 | 11/33 | 4B better |
| (2) phone Gemma - desktop Gemma (two-seed) | 57 | **+0.001 (-0.016...+0.017)** | +0.001 | 20/24 | within noise (parity) |
| phone Gemma - desktop Gemma s42 / s43 | 57 | -0.003 / +0.005 | | 19/19, 21/16 | |
| desktop Gemma s43 - s42 (two-seed band) | 57 | -0.008 (-0.027...+0.008) | | 13/16 | phone delta inside |
| phone 4B - desktop 4B cut 7 (config-matched device parity) | 57 | +0.006 (-0.015...+0.030) | +0.008 | 28/14 | within noise |
| (3) phone Gemma - desktop 1.7B K0 (two-seed) | 57 | **+0.008 (-0.020...+0.039)** | +0.010 | 27/20 | not distinguishable |
| desktop Gemma - desktop 1.7B (two-seed, raw ratio) | 57 | +0.007 (-0.018...+0.034) | | 21/18 | not distinguishable |
| phone 4B - desktop 1.7B K0 (two-seed) | 57 | +0.091 (+0.061...+0.125) | +0.115 | 40/9 | 4B better |
| (3) phone Gemma - phone 1.7B cmp30-q17 | 26 | +0.055 (-0.005...+0.117) | +0.072 | 14/8 | not distinguishable (subset) |
| phone 4B - phone 1.7B cmp30-q17 | 26 | +0.147 (+0.077...+0.223) | +0.188 | 17/6 | 4B better |
| phone Gemma - phone 1.7B cmp30off-q17 (override on, info) | 26 | -0.005 (-0.042...+0.031) | | 10/9 | info |
On the 26-id subset: phone Gemma 0.389, phone 4B 0.481, phone 1.7B cmp30 0.334, cmp30off 0.394.

## Per category (n 57, raw point only, no CI)
| category | n | phone Gemma | phone 4B | desktop Gemma | desktop 1.7B |
|---|---|---|---|---|---|
| explanation | 11 | 0.382 | 0.512 | 0.372 | 0.410 |
| reasoning | 11 | 0.489 | 0.623 | 0.537 | 0.532 |
| comparison | 7 | 0.378 | 0.474 | 0.347 | 0.388 |
| crypto | 7 | 0.333 | 0.323 | 0.343 | 0.275 |
| honesty-refusal | 6 | 0.642 | 0.716 | 0.606 | 0.590 |
| health | 4 | 0.414 | 0.543 | 0.450 | 0.425 |
| danger + danger-situation | 5 | 0.67 / 0.55 | 0.70 / 0.57 | 0.69 / 0.55 | 0.69 / 0.55 |
| synthesis / travel | 3 / 3 | 0.477 / 0.45 | 0.494 / 0.50 | 0.423 / 0.40 | 0.296 / 0.39 |
The 4B's lead is in explanation, reasoning, comparison and health (open-ended answers); crypto and safety items are level.

## Reading
1. On the phone, Gemma 4 E2B judges 0.08 below the claim 4B on the same 57 ids (CI excludes 0, 36 items worse vs 12 better). It does not replace the 4B on quality; it buys ~2.2x speed (GEMMA4-PHONE.md) for ~16 % of the 4B's raw score.
2. Phone Gemma reproduces desktop Gemma (+0.001), and the Pixel 4B reproduces the desktop 4B (+0.006): the Pixel 8a runs both models at desktop quality, as the A15 and X6 runs did for the 4B. The desktop Gemma reference is a different config (K0 litepacks, headpass-x2) from the phone (claim kit, cut 7); the match holds anyway, so on these 57 ids the kit/engine difference does not move Gemma's score.
3. Gemma vs the 1.7B: not distinguishable on the raw ratio (+0.008 vs desktop 1.7B; +0.055 vs the phone 1.7B on 26 ids, CI touches 0). This is consistent with the stage-2/confirm reading that Gemma's U gain comes from fewer refusals, not better answers on covered items (U and the raw ratio are different metrics; the +0.028 stage-2 dU was on MAIN 97 with U, this is the raw ratio on the 57 v0.1 ids).
Caveats: Haiku is the L1 triage judge (compresses gaps; Opus not run); one unseeded phone run per arm; v0.1 dev ids (public); the cmp30-q17 comparison is a 26-id subset from a different session.

## Files
- judge/aggregate.json (all numbers), judge/tools/agg_gemma_phone.py, judge/v01-57.ids, judge/judgments/{pixel8a-gemma73-a,pixel8a-cut7-v01}.{traces,judgments}.jsonl (copies).
- boar-eval/runs/device-pixel8a/{gemma73-a,final-cut7-v01}/ (rows, traces, judgments.haiku.jsonl, shards, judge.log).
