# B1-LAYER-SPLICE (2026-10-21): SUPPORTED as a projection. Our 8 facts-table answers spliced into RC1 lift U 0.143 -> 0.248 (Opus, CV5 51)

**A 0-call counterfactual, not a measurement.** It assumes the app would route the same 8 questions to the same deterministic texts.
Criterion B1-SPLICE-criterion.md (sha f5f0bfff...), committed ae243d90 before any spliced number. Tool tools/b1_splice.py.
Output aggregates/B1-LAYER-SPLICE.json. Cost: 0 LLM, **0 new judge calls**, 0 phone.

## Judgments reused (no new call)
- RC1 base: a1/judgments/rc1-shipped.opus.judgments.jsonl (sha bf6bab00..., 102 Opus judge.v1 rows, both orders, seed 7; rows.jsonl df26ed79...).
- Layer answers: CV5 rung L3_4B_phone_cut7 (Pixel 8a cut 7, traces sha a9cb9653...). Their judgments are the Opus judge.v1 rows in
  ruler/cv5-ladder/out/L3_4B_phone_cut7.judgments.jsonl (sha f90121b9...), both orders, seed 7, created 2026-10-21 08:25-08:27 UTC.
- Layer check: 8/8 ids have outputTokens 0 and an answer:facts-* reason code (population, height, winner, area, host, depth, dates,
  electricity). All 8 texts are byte-identical across the L1 1.7B, L2 Gemma and L3 4B rungs, so they are model-independent.

## Result (item-cluster bootstrap B 2000, seed 11, paired)
| row | U floor-adj (CI) | raw | correct / CE per 100 | win/loss |
|---|---|---|---|---|
| RC1 shipped (measured) | 0.143 (0.103-0.188) | 0.316 | 2.0 / 68.6 | 0/51 |
| RC1 + 8 layer answers (projection) | **0.248 (0.167-0.335)** | 0.401 | 17.6 / 58.8 | 1/47 |
| dU spliced - RC1 | **+0.106 (+0.040...+0.183)** | | +15.6 / **-9.8 (-17.6...-2.0)** | |
| sensitivity: 1.5B closed-book desktop + layers | 0.320 vs 0.261, dU +0.059 (+0.010...+0.122) | | CE -3.9 | |
U_D2S equals U (no decline detected). Per item, RC1 scored s 1.0-2.8 (correctness <= 2 on all 8); the layer answers score s 3.3-5.0 (correctness 5 on all 8).

## Verdict vs the frozen rule
n_layer 8 >= 5; dU +0.106 >= +0.04 with CI low +0.040 > 0; d CE -9.8 <= -8 -> **SUPPORTED**. Not KILL (dU >= +0.02).
The lift is about 2.6x the hypothesis' +0.04 bar because RC1 is so weak on these items (Detailed 1.5B, KB only, CE on 6/8).
On the closed-book 1.5B rung the same splice gives +0.059, matching the +0.04...+0.06 'any model' prior.

## Sentence for NOTE-1 section 3 / page (projection wording)
"If the app answered the 8 facts-table questions in our 51-question dev set with our engine's deterministic answers, its score would move
from 0.14 to about 0.25 (Opus, a projection from existing judgments of those answers, not a new measurement); on a closed-book 1.5B the
same swap is worth about +0.06." Ordering consequence: the layers port keeps 'largest measured per-item lever' for the shipped app, and
all 8 of the CV5 layer items are the facts table alone (no arithmetic, distance or cards), so the facts table is the pre-freeze candidate.

## Limits
- n 8 changed items of 51; one run, one seed, dev ids. The spliced items carry L3's own reference scores (r 4.5-5.0) as judged with that answer.
- Assumes identical routing and texts on the shipped app; the RC1 Detailed persona would not touch a 0-token layer answer.
- 8 is the CV5 layer count; the X6 attribution saw 11/57 on its frame. ROUTING.md row 1 lists the same 8 ids.
