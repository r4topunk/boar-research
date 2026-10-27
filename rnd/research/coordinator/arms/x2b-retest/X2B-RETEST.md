# X2B-RETEST result (2026-10-21 13:0x)

TL;DR
- **X2b: NOT CONFIRMED on real items, and not refuted (underpowered).** ON - OFF on REAL (25 non-self-test ids) = **+0.033 U_d (CI -0.100..+0.173)**. The bar was >= +0.02 with CI low > -0.01. The CI low is far below the bar. It does not fit the neutral band (|d| < 0.02) or the "pads" band (<= -0.02) either, so rule 3 applies: underpowered (n 25, MDE about 0.1).
- **On the 62 self-tests answered with the K1 kit, OFF is better: +0.032 (-0.033..+0.099).** Pooled over the 87, OFF - ON = +0.013 (-0.052..+0.074). CEu 11 -> 13, R 41 -> 39.
- **X2b's cost is certain:** OFF cuts prompt tokens by 46 % (796 -> 427 mean, live 81) and mean retrieval wall by 52 ms (180 -> 127).
- **V1orC: NO by rule.** U is fine: V1orC - ON on REAL is +0.034 (-0.021..+0.110), and CEu goes 2 -> 1. But the prompt-token cut is -13.0 % on all 81 live items and -8.1 % on the judged 59, short of the 15 % bar. Retrieval wall +28 ms (cosine scoring).
- **Reading:** on this pool, X2b has no measurable real-item gain under default-mode U. Its +0.066 self-test gain (pack-matched, 4B/Opus) does not show up at K1 (kit packs), where self-tests lean slightly to OFF. The claim text should say the pack gain holds on pack-written questions with the matching pack installed. An X2b-OFF default on kit-only installs is a candidate engine note (halves the prompt at no measured U cost). It needs an Opus or larger-n confirmation before any engine change.

## Setup
Criterion X2B-RETEST-criterion.md, sha256 3a3aaf0b…, committed 11fed7a4 before generation. 1.7B LITEPACKS K1, seed 42, mini (gen1/gen2 slots, 12:39-12:47, 2 x 87 rows, 0 errors).
- Arms: ON = mini control (null-cal/control/pool-K1.json), OFF = x2b-off.patch (adapter drops packHeadPass/packDense2), V1orC = retv1orc.patch.
- Judge: Haiku 5.5-low, judge.v1-low, N 4, both orders, changed answers only: **200 calls (cap 200)**, 0 Opus, 0 paid.
- Sanity: OFF 0 headpass:add codes (ON 52), V1orC retfloor codes on 87/87. Changed answers: OFF 77, V1orC 45. Context (kept sources or prompt tokens) changed: OFF 76, V1orC 42. 3 and 5 answers changed with an identical prompt (nondeterminism floor).

## Deviations (logged, not tuned)
1. The criterion's parenthetical set sizes were wrong: REAL is 25 and ST 62, not 37/50. The governing definition is the "st-" prefix, which divergent-main uses for st items as well. Decisions are read on the 25.
2. Cap rule applied: OFF was judged in full (154 calls), V1orC on 12 real + 11 st ids (46 calls). 22 st ids are unjudged, so V1orC's ST/POOL stats are on 40/65 ids (list in logs/x2bv1orc.judge.log). The runner copy got a second line (JUDGE_ALLOW) to enforce this.

## Table (aggregates/x2b-retest.json; d = arm - ON, item bootstrap B 2000 seed 11)
| arm | set | n | U_d ON -> arm | d (95 % CI) | CEu | R | prompt tok (live) | retrieval ms mean |
|---|---|---|---|---|---|---|---|---|
| OFF | REAL | 25 | 0.268 -> 0.235 | -0.033 (-0.173..+0.100) | 2 -> 3 | 12 -> 13 | 852 -> 454 (-47 %) | 167 -> 110 |
| OFF | ST | 62 | 0.230 -> 0.262 | +0.032 (-0.033..+0.099) | 9 -> 10 | 29 -> 26 | 772 -> 415 | 185 -> 134 |
| OFF | POOL | 87 | 0.241 -> 0.254 | +0.013 (-0.052..+0.074) | 11 -> 13 | 41 -> 39 | 796 -> 427 (-46 %) | 180 -> 127 |
| OFF | covered REAL | 23 | 0.261 -> 0.225 | -0.036 (-0.185..+0.103) | 2 -> 3 | 11 -> 12 | | |
| V1orC | REAL | 25 | 0.268 -> 0.302 | +0.034 (-0.021..+0.110) | 2 -> 1 | 12 -> 11 | 852 -> 759 (-11 %) | 167 -> 197 |
| V1orC | ST (judged) | 40 | 0.263 -> 0.267 | +0.003 (-0.009..+0.019) | 8 -> 10 | 17 -> 16 | | |
| V1orC | POOL (judged) | 65 | 0.265 -> 0.280 | +0.015 (-0.008..+0.044) | 10 -> 11 | 29 -> 27 | 817 -> 751 (-8 %); all 81 live: 796 -> 692 (-13.0 %) | 176 -> 203 |

## Verdicts by the frozen rules
1. X2b stays adopted? **No: not established** (+0.033, CI low -0.100 < -0.01). Not "real-item-neutral" (|d| > 0.02), and not "pads" (ON - OFF > 0, CEu ON 2 <= OFF 3). Underpowered per rule 3.
2. V1orC adopted? **No**: U holds (+0.034 >= -0.01, CEu not up), but prompt tokens fall 13.0 % (< 15 %).

UNKNOWN:
- Haiku compresses gaps (about 0.01). REAL n 25 cannot resolve +/-0.03. The decisive follow-up is an Opus pass on the 23 OFF-changed REAL answers (46 calls), or OFF on MAIN live 77 (the revisit entry's set).
- Whether the ST lean to OFF holds with each item's own pack installed (the LITE5-180 setting, where ON was +0.071 Haiku). Here the self-tests ran with the K1 kit, not their pack.

Files: X2B-RETEST-criterion.md(.sha256), x2b-off.patch, v1orc.patch, tools/{run_pool_x2b.sh,changed.py,report.py}, x2boff/ and x2bv1orc/ (traces, judgments, aggregates), aggregates/x2b-retest.json, v1orc-judge.allow, v1orc-judged.ids, PLAN.md, logs/.
