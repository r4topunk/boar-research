# LENGTH-TERCILE (web action 31.1 / W62, 2026-10-21): does CE rise with answer length inside the 1.5B Detailed rows?

0 LLM, 0 generation, 0 new labels. Script tools/length_tercile.py -> aggregates/length_tercile.json. 51 v0.1 dev ids (CV5), Qwen2.5-1.5B, Detailed persona, one run each.
Length = whitespace words of answer.text. Terciles by rank within the source (17/17/17). correct = mean of both orders' judge.v1 correctness >= 4; CE = <= 1.5 (shown answers; declined = answer.declined, 0 here). Totals match the published A1 (2.0 / 68.6) and STYLE15B (0.0 / 70.6) rows.
Note: the style15b-detailed traces are labelled qwen3-1.7b by the adapter, but the model sha (1adf0b11) is the 1.5B file, as in STYLE15B.

| source | judge | tercile (words) | n | median words | correct/100 | CE/100 |
|---|---|---|---|---|---|---|
| RC1 phone | Opus | short 44-293 | 17 | 229 | 5.9 | 47.1 |
| | | mid 294-358 | 17 | 319 | 0.0 | 82.4 |
| | | long 364-554 | 17 | 397 | 0.0 | 76.5 |
| N-D replica | Opus | short 20-277 | 17 | 193 | 5.9 | 58.8 |
| | | mid 277-334 | 17 | 318 | 0.0 | 52.9 |
| | | long 339-483 | 17 | 405 | 0.0 | 70.6 |
| style15b-detailed | Haiku | short 58-400 | 17 | 337 | 0.0 | 58.8 |
| | | mid 408-471 | 17 | 454 | 0.0 | 70.6 |
| | | long 477-782 | 17 | 552 | 0.0 | 82.4 |

Reading: within the same persona (Detailed) CE is higher in the long tercile than the short one in all three sources (+29 Opus phone, +12 Opus replica, +24 Haiku points per 100), monotone only under Haiku; correct stays at 0-6 per 100 everywhere. This is the direction facts-exhaustion (arXiv 2505.23295) predicts, but n = 17 per cell (one step = 5.9 points), no CIs, and length is confounded with question difficulty (hard questions get longer answers, see LENGTH-SLOPE): consistent with the prior, not a causal test.
