# MIN3CITE-OPUS (2026-10-21): PASS stands under Opus. MIN3CITE is +0.047 U over the 1.7B on MAIN 97 (CI +0.021...+0.075), seed 42; Haiku +0.062

Criterion MIN3CITE-OPUS-criterion.md (sha 0006d1f3..., rnd 3aaf0954) was frozen with the unit set before any call. Step A was 0 calls (rnd 865f282c). Step B used **150 new Opus judge.v1 calls**, exactly the cap of 150. Every shard returned rc 0, every unit got both orders, and there was no STOP file. Reused: all 97 control units (GEMMA-OPUS-MAIN pool) and 22 MIN3CITE units with identical text. 0 generation, 0 Haiku, 0 paid.
Outputs: MIN3CITE-OPUS-stepA-2026-10-21.json, MIN3CITE-OPUS-2026-10-21.json (sha cbc365455422...). Tools: tools/min3cite_opus_{prep,analyze}.py and min3cite_opus_run.sh.

## TL;DR
- **Verdict: PASS stands** (frozen rule: dU >= +0.03 and CI low > 0). dU is **+0.0465 [+0.0205, +0.0745]**. Under Haiku it was +0.0623 [+0.037, +0.088].
- **Opus shrinks the gain by 0.016.** This is not because Opus favours the longer answers. Opus lifts the 1.7B more than it lifts MIN3CITE (offset +0.029 vs +0.013).
- **At equal length the gain is not established.** The OLS estimate of dU at equal answer length is +0.027 [-0.006, +0.064] under Opus and +0.023 [-0.007, +0.057] under Haiku. About 40 % of the gain goes with the extra ~46 tokens.
- **Against the 4B (report only), MIN3CITE is at best level.** Under Haiku, on all 97 items, MIN3CITE - 4B is -0.014 [-0.038, +0.011]. Under Opus, on the 61 items whose 4B answer already had an Opus row, it is -0.037 [-0.059, -0.016]. That subset is not random.
- **Kill clauses of the revisit entry** (ruler/revisit-closed-2026-10-21.json; not this criterion's rule): "Opus dU vs 1.7B < +0.048 -> closed" fires (+0.0465), and "Opus MIN3CITE - 4B < -0.02" fires on the partial 61. Under that entry, the line is **closed (dominated by the 4B)**, even though the PASS stands under this criterion.

## Step A (0 calls), 75 live items
| | 1.7B | MIN3CITE | 4B |
|---|---|---|---|
| answer tokens median / mean | 47 / 45.5 | 106 / 105.6 (x2.32) | 68 / 68.4 |
| words median | 42 | 76 | 61 |
| [n] brackets in text (items) | 19 (17) | 47 (23) | 20 (16) |
| citations kept by the engine (items) | 18 (17) | 33 (23) | 19 (16) |
Haiku per item: 75 texts changed; better / worse / tie 48 / 18 / 31; Spearman of the item delta vs the token delta 0.21. No live MIN3CITE answer is <= 47 tokens (minimum 51).

## Step B, Opus judge.v1, MAIN 97 K0 seed 42 (item bootstrap B 2000 seed 11)
| measure | 1.7B | MIN3CITE | Opus delta [95 % CI] | Haiku delta |
|---|---|---|---|---|
| **U** | 0.435 | 0.481 | **+0.047 [+0.021, +0.075]** | +0.062 [+0.037, +0.088] |
| CE-unwarned (count) | 6 | 5 | rate -0.010 [-0.083, +0.052] | 7 -> 6 |
| CE any | 18 | 14 | | 23 -> 18 |
| declined / warned / refused R | 7 / 39 / 46 | 7 / 33 / 40 | | same |
| default-mode U (refused = 0) | | | +0.053 [+0.026, +0.083] | +0.056 |
| U on items both answer (n 49) | 0.528 | 0.578 | +0.050 [+0.014, +0.086] | +0.058 [+0.026, +0.091] |
| items better / worse / tie | | | 40 / 24 / 33 | 48 / 18 / 31 |

## Length-adjusted views (report only, no truncation re-judge)
| view | n | Opus dU [CI] | Haiku dU [CI] |
|---|---|---|---|
| L1: both shown, MIN3CITE tokens <= 1.7B median (47) | 15 | 0.000 | 0.000 |
| L2: both shown, MIN3CITE tokens <= 1.5x the 1.7B's | 19 | +0.011 [0.000, +0.030] | +0.003 [-0.020, +0.028] |
| **L3: OLS intercept, dU at equal length** | 97 | **+0.027 [-0.006, +0.064]** (slope +0.040 per 100 tokens) | +0.023 [-0.007, +0.057] |
Disclosure (the frozen definition, not changed): L1 contains only dead items with identical text (0 live answers are that short), so it carries no information. L2 is 15 dead items plus 4 live ones. L3 is the only informative view, and it is observational.

## Opus vs Haiku
| arm | U Opus | U Haiku | offset [CI] | Spearman s | CE agree / correct agree (of 97) |
|---|---|---|---|---|---|
| 1.7B | 0.435 | 0.406 | +0.029 [+0.007, +0.050] | 0.88 | 88 / 83 |
| MIN3CITE | 0.481 | 0.468 | +0.013 [-0.010, +0.036] | 0.86 | 85 / 90 |
Spearman of the per-item delta, Opus vs Haiku: 0.66. dU shift Opus - Haiku: -0.016. The offset is asymmetric, as the revisit entry suspected. It runs against MIN3CITE, not for it.

## Sentences the page may use (each names the judge, 1 seed, dev)
- "Under Opus, MIN3CITE (Ministral-3-3B with a citation prompt) is +0.047 U over the 1.7B on MAIN 97 (CI +0.021...+0.075), 1 seed, dev questions. Under Haiku it is +0.062."
- "Part of that gain comes with longer answers (2.3x the 1.7B's tokens). Estimated at equal length, the gain is +0.027 under Opus, and its CI includes 0."
- "MIN3CITE is not better than the 4B. Under Haiku it is -0.014 (CI -0.038...+0.011) on the same 97 questions, and the 4B was measured on a phone while MIN3CITE's time is only projected."
- "MIN3CITE is not offered to the app maintainer: its projected phone answer time is about 3x the 1.7B's (p50 21.6-25.6 s vs 6.8-7.9 s on a Pixel 8a, projected)."

## Sentences that may NOT be used
- "MIN3CITE gives better answers" without the length caveat: the equal-length estimate has a CI that includes 0.
- Any comparison with the 4B under Opus as a full-set number: the Opus 4B rows cover 61/97 items, and that subset is not random.
- Any U without its judge family, or "phone-tested": the phone time is projected, and PSS is unmeasured.

## Limits
One seed; n 97 dev; the judge sees the warning line; the control units were exposed to Opus in earlier passes; the length views are observational.
