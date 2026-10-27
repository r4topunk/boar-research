# STYLE15B (2026-10-21): Succinct is not worse than Detailed on either small model, and it is about 25 s cheaper per answer on the phone

Criterion STYLE15B-criterion.md (sha 474ac0a0..., rnd f79a1745), frozen before generation; addendum 1 (post-hoc Opus diagnostic, frozen before its 22 calls).
Analysis tools/ship15b_analyze.py -> aggregates/ship15b.json; diagnostic tools/ship15b_diag.py -> aggregates/ship15b-diag.json.
Calls: Haiku judge.v1 184 new (1.5B-D 100, 1.7B-D 84; 1.5B-S = SHIP15B arm P, 100 counted there; 1.7B-S = existing K1 control rows), Opus 22 (addendum); 0 paid.

## TL;DR
- **Verdict: NONINFERIOR on both models** (Haiku, CI low of S - D >= -0.02).
  - 1.5B: S - D = **+0.087 (+0.038...+0.143)**, 28 better / 11 worse. Succinct is better, not just not worse.
  - 1.7B: S - D = **+0.038 (-0.005...+0.084)**, 21 / 11.
- Detailed doubles the confident errors under Haiku: CE-shown per 100, 1.5B 35 -> 71, 1.7B 27 -> 53 (S - D -35 and -25, CIs exclude 0).
- Detailed writes +496 tokens p50 (1.5B) and +357 (1.7B) per answer. At RC1's 18.6 tok/s (1.5B) and the 1.7B's 14.3 tok/s that is **about 27 s and 25 s more per answer** on the phone (projection).
- Opus check on the 1.7B (11 ids only): S - D +0.018 under Opus vs -0.066 under Haiku on the same 11. That is too few ids to say more than "Opus does not favour Detailed here".

## Setup (Mac mini M4, tree be-0cfd4a77-cut7-litepacks, b11010 CPU -t 4, seed 42, K1 kit, v0.1 dev CV5 51 ids)
| arm | model | persona (tree's own) | maxTokens | FACTS | traces | run |
|---|---|---|---|---|---|---|
| 1.5B-S | Qwen2.5-1.5B Q4_K_M | succinct | 512 | off | arms/ship15b-packs/traces/ (SHIP15B P) | 10-21 17:56, parallel with 1.5B-D |
| 1.5B-D | Qwen2.5-1.5B Q4_K_M | detailed | 1024 (native Detailed cap) | off | arms/style15b-detailed/traces/ | 10-21 17:56 |
| 1.7B-S | Qwen3-1.7B Q4_K_M | succinct | 512 | on | arms/lp-screens/control/traces/lpctl-K1-main-s42 (existing) | earlier mini run |
| 1.7B-D | Qwen3-1.7B Q4_K_M | detailed | 1024 | on | arms/style17-detailed/traces/ | 10-21 17:57 (queued behind 2 jobs) |

## Haiku 5.5-low judge.v1, both orders, n 51, seed 42, host mini (item-cluster bootstrap B 2000 rng 11)
| model | arm | U floor-adj (CI) | U raw | win-rate | correct-shown /100 | CE-shown /100 |
|---|---|---|---|---|---|---|
| 1.5B | Succinct | 0.220 (0.165-0.288) | 0.385 | 0.00 | 19.6 | 35.3 |
| 1.5B | Detailed | 0.133 (0.098-0.172) | 0.317 | 0.00 | 0.0 | 70.6 |
| 1.7B | Succinct | 0.263 (0.201-0.333) | 0.419 | 0.02 | 27.5 | 27.5 |
| 1.7B | Detailed | 0.224 (0.165-0.293) | 0.387 | 0.02 | 17.6 | 52.9 |

| model | dU S - D (CI) | dU raw | better / worse | d CE-shown /100 (CI) | verdict |
|---|---|---|---|---|---|
| 1.5B | **+0.087 (+0.038...+0.143)** | +0.068 | 28 / 11 | -35.3 (-51.0...-19.6) | NONINFERIOR |
| 1.7B | **+0.038 (-0.005...+0.084)** | +0.031 | 21 / 11 | -25.5 (-39.2...-11.8) | NONINFERIOR |

## Tokens and wall per arm (51 ids; 0-token rows are deterministic layers: 1 on the 1.5B, 9 on the 1.7B)
| arm | out tokens p50 (generated rows) | rows at cap | words p50 | wall p50 mini | wall sum | paired dTok D - S p50 (p10-p90) |
|---|---|---|---|---|---|---|
| 1.5B-S | 49 | 0 | 41 | 5.9 s | 292 s | |
| 1.5B-D | 557 | 0 / 1024 | 454 | 16.0 s | 834 s | +496 (+359...+706), n 50 |
| 1.7B-S | 46 | 0 | 40 | 4.3 s | 190 s | |
| 1.7B-D | 400 | 0 / 1024 | 303 | 16.9 s | 750 s | +357 (+305...+438), n 42 |
Mini wall is CPU desktop with 2 jobs in parallel (1.7B-S ran in another session), so read the tokens, not the seconds. Phone projection = dTok / decode rate (RC1 1.5B 18.6 tok/s, Pixel 8a 1.7B 14.3 tok/s).

## Opus diagnostic (addendum 1, no rule): 1.7B, the 11 ids with an existing Opus row on the Succinct text and a changed Detailed text
| judge | U S | U D | S - D | better / worse | CE S / D | mean dlog2 words |
|---|---|---|---|---|---|---|
| Opus | 0.276 | 0.259 | +0.018 | 5 / 4 | 4 / 3 | +3.1 |
| Haiku | 0.191 | 0.257 | -0.066 | 3 / 6 | 5 / 5 | +3.1 |
Reading: LENGTH-SLOPE's +0.31 per doubling (1.7B, Opus, observational) would predict Detailed about +0.9 higher on the 1-5 item score at +3.1 doublings. On these 11 Opus scores Succinct +0.06 higher (mean item score). So the slope does not carry over to a persona change. n 11, one run: a sign, not a number.

## Reading (for NOTE-1's Succinct ask)
- Detailed costs ~25 s per answer and buys no measured quality on either model under Haiku. On the 1.5B (the RC1 ship model, whose default is Detailed) it loses 0.09 U and doubles the CE count.
- The CE jump is mostly long Detailed answers with more invented specifics. Caveat: Haiku labels more CE than Opus on shown answers (CV5-PER100: Haiku-only CE 5, Opus-only 0). On the 11 Opus ids, CE D was 3 under Opus vs 5 under Haiku. The CE gap is likely smaller under Opus; its sign is not tested.
- NOTE-1 may say: "With our packs, Succinct scored +0.09 U (1.5B) and +0.04 U (1.7B) over Detailed (Haiku, 51 dev items, one run) and saves about 25 s per answer."

## Limits
One seed; n 51 dev; Haiku only for the verdict; bench TS engine with the tree's own persona prompts (the native app's prompts may differ); FACTS off on the 1.5B pair, on for the 1.7B pair; 1.7B-S is an earlier mini run, not interleaved.
