# LENGTH-SLOPE (web action 27.1, 2026-10-21): does judge.v1 reward longer answers?

0 LLM, 0 judge, 0 generation. Data: 13,310 existing judge.v1 (seed 7, both orders) rows under arms/ + ruler/ + boar-eval/runs + rnd/kiln, resolved to answer text through tracesSha256 (blind/veil never walked). Script: arms/web-actions/tools/length_slope_build.py (dataset) and length_slope.py (fits). Numbers: arms/web-actions/aggregates/length_slope.json.
Length = whitespace words of answer.text (about 1.3 tokens per word; no tokenizer). Score s = judge.v1 mean(correctness, completeness, usefulness), 1-5, both orders averaged. Slope b = change in s per doubling of words, OLS, 95 % CI from an item-id cluster bootstrap (B 1000, seed 11). Declined/warned = null-cal labels (warning line or refusal).

## Slope per doubling of length, per tier x judge
| tier | judge | rows / items | median words | declined+warned | all | shown only | within-item, shown |
|---|---|---|---|---|---|---|---|
| Qwen2.5-1.5B | Haiku | 147 / 44 | 154 | 18 % | +0.08 (+0.03, +0.13) | -0.02 (-0.11, +0.06) | -0.03 (-0.14, +0.08) |
| Qwen2.5-1.5B | Opus | 317 / 78 | 32 | 20 % | -0.05 (-0.14, +0.04) | -0.53 (-0.72, -0.33) | -0.06 (-0.25, +0.16) |
| Qwen3-1.7B | Haiku | 4757 / 331 | 43 | 38 % | -0.03 (-0.08, +0.03) | -0.04 (-0.11, +0.03) | +0.02 (-0.02, +0.05) |
| Qwen3-1.7B | Opus | 652 / 176 | 46 | 52 % | -0.18 (-0.37, -0.02) | -0.09 (-0.30, +0.09) | **+0.31 (+0.13, +0.48)** |
| Qwen3-4B | Haiku | 3452 / 392 | 67 | 1 % | -0.04 (-0.08, -0.00) | -0.05 (-0.09, -0.02) | -0.04 (-0.07, -0.01) |
| Qwen3-4B | Opus | 2402 / 275 | 54 | 2 % | -0.32 (-0.43, -0.20) | -0.39 (-0.49, -0.28) | -0.16 (-0.23, -0.08) |
| Gemma-4 E2B/E4B | Haiku | 58 / 42 | 44 | 5 % | -0.01 (-0.40, +0.44) | -0.06 (-0.46, +0.42) | -0.93 (-2.18, +0.16), n too small |
| Gemma-4 E2B/E4B | Opus | 265 / 57 | 49 | 5 % | -0.21 (-0.38, -0.04) | -0.25 (-0.43, -0.07) | -0.07 (-0.20, +0.06) |
| Deep 26-35B | Haiku | 114 / 57 | 77 | 0 % | -0.09 (-0.18, +0.00) | same | -0.07 (-0.17, +0.03) |
| Deep 26-35B | Opus | 395 / 57 | 154 | 0 % | -0.14 (-0.24, -0.04) | same | -0.04 (-0.13, +0.04) |
Partial slope (decline and warned dummies added, column "partial" in the json) is within 0.05 of "all" except Qwen2.5-1.5B (Haiku +0.08 -> -0.03; Opus -0.05 -> -0.49): there the positive raw slope was declines being short. Per 100 words the signs match (json: shown_per100w).
Across-item slopes are negative because hard questions get longer, hedged answers; the within-item column (item fixed effects, same judge, same tier, different answers to the same id) is the length effect closest to causal. It is still observational: the arms differ in more than length (retrieval, packs, X2b, seed).

## Paired contrasts (same id, two arms, ΔU vs Δlog2 words)
| contrast | cell | n pairs | mean Δs | mean Δlog2 words | slope (CI) |
|---|---|---|---|---|---|
| X2b ON - OFF | 1.7B, Haiku | 18 | +0.09 | +0.01 | not identified (length did not change; 14 of 18 pairs involve a warned/declined answer) |
| X2b ON - OFF | 4B, Haiku | 38 | +0.03 | -0.06 | +0.37 (-0.61, +1.39), no length variation to read |
| literal - succinct persona | 4B, Opus | 54 | -0.26 | +1.16 | -0.22 (-0.53, +0.04); shown-only -0.22 |
DEEPFULL (persona "detailed", 390 vs 89 tokens on the deep tier) has only head-to-head aggregates on disk (no per-item U, no traces with judge rows), so it is not in the fit; its reported result was Δ -0.013 (-0.069, +0.048) at 4x the length, i.e. longer did not win there either.

## Reading
judge.v1 does not reward length in our data: within-item slopes are zero or negative for the 4B (Haiku -0.04, Opus -0.16 per doubling), the deep tier, Gemma and the 1.5B, and a persona that doubled the length (literal, +1.16 doublings) scored -0.26 lower, so the Succinct-default quality guard is not tilted against Succinct for tiers at or above 4B. The one exception is the 1.7B under Opus (+0.31 per doubling, CI +0.13 to +0.48, 652 rows, 52 % warned/declined, X2b pairs carry no length variation), so a Succinct-vs-Detailed claim for the 1.7B should be run under both judges and quote this slope next to it; the uncapped ruler references (about 485 words) remain a separate length asymmetry this regression does not measure.
