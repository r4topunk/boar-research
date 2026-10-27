# SEFIX F1b answer screen: call ledger (cap Haiku 300, Opus 0, paid 0, phone 0)
| time | what | Haiku calls | running total |
|---|---|---|---|
| 20:15-20:22 | generation 97 items on the mini (arm f1b-main-s42, one job, local llama-server) | 0 | 0 |
| 20:24-20:26 | F1b judge: changed vs ARM-G 64 ids (v01 33, cooking 13, money 18) x 2 orders | 128 | 128 |
| 20:26 | sensitivity: 2 items with the same kept titles but different chunk ids / prompt (lan-exp-004, lan-exp-005) x 2 orders | 4 | 132 |

Total 132 of 300; 0 retries; control rows (null-cal/control/pool-K1.json) and ARM-G rows reused (0 calls). Raw ledgers: ans-judge/F1B/calls.log, ans-judge/F1B2/calls.log.

## SEFIX-ALL answer screen (cap Haiku 150, Opus 0, paid 0, phone 0)
| time | what | Haiku calls | running total |
|---|---|---|---|
| 21:30-21:39 | generation 97 items on the mini (arm sefixall-main-s42, local llama-server) | 0 | 0 |
| 21:41-21:44 | judge: 43 changed vs ARM-G (v01 6, cooking 18, money 19) x 2 orders | 86 | 86 |

Total 86 of 150; 0 retries. Ledgers: ans-judge/ALL/calls.log.

## SEFIX-ALL Opus confirm (CV5 51; cap Opus 110, Haiku 0, paid 0, phone 0) - plan frozen before any call
Finding before the run: ALL text differs from the K3 control (mini K1) on 36 of the 51 ids (the 13-pack kit + merge changes the prompt; only 6 differ vs ARM-G), and 31 control / 38 ALL texts have no existing Opus judge.v1 row (v0.1 frame bd235bb9/568b3ece, seed 7) -> 66 units = 132 calls > 110. Pre-registered fit (outcome-blind): keep the 6 SEFIX-changed ids and every id with an Opus row on both arms; drop 3 identical-text ids with no row (hum-004, cry-009, rsn-004; they cancel in the delta) and 6 two-unit ids chosen by numpy default_rng(11) permutation among the non-SEFIX ones (trav-004, lan-exp-005, lan-exp-002, vit-cry-003, vit-hum-006, vit-hlt-003) -> n 42; judge 29 ALL units (opus/ids.ALL, ALL traces) + 22 control units (opus/ids.CTL, mini K1 traces) = 51 units = 102 calls. plan.json sha ab9fcf83.
| time | what | Opus calls | running total |
|---|---|---|---|
| 21:48-21:50 | ALL traces: 29 ids x 2 orders (opus/ids.ALL, 4 shards, wall 130 s) | 58 | 58 |
| 21:48-21:50 | control (mini K1) traces: 22 ids x 2 orders (opus/ids.CTL, 4 shards, wall 99 s) | 44 | 102 |

Total 102 of 110; 0 retries (shard logs: 4+4 shards, all rc 0; 58 + 44 rows ok, one judgeModel claude-opus-5-5). Haiku 0, paid 0, phone 0, generation 0. Raw: opus/{all,ctl}.judgments.jsonl, opus/*.log. Reuse: 20 control + 13 ALL units from existing identical-unit Opus rows (cv5_opus_pool); every reused unit checked by (id, sha256(text)).

## SEFIX-ALL seed 43 replicate (cap Haiku 200, Opus 0, paid 0, phone 0)
| time | what | Haiku calls | running total |
|---|---|---|---|
| 22:12-22:14 | ALL s43: v01 17 + cooking 13 + money 19 ids x 2 orders | 98 | 98 |
| 22:15-22:17 | control s43: v01 18 + cooking 14 + money 19 ids x 2 orders | 102 | 200 |

Total 200 of 200; 0 retries; generation 194 items on the mini, 0 LLM judge elsewhere. Ledgers: ans-judge/S43/{ALL,CTL}/calls.log.

## SEFIX-ALL Opus read, cooking/money units (cap Opus 60, Haiku 0, paid 0, phone 0, generation 0) - plan frozen before any call (opus-cm/plan.json sha f41b63bb)
Finding before the run: ALL text differs from the K1 control on 38 of the 40 cm units (not ~30); 21 control units already had an Opus judge.v1 row in the self-test frames (REVEAL-CENSUS K0 pass, identical text), 2 ALL units; 30 new units = 60 calls fit exactly. Rule (outcome-blind): the 20 newly delivered cm facts whose text differs first, then the rest by id (cooking-001, cooking-003); 16 differing units left unjudged.
| time | what (judge: shard_judge.sh model opus = judge.mjs --judge-model opus, judge.v1, both orders, seed 7, N 4) | Opus calls | running total |
|---|---|---|---|
| 22:29:15-22:29:28 | CTL qa-cooking-se: cooking-001, -003, -010, -019 (4 units x 2 orders) | 8 | 8 |
| 22:29:28-22:29:40 | CTL qa-money-se: money-002, -006, -010, -020 (4 units x 2 orders) | 8 | 16 |
| 22:29:40-22:30:18 | ALL qa-cooking-se: cooking-001, -003, -005, -006, -007, -010, -013, -015, -016, -017, -018, -019 (12 units x 2) | 24 | 40 |
| 22:30:18-22:31:08 | ALL qa-money-se: money-002, -003, -006, -007, -010, -012, -013, -016, -019, -020 (10 units x 2) | 20 | 60 |

Total 60 of 60; 0 retries (4 invocations, rc 0, 60 rows ok, one judgeModel claude-opus-5-5). Reuse: ctl 14 of 22 units from existing identical-text Opus rows, ALL 0 of 22 (checked by (id, sha256(text)) in the self-test frames refs 617f19ba/9cd5b186). Raw: opus-cm/{CTL,ALL}.<unit>.judgments.jsonl + .log, run.sh, status.txt. Aggregate: ans-tools/agg_opus_cm.py -> opus-cm.{json,md}.

## SEFIX-124 (F1+F2+F4, F3 off) answer screen (cap Haiku 200, Opus 0, paid 0, phone 0)
Plan (ans-tools/sanity_124.py, outcome-blind): 124 text byte-identical to SEFIX-ALL on 92/97 at both seeds, so only units without an existing judged row (cache keyed by (id, text)) were judged: 13 v0.1 ids at s43 for each arm (the 14 differing items SEFIX-ALL s43 had left unjudged, minus 1); s42 and all cooking/money units fully cached (0 calls).
| time | what | Haiku calls | running total |
|---|---|---|---|
| 22:42-22:53 | generation 2 x 97 items on the mini (sefix124-main-s42, -s43, parallel, gen1/gen2) | 0 | 0 |
| 22:54 | judge s43 SEFIX-124: 13 v0.1 ids x 2 orders (ans-judge/S124/43.X) | 26 | 26 |
| 22:54 | judge s43 K3 control: 13 v0.1 ids x 2 orders (ans-judge/S124/43.C) | 26 | 52 |
Total 52 of 200; 0 retries. Ledgers: ans-judge/S124/{43.X,43.C}/calls.log.

## F3B (safe replacement for F3; cap Haiku 200, Opus 0, paid 0, phone 0)
| time | what | Haiku calls | running total |
|---|---|---|---|
| 23:05-23:09 | generation 2 x 65 probes on the mini (f3b-A-s42, f3b-B-s42, gen1/gen2), no judge | 0 | 0 |
| 23:10-23:17 | MAIN 97 replays on the MacBook (F3bOFF identity, F3bA), 0 LLM | 0 | 0 |
Total 0 of 200: A fails the frozen delivery gate (chunk-level 43 < 45), B fails the safety rule, so no answer screen was run (answers-sefix-f3b.* not produced). Ledger: f3b/runs/.
