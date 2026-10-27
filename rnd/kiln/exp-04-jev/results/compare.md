# exp-04 side by side: Jev (frozen v2) vs precheck v2.2 vs claude -p judge (hand labels = truth)

## TEST (held out: run 4 Maple + baseline-mix 4B/Ling + 1.5B): n = 152

| Instrument | 4-class | binary (correct vs not) | CW precision | CW recall | cost per 1M answers |
|---|---|---|---|---|---|
| **Jev v2** | 117/152 = 77% | 130/152 = 86% | 25/38 = 66% | 25/30 = 83% | ~[usage detail removed] (measured) |
| precheck v2.2 (frozen; in-sample on run 4 Maple) | 113/152 = 74% | 136/152 = 89% | 5/7 = 71% | 5/30 = 17% | 0 (local regex) |

## TUNE (iPhone runs 2-3; Jev wording was tuned here), excluding the app's fixed-message declines: n = 59

| Instrument | 4-class | binary (correct vs not) | CW precision | CW recall | cost per 1M answers |
|---|---|---|---|---|---|
| **Jev v2** | 48/59 = 81% | 52/59 = 88% | 12/18 = 67% | 12/13 = 92% | ~[usage detail removed] (measured) |
| precheck v2.2 (frozen; in-sample on run 4 Maple) | 57/59 = 97% | 58/59 = 98% | 13/14 = 93% | 13/13 = 100% | 0 (local regex) |
| claude -p judge (binary only, correctness ≥ 4/5) | — | 42/59 = 71% | — | — | [usage detail removed] (≈ 0.02–[usage detail removed] list price per pair) |
| Jev v2 on the same 59 judged rows | — | 52/59 = 88% | | | |

