# RETBENCH v1 — bench + 12-point knob sweep on SEFIX-124 (0 LLM) — 2026-10-23 18:3x

Criterion SWEEP-criterion.md (sha in SWEEP-criterion.sha256, frozen before any arm replay, unchanged). Tree kiln-local/rs-RETBENCH (rs-SEFIX + RETBENCH-KNOBS.patch), MacBook only, 0 LLM / 0 judge / 0 paid. Stage A and the base were run by the 10-23 agent (killed by the 17:4x restart after 8 aggregates); stage B/C (2 runs) and this report by the night session.

## Bench (one command, tools/retbench.sh <config.json>)
Sets (items/, SHA256SUMS): MAIN 92 keyed chunk-level facts, 180 self-tests (own fact chunk / own article kept), 27 TOPICS (expected article kept), 48 F8 follow-up pairs (96 turns), LONGSESSION 50 turns. Base identity vs the rs-SEFIX references: kept ids MAIN 97/97, ST 180/180, TOPICS 27/27, F8 96/96, LS 50/50 (aggregates/identity.base.json); base = MAIN 42, ST own-article kept 100, fact chunk 77, TOPICS 24, F8 survived 1, LS 4 (P1 holds; TOPICS recorded as measured, 24 here vs 25 with the K13 topics recipe).

## Pruning as frozen
Stage A ran 7 points (k 4/6/8, floor 0.65, pool 2000, lead on, compress 0.4). Cap and within-article pick were cited from ARTCAP (cap4/capfact/cap4lead = 39-40 facts, NO) per the ARTCAP-overlap rule, so the 7 cap/pick configs (configs/unused/) were not rerun (coordinator cut to 12 points at 16:21). Helpful levels: k 4 (+2 MAIN), compress 0.4 (+1 MAIN), k 6 (MAIN = base, ST fact +5). Stage B = k4 + comp40 (the only 2-knob combination); stage C = swap k to its second-best level (k6 + comp40).

## Table (tools/table.py; ms on a busy MacBook, not comparable)
| config | MAIN facts (d) | cm / v01 | +/- | ST fact | ST own kept | TOPICS | F8 | LS | health losses | ctx p50 (x) | eligible |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **B-k4comp40** | **45 (+3)** | 15 / 30 | +3/-0 | 78 | 100 | 25 | 1 | 5 | 0 | 749 (1.023) | yes |
| C-k6comp40 | 44 (+2) | 14 / 30 | +3/-1 | 82 | 104 | 24 | 1 | 5 | 0 | 826 (1.128) | yes |
| A-k4 | 44 (+2) | 14 / 30 | +2/-0 | 77 | 100 | 24 | 1 | 4 | 0 | 737 (1.007) | yes |
| A-comp40 | 43 (+1) | 15 / 28 | +1/-0 | 78 | 100 | 25 | 1 | 5 | 0 | 737 (1.007) | yes |
| A-k6 | 42 (+0) | 13 / 29 | +2/-2 | 82 | 105 | 24 | 1 | 5 | 0 | 785 (1.072) | yes |
| A-lead | 42 (+0) | 14 / 28 | +0/-0 | 78 | 100 | 24 | 1 | 4 | 0 | 762 (1.041) | yes |
| A-pool2000 | 42 (+0) | 14 / 28 | +0/-0 | 77 | 100 | 25 | 1 | 4 | 0 | 723 (0.988) | yes |
| base | 42 | 14 / 28 | — | 77 | 100 | 24 | 1 | 4 | 0 | 732 (1.0) | yes |
| A-k8 | 40 (-2) | 12 / 28 | +2/-4 | 83 | 106 | 24 | 1 | 5 | 0 | 863 (1.179) | no (ctx) |
| A-floor65 | 37 (-5) | 13 / 24 | +1/-6 | 66 | 95 | 24 | 1 | 4 | 3 | 710 (0.97) | no (health) |

## Top configs
1. B-k4comp40: +3 MAIN (0 lost), ST +1, TOPICS +1, 0 health losses, ctx 1.023x, 19 MAIN kept sets changed. Meets NIGHT-2026-10-24 step 0's "+3 facts under the guards" bar exactly.
2. C-k6comp40 (+2, one loss, ctx 1.128x), 3. A-k4 (+2, 0 lost, ctx 1.007x).

## Which knobs move MAIN
k (one k = 4 for every task, vs lookup 3 / other 4 / deep 6) and the compress floor 0.4 move MAIN by +1..+3; k 6/8 trade MAIN for ST (fact +5/+6) and context; floor 0.65 hurts (-5, 3 health losses); pool 2000 and the lead header do nothing on MAIN. Predictions: P1 hit, P2 hit (no single knob >= +6), P3 not testable (cap/pick cited from ARTCAP: MAIN -2..-3), P4 partly (TOPICS +1 at pool 2000, no context cost), P5 hit (k8 1.179x), P6 hit (best +3).

## Status
B-k4comp40 is a candidate, NOT in ENGINE-RC: the RETBENCH criterion has no safety-probe guard and no answer screen. Before adoption it needs (0 LLM) the 65 probe kept lists vs SEFIX-124 (<= 5 changed, 0 dose/number) and the Haiku screen on its changed MAIN answers (19 items, both orders; r4to picks the judge runs on 10-24). F8 survival stays 1/19 in every config: no retrieval knob fixes the follow-up referent.
