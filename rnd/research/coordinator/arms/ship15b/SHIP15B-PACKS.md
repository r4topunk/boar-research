# SHIP15B-PACKS (2026-10-21): the K1 packs do not measurably help the shipped Qwen2.5-1.5B (NO-GAIN, Opus)

Criterion SHIP15B-PACKS-criterion.md (sha 1d0cb24c..., rnd f79a1745), frozen before generation; analysis tools/ship15b_analyze.py (rnd 2167ed54, committed before any judgment).
Output aggregates/ship15b.json. Calls: 94 new Opus judge.v1 (cap 120) + 4 reused pool units; 100 Haiku judge.v1; 99 Haiku DECLINE2STAGE stage 1; 0 paid, 0 phone.

## TL;DR
- **Verdict: NO-GAIN.** Opus judge.v1 + D2S: dU(packs - closed-book) = **+0.015 (-0.036...+0.068)**, 20 better / 15 worse. Rule needed >= +0.03 with CI low > 0.
- No harm: CE-shown -5.9 per 100 (-17.6...+5.9), i.e. 13 vs 16 CE answers of 51. Haiku agrees: +0.011 (-0.032...+0.055).
- Retrieval did run: 48/51 items kept a source, yet the 1.5B answer barely moved in score. It reads the packs about as well as it remembers.
- Context: the 1.5B + K1 sits **-0.082 (-0.157...-0.011) U below the 1.7B K0 rung** under Opus (0.270 vs 0.351, same 51, same host). The ship model is the weaker reader.
- Cost of the packs on the desktop: wall p50 1.7 s -> 5.9 s (pack search + longer prompt), tokens unchanged (44 -> 48 p50).

## Setup (both arms: Mac mini M4, tree be-0cfd4a77-cut7-litepacks, llama-server b11010 CPU -t 4, seed 42, Succinct, maxTokens 512, FACTS off)
| arm | what | traces | generated |
|---|---|---|---|
| P packs | Qwen2.5-1.5B-Instruct Q4_K_M (sha 1adf0b11) under the 1.7B id, K1 kit, retrieval on | arms/ship15b-packs/traces/ship15b-packs-K1-main-sub3e6183-s42.traces.jsonl | 10-21 17:56, 2-slot mini |
| C closed-book | same model and patch base, retrieve() returns [] (FLOOR-ANCHORS run, reused) | arms/floor-anchors/traces/floor-anchors-K0-main-sub3e6183-s42.traces.jsonl | 10-21 04:02, mini |
Same-host comparable: same tree, binary, threads, seed, persona, model swap; the request kit field differs (inert when retrieval returns []). Not interleaved (13 h apart).

## Levels (v0.1 dev, CV5 51 ids, seed 42, host mini, item-cluster bootstrap B 2000 rng 11)
| judge | arm | U floor-adj (CI) | U raw | U_net | win-rate | correct-shown /100 | CE-shown /100 | D2S not-attempted |
|---|---|---|---|---|---|---|---|---|
| Opus + D2S | P packs | **0.270** (0.200-0.350) | 0.419 | 0.225 | 0.02 | 27.5 | 25.5 | 0 |
| Opus + D2S | C closed-book | 0.255 (0.184-0.336) | 0.406 | 0.209 | 0.02 | 27.5 | 31.4 | 2 |
| Opus v1 only | C closed-book | 0.261 (0.189-0.342) | 0.412 | 0.216 | 0.02 | 27.5 | 31.4 | - |
| Haiku | P packs | 0.220 (0.165-0.288) | 0.385 | 0.172 | 0.00 | 19.6 | 35.3 | - |
| Haiku | C closed-book | 0.209 (0.154-0.272) | 0.375 | 0.161 | 0.00 | 21.6 | 37.3 | - |
| Haiku | 1.7B K1 mini control (Succinct, FACTS on) | 0.263 (0.201-0.333) | 0.419 | 0.217 | 0.02 | 27.5 | 27.5 | - |
| Opus v1 (CV5 rung) | 1.7B K0 mini control | 0.351 (0.279-0.437) | - | - | - | - | - | - |
The C Opus v1 row reproduces the CV5 L0 rung (0.261). The 1.7B K1 row has Opus pool rows on only 20/51 texts, so it has no Opus level (no new calls by the criterion).

## Paired P - C
| judge | dU floor-adj (CI) | dU raw | better / worse | d CE-shown /100 (CI) | rule |
|---|---|---|---|---|---|
| Opus + D2S (primary) | **+0.015 (-0.036...+0.068)** | +0.012 | 20 / 15 | -5.9 (-17.6...+5.9) | NO-GAIN |
| Opus v1 | +0.008 (-0.041...+0.060) | +0.007 | 19 / 15 | -5.9 | - |
| Haiku | +0.011 (-0.032...+0.055) | +0.010 | 20 / 18 | -2.0 (-15.7...+11.8) | - |
Context, Opus v1: P - 1.7B K0 = -0.082 (-0.157...-0.011), CE 13 vs 8 of 51 (kit differs: K1 vs K0).

## Cost per arm (51 ids, mini)
| arm | out tokens p50 / mean | wall p50 | wall sum | items with a kept source |
|---|---|---|---|---|
| C closed-book | 44 / 44 | 1.7 s | 86 s | 0 |
| P packs | 48 / 49 | 5.9 s | 292 s | 48 |

## Reading (for NOTE-5 and S01)
- The packs are not the 1.5B's lever: with the same model, adding K1 changes the judged usefulness by about +0.01 under both judges. The CI cannot rule out +0.07 or -0.04.
- The model is the lever: the 1.7B with the K0 kit is +0.08 U above the 1.5B with K1 under Opus. S01 should not credit packs for the 1.5B. The ship ask stays "add the 1.7B entry" (NOTE-1).
- CE-shown falls a little with packs (-3 answers of 51), not significant. This is in line with the packs grounding some answers. It is not a safety claim.
- Sentence S01 may print: "On the shipped 1.5B, our packs moved judged usefulness by +0.015 U (CI -0.036...+0.068; Opus, 51 dev items, one run): no measurable gain."

## Limits
One seed; n 51 dev; control generated 13 h earlier (not interleaved); FACTS off in both 1.5B arms; TS bench engine with our prompts, not the native RC1 app (its Detailed default and built-in KB differ); desktop wall, not the phone.
Deviation: the Opus judge pass ran without the shard_judge preflight (it requires a pre-L1 clause block); the criterion declares the Opus use and cap; the run script checks the sha and cap (as cv5_ladder_run.sh).

## Files
arms/ship15b/{SHIP15B-PACKS-criterion.*, patches/ship15b-packs.patch, tools/, opus/P.*, stage1/, aggregates/ship15b.json, ship15b-diag.json}; arms/ship15b-packs/ (run_arm outputs).
