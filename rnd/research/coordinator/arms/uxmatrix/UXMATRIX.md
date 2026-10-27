# UXMATRIX (U1, 2026-10-23): app mode x pack state -> what the user receives

**Leitura para o r4to (PT-BR)**
- Succinct, pack ON: 35 % certo (28 % com a fonte certa mostrada); pack OFF: 28 % certo, quase todo de memória e com a linha "Not found ... may be wrong" (75 % das respostas OFF levam o aviso).
- Detailed, pack ON: 27 % certo (18 % com fonte); OFF: 17 % certo e mais erro sem aviso (15 % vs 7 % no Succinct). Detailed perde do Succinct nos dois estados.
- Quando falta o conteúdo, o modelo nunca diz "não sei" sozinho: os 12 % de "honest unknown" são todos recusas do motor (6 falsos alarmes de saúde em culinária + 1 rota de places), iguais em todo modo e estado. O usuário recebe aviso + resposta de memória.
- Com o pack ON o aviso some em mais respostas e parte delas sai errada sem aviso (WC 22 % ON vs 7 % OFF no Succinct): a fonte certa aparece em só 50 % das respostas ON, e o 1.7B lê certo 17 de 30 vezes quando ela aparece.
- Padrões recomendados: Succinct continua o padrão; Detailed não vira padrão; Deep Research segue escondido (DEEPMODE; não rodado aqui). Pela regra congelada nenhuma superfície de honestidade muda (WC OFF 7 % < 25 %, recusa indevida 0 %), mas os 6 falsos alarmes de saúde escondem conteúdo que o pack tem.
- Ressalvas: 1 seed, rótulos Haiku (lidos 8 à mão: 6 ok, 1 errado, 1 limítrofe), gêmeo desktop (Succinct no MacBook, Detailed no mini), itens de saúde AI-reviewed, not clinically reviewed.

Criterion: UXMATRIX-criterion.md, sha256 0cc3ca207707026212ad5210e05e438c7bb6298834f960d53e2f6eb9f445c922 (frozen before any generation or label call). Haiku 309 of 400 (A 208, B 88, C 13; 0 failures; three-way 0, single 0), Opus 0, paid 0, phone 0. Ledger CALLS.md.

## Deviations from the frozen criterion
- **Deep arms not run (DEEPMODE covers it).** Coordinator scope cut at 12:37: the mini Deep job was killed after 9 of 11 OFF groups (33 items, ON not generated), its slot released and tree removed; those partial traces are not used. P4 and the Deep rows are therefore not measured.
- Detailed ran on the mini (M4), not the MacBook: after the cut the mini was free and faster; the whole mode (ON and OFF) ran there (two jobs, same tree recipe, answer.ts 3ef9335c on both hosts), so one host per mode holds; 1 MacBook Detailed item was discarded. Succinct ran on the MacBook (M1 Pro) after the 5-item kept-list identity check (5/5 identical vs the mini sefix124 traces). Mode-vs-mode comparisons mix hosts.
- gen-nopack is 5 items, not the 15 of the brief (written in the criterion before the run: only 5 keyed v0.1 items have no fact in any K13 pack).

## Commands
```
python3 -I tools/deliv_packs.py deliv_packs.json; python3 -I tools/select.py; python3 -I tools/mk_req.py
tools/run_local.sh succinct                          # MacBook: local_gen.sh per group (local detector :8094, server wrapper)
tools/run_mini.sh detailed on on start; tools/run_mini.sh detailed off 'off-*' start   # mini, mini_gen_multi.sh, slot lock; then ... fetch
python3 -I tools/prep.py succinct detailed; node tools/label.mjs judge/units.json judge/labels.jsonl; python3 -I tools/agg.py
```
Items (items.json): cm 40 (OFF = K13 minus qa-cooking-se / qa-money-se), gen-delivered 15 (OFF = K13 minus every pack holding a kept fact chunk), gen-nopack 5 (ON = OFF). 230 generations (115 per mode), 208 label units (identical ON/OFF answers share a unit).

## THE MATRIX (outcome shares; CWS correct with source, CFM correct from memory, HU honest unknown, RW refused wrongly, WW wrong but warned, WC wrong confident)

### all
| mode | state | n | CWS | CFM | HU | RW | WW | WC |
|---|---|---|---|---|---|---|---|---|
| succinct | ON | 60 | 0.28 | 0.07 | 0.12 | 0.00 | 0.32 | 0.22 |
| succinct | OFF | 60 | 0.03 | 0.25 | 0.12 | 0.00 | 0.53 | 0.07 |
| detailed | ON | 60 | 0.18 | 0.08 | 0.12 | 0.00 | 0.40 | 0.22 |
| detailed | OFF | 60 | 0.03 | 0.13 | 0.12 | 0.00 | 0.57 | 0.15 |

### cm
| mode | state | n | CWS | CFM | HU | RW | WW | WC |
|---|---|---|---|---|---|---|---|---|
| succinct | ON | 40 | 0.28 | 0.05 | 0.17 | 0.00 | 0.35 | 0.15 |
| succinct | OFF | 40 | 0.00 | 0.23 | 0.17 | 0.00 | 0.55 | 0.05 |
| detailed | ON | 40 | 0.15 | 0.07 | 0.17 | 0.00 | 0.38 | 0.23 |
| detailed | OFF | 40 | 0.00 | 0.10 | 0.17 | 0.00 | 0.60 | 0.12 |

### gen-delivered
| mode | state | n | CWS | CFM | HU | RW | WW | WC |
|---|---|---|---|---|---|---|---|---|
| succinct | ON | 15 | 0.40 | 0.00 | 0.00 | 0.00 | 0.13 | 0.47 |
| succinct | OFF | 15 | 0.13 | 0.27 | 0.00 | 0.00 | 0.47 | 0.13 |
| detailed | ON | 15 | 0.33 | 0.00 | 0.00 | 0.00 | 0.40 | 0.27 |
| detailed | OFF | 15 | 0.13 | 0.13 | 0.00 | 0.00 | 0.47 | 0.27 |

### gen-nopack
| mode | state | n | CWS | CFM | HU | RW | WW | WC |
|---|---|---|---|---|---|---|---|---|
| succinct | ON | 5 | 0.00 | 0.40 | 0.00 | 0.00 | 0.60 | 0.00 |
| succinct | OFF | 5 | 0.00 | 0.40 | 0.00 | 0.00 | 0.60 | 0.00 |
| detailed | ON | 5 | 0.00 | 0.40 | 0.00 | 0.00 | 0.60 | 0.00 |
| detailed | OFF | 5 | 0.00 | 0.40 | 0.00 | 0.00 | 0.60 | 0.00 |

### UX surface (all items)
| mode | state | n | Not-found warning line | health decline | 0 sources | sources shown (mean) | any citation | out tokens (mean) | total ms p50 | host |
|---|---|---|---|---|---|---|---|---|---|---|
| succinct | ON | 60 | 0.45 | 0.10 | 0.15 | 4.6 | 0.42 | 42 | 9810 | Apple M1 Pro cpu x4  |
| succinct | OFF | 60 | 0.75 | 0.10 | 0.23 | 2.9 | 0.07 | 39 | 6475 | Apple M1 Pro cpu x4  |
| detailed | ON | 60 | 0.48 | 0.10 | 0.15 | 4.6 | 0.38 | 378 | 18086 | Apple M4 cpu x4 (dar |
| detailed | OFF | 60 | 0.63 | 0.10 | 0.23 | 2.9 | 0.18 | 371 | 16567 | Apple M4 cpu x4 (dar |

### Deltas
| comparison | n | CWS | correct | WC | HU |
|---|---|---|---|---|---|
| succinct|all-with-off | 55 | +0.273 (+0.14..+0.40) | +0.073 (-0.06..+0.20) | +0.164 (+0.02..+0.31) | +0.000 (+0.00..+0.00) |
| succinct|cm | 40 | +0.275 (+0.15..+0.42) | +0.100 (+0.00..+0.23) | +0.100 (-0.03..+0.25) | +0.000 (+0.00..+0.00) |
| succinct|gen-delivered | 15 | +0.267 (+0.00..+0.53) | +0.000 (-0.33..+0.27) | +0.333 (+0.00..+0.67) | +0.000 (+0.00..+0.00) |
| detailed|all-with-off | 55 | +0.164 (+0.06..+0.27) | +0.109 (+0.00..+0.22) | +0.073 (-0.06..+0.22) | +0.000 (+0.00..+0.00) |
| detailed|cm | 40 | +0.150 (+0.05..+0.28) | +0.125 (+0.00..+0.25) | +0.100 (-0.07..+0.28) | +0.000 (+0.00..+0.00) |
| detailed|gen-delivered | 15 | +0.200 (-0.07..+0.47) | +0.067 (-0.13..+0.27) | +0.000 (-0.20..+0.20) | +0.000 (+0.00..+0.00) |
| detailed-succinct|on | 60 | -0.100 (-0.20..+0.00) | -0.083 (-0.18..+0.03) | +0.000 (-0.15..+0.15) | - |
| detailed-succinct|off | 60 | +0.000 (+0.00..+0.00) | -0.117 (-0.23..+0.00) | +0.083 (+0.02..+0.15) | - |

flags {}; rows 240

Extra reads (aggregates/reading.json): source shown that holds the answer: Succinct ON 30/60, Detailed ON 28/60, OFF 3/60 both. Correct when such a source is shown: Succinct 17/30, Detailed 11/28. Correct among answers carrying the Not-found warning: Succinct ON 8/27, OFF 13/45; Detailed ON 5/29, OFF 4/38.

## OFF-state story per mode
- **Succinct:** the user gets the Not-found warning on 75 % of answers; 25 % are right from memory (cooking/money general knowledge), 53 % are wrong but warned, 7 % wrong without a warning. ON moves +0.27 into CWS (CI +0.14..+0.40) but only +0.07 in total correct (CI -0.06..+0.20): much of the pack's effect is turning warned memory answers into sourced ones, and WC rises +0.16 (CI +0.02..+0.31) because answers that drop the warning are not all right.
- **Detailed:** warning on 63 %, right from memory 13 %, WC 15 % (Succinct 7 %, paired +0.08, CI +0.02..+0.15). ON: CWS +0.16 (+0.06..+0.27), correct +0.11 (+0.00..+0.22). Detailed - Succinct correct: ON -0.08 (-0.18..+0.03), OFF -0.12 (-0.23..0.00).
- **Deep Research:** not run (deviation above).
- HONEST_UNKNOWN (12 % everywhere) = 7 engine routing declines that fire before generation in every mode and state: 6 health-strict declines on cooking/money items (the known detector misfires; the pack held the answer, but no source is shown, so the protocol cannot call them REFUSED_WRONGLY) and 1 "places pack is not installed" route (cooking-002). The generator itself never produced an "I do not have this" answer.

## Predictions
| # | prediction | result |
|---|---|---|
| P1 | ON raises CWS in every mode, most in Succinct | HIT on the two modes run (Succinct +0.27, Detailed +0.16); Deep not run |
| P2 | OFF WC higher in Detailed and Deep than Succinct | HIT for Detailed (0.15 vs 0.07); Deep not run |
| P3 | HU the most common OFF outcome only in Succinct | MISS: in every OFF cell the most common outcome is WRONG_WARNED (Succinct 0.53, Detailed 0.57); HU 0.12 everywhere |
| P4 | Deep never improves OFF over Succinct | NOT MEASURED |

## Product defaults (frozen rules)
- Default mode: stays **Succinct** (Detailed ON correct 0.27 < Succinct 0.35, and OFF WC higher).
- Deep Research: stays **hidden** (not measured here; DEEPMODE U 0.174 vs Succinct 0.263).
- OFF honesty surface: **no change by rule** (default-mode OFF WC 0.07 < 0.25; RW with pack ON 0.00 < 0.10). Outside the rule: the 6 health misfires on cooking/money hide content the pack holds (W98 / DETECTOR-HN line), and ON answers without the warning are wrong 50 % of the time in Succinct (13 of 26 correct), so the absence of the warning is not a correctness signal.

## Caveats
One seed (42); Haiku 5.5-low labels, N 1 with borderline re-checks (hand read of 8 Succinct ON WC labels on gen-delivered: 6 fair, 1 wrong (lan-ref-003 is correct), 1 borderline (lan-exp-007, 50,000 vs 56,000 people)), so WC is if anything overstated; desktop twin on two CPU hosts; cm items written from those packs (install value by construction); gen-delivered n 15, gen-nopack n 5; health items AI-reviewed, not clinically reviewed. The local detector the MacBook run started on :8094 was left running (other sessions' MacBook runs started after it may use it).

Files: UXMATRIX-criterion.md (+ .sha256), items.json, deliv_packs.json, in/, tools/ (deliv_packs.py, select.py, mk_req.py, local_gen.sh, run_local.sh, mini_gen_multi.sh, run_mini.sh, run_mini_deep.sh, prep.py, label.mjs, agg.py), aggregates/ (uxmatrix.json, matrix.md, reading.json), CALLS.md; gen/ and judge/ gitignored.
