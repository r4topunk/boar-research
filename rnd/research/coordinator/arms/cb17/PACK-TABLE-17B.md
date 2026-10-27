# PACK-TABLE-17B (2026-10-21): the 1.7B with vs without added knowledge, per item (MAIN 97 dev)

Criterion `CB17-criterion.md` (sha e2723627…, rnd b44e7eef, frozen before generation). Data `aggregates/pack_table_17b.{json,csv}` (tools/cb17_table.py, 0 calls).
New this run: the closed-book 1.7B arm (CB), 97 generations on the Mac mini (seed 42). Calls: **Haiku 291** (194 judge.v1-low + 97 DECLINE2STAGE stage 1; cap 900), **Opus 58** (29 new units; 22 identical units reused; cap 110), 0 paid.

## What "closed-book" means here
- Same engine, prompt and succinct persona as the mini K0/K1 controls. Two changes: no pack installed (kit = []), and `retrieve()` returns nothing (patch tools/cb17-noretrieval.patch).
- So the prompt never carries a source: no packs and no bundled knowledge base.
- Deterministic layers are kept as they ship: the FACTS table, calculators, travel distance, emergency numbers + detector, condition/first-aid cards, the health-from-memory refusal, phrase decline.
- The answer then shows with the warning line "From the model's memory, may be wrong" (OFF5).
- On the 97: 46 answers are warned memory answers, 29 are unwarned chat-type memory answers, 10 are engine health refusals, 10 come from FACTS/calculators, and 2 are other.

## Levels (U = sum(s−1)/sum(r−1), CV5 metric; item bootstrap B 2000, seed 11)
| set | judge | CB closed-book | K0 claim kit | K1 + simplewiki | K3 + factbook/health (MacBook host) |
|---|---|---|---|---|---|
| CV5 51 | **Opus judge.v1** | **0.337 (0.256–0.425)** | 0.351 (0.279–0.437) | 20/51 rows only | 30/51 rows only |
| v0.1 57 | Opus judge.v1 | 0.377 (0.299–0.460) | 0.390 (0.316–0.469) | 26/57 | 36/57 |
| MAIN 97 | Haiku 5.5-low | 0.248 (0.201–0.292) | 0.243 (0.200–0.288) | 0.249 (0.203–0.295) | 0.229 (0.183–0.274) |
| v0.1 57 | Haiku 5.5-low | 0.294 | 0.294 | 0.305 | 0.286 |
| cooking+money 40 | Haiku 5.5-low | 0.177 | 0.167 | 0.165 | 0.143 |
Reference rungs on the CV5 51 (Opus): closed-book Qwen2.5-1.5B 0.261, 4B cut 7 phone 0.460.

**Prediction (frozen): BETWEEN.** The CB Opus U of 0.337 lies between the 1.5B (0.261) and K0 (0.351). K0 − CB has CI low < 0, so under Opus, packs are **not separable** from no packs on these items.

## Paired deltas vs closed-book (win/tie/loss per item, tie = |Δs| ≤ 0.25)
| pair | set | judge | ΔU (95 % CI) | W/T/L | texts changed | ΔU, identical texts reuse the arm's row (sensitivity) |
|---|---|---|---|---|---|---|
| K0 − CB | CV5 51 | **Opus** | **+0.015 (−0.035…+0.056)** | 13/33/5 | 31 | same (Opus reuses identical units) |
| K0 − CB | v0.1 57 | Opus | +0.013 (−0.031…+0.051) | 13/39/5 | 31 | same |
| K0 − CB | MAIN 97 | Haiku | −0.005 (−0.027…+0.017) | 16/65/16 | 34 | +0.009 (−0.010…+0.027), 12/82/3 |
| K1 − CB | MAIN 97 | Haiku | +0.001 (−0.024…+0.026) | 18/59/20 | 63 | +0.003 (−0.022…+0.027), 17/64/16 |
| K3 − CB | MAIN 97 | Haiku (K3 MacBook host) | −0.019 (−0.051…+0.013) | 19/51/27 | 77 | n/a (cross-host) |
| K1 − K0 | MAIN 97 | Haiku | +0.006 (−0.015…+0.026) | 19/59/19 | 61 | |
- Haiku judge noise: on the 63 MAIN texts that are byte-identical between CB and K0, re-judging moved the per-item s by 0.175 on average, and the U gap on those texts was −0.021.
- That is why the sensitivity column is the cleaner read of K0 − CB under Haiku. Opus has no retest noise in these columns because identical units reuse one row.
- Confident errors (corr ≤ 1.5, not declined): Opus on the 51, CB 13 vs K0 8. Haiku on MAIN 97, CB 29, K0 23, K1 24, K3 24. These are counts only, with no CI.

## Splits
| split | judge | n | ΔU K0 − CB (CI), W/T/L | ΔU K1 − CB (CI), W/T/L |
|---|---|---|---|---|
| fact present in the K1 kept context: yes | Haiku MAIN | 22 | +0.007 (−0.054…+0.068), 6/12/4 | +0.008 (−0.064…+0.080), 8/8/6 |
| fact present in K1 context: no | Haiku MAIN | 70 | −0.009 (−0.032…+0.013), 9/50/11 | −0.000 (−0.028…+0.026), 10/47/13 |
| fact present: yes | Opus v0.1 | 22 | +0.027 (−0.057…+0.099), 7/12/3 | (K1 Opus rows incomplete) |
| fact present: no | Opus v0.1 | 30 | +0.001 (−0.054…+0.047), 5/23/2 | |
| in-pack (INPACK tag) | Haiku MAIN | 72 | +0.007 (−0.012…+0.029), 11/52/9 | +0.010 (−0.015…+0.038), 13/46/13 |
| off-pack | Haiku MAIN | 25 | −0.034 (−0.097…+0.022), 5/13/7 | −0.023 (−0.095…+0.039), 5/13/7 |
| in-pack | **Opus v0.1** | 32 | **+0.048 (+0.007…+0.091), 10/19/3** | |
| off-pack | Opus v0.1 | 25 | −0.031 (−0.117…+0.032), 3/20/2 | |
| RAG-FUNNEL K1 S1 (fact in no installed pack) | Haiku MAIN | 45 | −0.010 | −0.003 (−0.034…+0.027) |
| S2 in a pack, not retrieved (mostly deterministic answers) | Haiku | 8 | −0.010 | +0.039 (−0.013…+0.130) |
| S3 retrieved, dropped at keep | Haiku | 17 | −0.002 | −0.006 (−0.086…+0.060) |
| S4 kept, answer wrong | Haiku | 17 | +0.012 | −0.013 (−0.104…+0.074) |
| S5 kept and used | Haiku | 5 | −0.008 | +0.075 (−0.025…+0.175) |
The in-pack tag counts health/first-aid/country items as in-pack, but K0 does not carry those packs. The in-pack splits are post-hoc readings with no rule riding on them.

## Reading (for the page; judge family named)
1. On 97 casual dev questions, adding knowledge packs does not measurably lift the 1.7B. Under Opus (51 items) the claim kit adds +0.015 U (CI −0.035…+0.056). Under Haiku the three pack sets sit between −0.019 and +0.009, and every CI straddles 0.
2. Mostly the packs never reach the answer: 63/97 claim-kit answers are word-for-word the closed-book answer (nothing relevant kept), and the key fact is in the simplewiki context for only 22 of 92 keyed items.
3. Where packs help, they help on the topics they cover. On v0.1 items tagged in-pack, Opus gives +0.048 (CI +0.007…+0.091; 10 better, 3 worse). Where the fact is kept and used (n 5), Haiku gives +0.075 (CI straddles).
4. Where they do nothing: cooking and money questions, where no pack is installed and 37/40 answers are identical, and the 70 items whose fact never reaches the context (Δ ≈ 0.000).
5. Where they hurt: off-topic sources crowd the prompt. Off-pack items show −0.03 under both judges, and the largest kit (K3) shows −0.019 under Haiku (all CIs straddle 0; K3 was run on a different host).
6. What packs do buy is fewer confident wrong answers (Opus 13 → 8 of 51) and source-backed text. The ruler cannot separate the scores, which puts the 1.7B with or without packs between a closed-book 1.5B (0.261) and the 4B (0.460) under Opus.

## Limits
- One seed. Dev items only (v0.1 public + 2 SE self-test sets).
- K1/K3 Opus rows cover only 20–30 of the 51, so Opus pairs exist only for K0.
- The K3 column is MacBook-generated; mini-vs-MacBook text differs on about 70 % of rows with identical contexts (MINI-BASELINE).
- DECLINE2STAGE is report-only, since it failed its own bar: U_D2S CB = 0.333 (Opus 51) and 0.242 (Haiku 97), flagging 8 not-attempted answers (7 engine refusals + dng-005).
- Deviation: the shard_judge preflight was run without PREFLIGHT_CRITERION, because the criterion's budget line is not in the "## Budget / calls_cap:" form the preflight parses. The caps were enforced by tools/judge_cb17.sh and the call ledger (runs/logs/calls.log).

## Per item
Legend: · = in the CV5 51. H = Haiku 5.5-low s, O = Opus judge.v1 s (1–5 scale, mean of 3 dims × 2 orders). K3* = MacBook host. Δ = arm − CB. Flags: W warned, D declined/refusal. Blank Opus cell = no Opus row on that exact text.

| id | set | tag | in-pack | fact in K1 ctx | funnel K1 | H CB | H K0 | H K1 | H K3* | O CB | O K0 | O K1 | ΔH K1−CB | ΔH K0−CB | ΔO K0−CB | flags CB/K0/K1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| vit-hum-001 · | v0.1 | humanities | off | no | S1 | 2.00 | 1.50 | 1.50 | 1.33 | 2.00 | 2.00 |  | -0.50 | -0.50 | +0.00 | W/W/W |
| vit-hum-002 · | v0.1 | humanities | off | no | S3 | 1.33 | 1.33 | 1.33 | 1.17 | 1.33 | 1.33 |  | +0.00 | +0.00 | +0.00 | W/W/W |
| vit-hum-003 · | v0.1 | humanities | off | no | S3 | 1.33 | 1.33 | 1.33 | 1.33 | 1.83 | 1.83 | 1.83 | +0.00 | +0.00 | +0.00 | W/W/W |
| vit-hum-004 · | v0.1 | humanities | off | yes | S4 | 1.00 | 1.00 | 1.00 | 1.17 | 1.00 | 1.00 |  | +0.00 | +0.00 | +0.00 | W/W/- |
| vit-hum-005 · | v0.1 | humanities | off | no | S3 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |  | +0.00 | +0.00 | +0.00 | -/W/W |
| vit-hum-006 · | v0.1 | humanities | off | no | S1 | 1.67 | 1.67 | 1.83 | 1.33 | 2.33 | 2.33 |  | +0.17 | +0.00 | +0.00 | -/-/W |
| lan-exp-001 · | v0.1 | country | in | yes | S4 | 2.50 | 2.67 | 2.67 | 2.33 | 2.33 | 3.33 |  | +0.17 | +0.17 | +1.00 | -/-/- |
| lan-exp-002 · | v0.1 | country | in | yes | S4 | 2.83 | 2.83 | 2.17 | 3.00 | 3.17 | 3.17 |  | -0.67 | +0.00 | +0.00 | -/-/W |
| lan-rsn-001 · | v0.1 | place-other | off | yes | S4 | 1.17 | 1.67 | 1.00 | 2.17 | 1.33 | 2.00 | 1.50 | -0.17 | +0.50 | +0.67 | W/W/W |
| lan-cmp-001 · | v0.1 | country | in | no | S2 | 2.67 | 2.83 | 2.50 | 3.00 | 4.33 | 4.33 | 4.33 | -0.17 | +0.17 | +0.00 | -/-/- |
| lan-cmp-002 · | v0.1 | nature | off | no | S3 | 1.67 | 2.17 | 2.17 | 2.33 | 2.00 | 2.00 | 2.67 | +0.50 | +0.50 | +0.00 | W/-/- |
| lan-rsn-002 · | v0.1 | place-other | off | no | S2 | 3.83 | 3.83 | 4.00 | 3.67 | 5.00 | 5.00 | 5.00 | +0.17 | +0.00 | +0.00 | -/-/- |
| lan-ref-001 · | v0.1 | history-culture | off | no | S2 | 3.00 | 2.67 | 2.83 | 2.67 | 5.00 | 5.00 | 5.00 | -0.17 | -0.33 | +0.00 | -/-/- |
| lan-hlt-001 · | v0.1 | health | in | yes | S4 | 1.50 | 1.50 | 1.83 | 1.50 | 1.67 | 1.67 |  | +0.33 | +0.00 | +0.00 | W/W/W |
| lan-hlt-002 · | v0.1 | health | in | no | S3 | 2.67 | 2.50 | 2.17 | 3.00 | 2.83 | 2.83 | 2.67 | -0.50 | -0.17 | +0.00 | W/W/- |
| lan-hlt-003 · | v0.1 | health | in | yes | S5 | 2.67 | 2.33 | 2.33 | 2.17 | 2.83 | 2.83 | 3.00 | -0.33 | -0.33 | +0.00 | W/W/W |
| vit-trv-003 · | v0.1 | travel | in | yes | S4 | 1.00 | 1.00 | 1.00 | 1.17 | 1.00 | 1.00 |  | +0.00 | +0.00 | +0.00 | W/W/W |
| vit-trv-004 | v0.1 | travel | in | no | S1 | 3.67 | 4.17 | 3.83 | 3.67 | 4.17 | 4.17 | 4.17 | +0.17 | +0.50 | +0.00 | -/-/- |
| vit-cry-001 · | v0.1 | crypto | in | no | S3 | 1.00 | 2.00 | 1.33 | 1.33 | 1.00 | 2.00 |  | +0.33 | +1.00 | +1.00 | W/W/W |
| vit-cry-002 · | v0.1 | crypto | in | yes | S4 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |  | +0.00 | +0.00 | +0.00 | W/W/W |
| vit-cry-003 · | v0.1 | crypto | in | yes | S4 | 1.33 | 1.33 | 1.17 | 1.33 | 1.67 | 1.33 |  | -0.17 | +0.00 | -0.33 | -/W/W |
| vit-cry-004 · | v0.1 | crypto | in | yes | S4 | 1.17 | 1.33 | 1.33 | 2.00 | 1.33 | 2.33 |  | +0.17 | +0.17 | +1.00 | -/-/W |
| vit-cry-005 · | v0.1 | crypto | in | no | S2 | 1.00 | 1.00 | 1.17 | 1.00 | 1.00 | 1.17 |  | +0.17 | +0.00 | +0.17 | W/W/W |
| vit-cry-006 · | v0.1 | crypto | in | yes | S4 | 1.00 | 1.00 | 1.50 | 1.67 | 1.00 | 1.33 | 1.33 | +0.50 | +0.00 | +0.33 | W/W/- |
| vit-cry-007 · | v0.1 | crypto | in | no | S3 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | +0.00 | +0.00 | +0.00 | W/W/- |
| vit-cry-008 · | v0.1 | crypto | in | yes | S4 | 1.00 | 2.33 | 2.33 | 2.17 | 1.00 | 2.17 |  | +1.33 | +1.33 | +1.17 | W/-/- |
| vit-cry-009 · | v0.1 | crypto | in | no | S2 | 1.00 | 1.17 | 1.33 | 1.00 | 1.00 | 1.33 |  | +0.33 | +0.17 | +0.33 | -/-/- |
| vit-cry-010 · | v0.1 | crypto | in | no | S3 | 1.33 | 1.17 | 1.50 | 1.33 | 1.67 | 2.67 |  | +0.17 | -0.17 | +1.00 | W/W/W |
| vit-cry-011 · | v0.1 | crypto | in | yes | S4 | 1.00 | 1.33 | 1.33 | 1.67 | 1.33 | 1.83 |  | +0.33 | +0.33 | +0.50 | W/-/- |
| vit-sci-001 · | v0.1 | science-tech | off | no | S3 | 2.33 | 1.67 | 2.00 | 1.50 | 2.33 | 2.33 | 2.33 | -0.33 | -0.67 | +0.00 | W/W/W |
| vit-sci-002 · | v0.1 | country | in | no | S1 | 1.00 | 1.33 | 2.17 | 1.00 | 1.00 | 1.83 |  | +1.17 | +0.33 | +0.83 | W/W/W |
| vit-sci-003 | v0.1 | science-tech | off | no | S1 | 3.83 | 3.67 | 3.83 | 3.67 | 4.33 | 4.33 | 4.33 | +0.00 | -0.17 | +0.00 | -/-/- |
| vit-hlt-001 | v0.1 | firstaid | in | no | S3 | 3.00 | 3.00 | 3.00 | 3.17 | 3.33 | 3.33 | 3.33 | +0.00 | +0.00 | +0.00 | -/-/- |
| vit-hlt-002 | v0.1 | firstaid | in | no | S3 | 3.50 | 3.67 | 3.50 | 3.50 | 4.17 | 4.17 | 4.17 | +0.00 | +0.17 | +0.00 | -/-/- |
| vit-hlt-003 · | v0.1 | health | in | no | S3 | 1.33 | 1.67 | 1.33 | 1.33 | 1.83 | 1.67 |  | +0.00 | +0.33 | -0.17 | W/-/W |
| lan-ref-002 · | v0.1 | history-culture | off | yes | S5 | 2.67 | 3.00 | 3.33 | 3.33 | 3.00 | 4.00 | 4.00 | +0.67 | +0.33 | +1.00 | W/-/- |
| lan-ref-003 · | v0.1 | history-culture | off | yes | S4 | 2.67 | 2.00 | 2.17 | 2.33 | 3.33 | 3.33 |  | -0.50 | -0.67 | +0.00 | W/W/- |
| lan-rsn-003 · | v0.1 | nature | off | yes | S4 | 3.00 | 1.33 | 1.17 | 1.00 | 3.83 | 1.33 |  | -1.83 | -1.67 | -2.50 | -/-/W |
| lan-cmp-003 · | v0.1 | country | in | no | S3 | 2.67 | 2.67 | 3.67 | 1.00 | 3.33 | 2.33 |  | +1.00 | -0.00 | -1.00 | W/W/- |
| lan-rsn-004 · | v0.1 | history-culture | off | yes | S4 | 1.83 | 2.00 | 1.17 | 1.00 | 2.00 | 2.00 |  | -0.67 | +0.17 | +0.00 | -/-/W |
| lan-ref-004 · | v0.1 | country | in | no | S1 | 3.67 | 3.33 | 3.50 | 3.00 | 4.83 | 4.83 | 4.83 | -0.17 | -0.33 | +0.00 | -/-/- |
| lan-exp-003 · | v0.1 | country | in | yes | S5 | 3.50 | 3.00 | 3.33 | 3.50 | 3.67 | 3.67 |  | -0.17 | -0.50 | +0.00 | -/-/- |
| lan-exp-004 · | v0.1 | place-other | off | yes | S5 | 1.83 | 1.67 | 2.67 | 2.67 | 2.50 | 2.33 |  | +0.83 | -0.17 | -0.17 | W/W/- |
| lan-exp-005 · | v0.1 | place-other | off | yes | S4 | 2.17 | 2.67 | 1.83 | 2.17 | 2.67 | 2.50 |  | -0.33 | +0.50 | -0.17 | W/-/- |
| lan-exp-006 · | v0.1 | place-other | off | no | S2 | 2.67 | 2.67 | 2.67 | 2.67 | 3.33 | 3.33 | 3.33 | +0.00 | +0.00 | +0.00 | -/-/- |
| lan-cmp-004 · | v0.1 | nature | off | no | S3 | 1.00 | 1.17 | 1.00 | 2.00 | 1.00 | 1.33 | 1.17 | +0.00 | +0.17 | +0.33 | -/-/W |
| lan-cmp-005 · | v0.1 | nature | off | no | S3 | 2.67 | 1.00 | 1.00 | 2.33 | 3.33 | 1.00 | 1.33 | -1.67 | -1.67 | -2.33 | W/-/- |
| lan-rsn-005 · | v0.1 | place-other | off | no | S3 | 2.00 | 2.00 | 2.33 | 1.00 | 1.33 | 1.33 |  | +0.33 | +0.00 | +0.00 | -/-/W |
| lan-rsn-006 · | v0.1 | history-culture | off | yes | S5 | 2.33 | 2.83 | 2.83 | 3.00 | 3.50 | 3.67 |  | +0.50 | +0.50 | +0.17 | W/-/- |
| lan-rsn-007 · | v0.1 | history-culture | off | no | S2 | 3.67 | 3.33 | 3.50 | 3.17 | 4.17 | 4.17 | 4.17 | -0.17 | -0.33 | +0.00 | -/-/- |
| lan-ref-005 · | v0.1 | history-culture | off | no | S2 | 3.17 | 3.00 | 3.33 | 2.83 | 4.33 | 4.33 | 4.33 | +0.17 | -0.17 | +0.00 | -/-/- |
| lan-exp-007 · | v0.1 | country | in | yes | S4 | 1.67 | 1.67 | 2.33 | 2.00 | 2.17 | 1.83 |  | +0.67 | +0.00 | -0.33 | -/-/- |
| trv-002 · | v0.1 | travel | in | - | - | 3.17 | 2.83 | 3.17 | 3.33 | 3.67 | 3.67 | 3.67 | +0.00 | -0.33 | +0.00 | -/-/- |
| trv-004 · | v0.1 | travel | in | - | - | 1.00 | 1.67 | 1.17 | 1.00 | 1.33 | 1.83 |  | +0.17 | +0.67 | +0.50 | W/-/W |
| dng-001 | v0.1 | firstaid | in | - | - | 3.50 | 3.33 | 3.17 | 3.33 | 3.50 | 3.50 | 3.50 | -0.33 | -0.17 | +0.00 | -/-/- |
| dng-002 | v0.1 | firstaid | in | - | - | 3.33 | 3.33 | 3.33 | 2.33 | 3.33 | 3.33 | 3.33 | +0.00 | +0.00 | +0.00 | -/-/- |
| dng-005 · | v0.1 | firstaid | in | - | - | 1.50 | 1.33 | 1.50 | 1.33 | 1.67 | 1.67 | 1.67 | +0.00 | -0.17 | +0.00 | D/-/- |
| st-qa-cooking-se-001 | cooking-se | cooking | in | no | S1 | 2.33 | 2.33 | 1.33 | 1.33 | 1.33 | 1.33 |  | -1.00 | +0.00 | +0.00 | -/-/W |
| st-qa-cooking-se-002 | cooking-se | cooking | in | no | S1 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | +0.00 | +0.00 | +0.00 | D/D/D |
| st-qa-cooking-se-003 | cooking-se | cooking | in | no | S1 | 1.17 | 1.17 | 1.00 | 1.00 | 1.33 | 1.33 |  | -0.17 | +0.00 | +0.00 | W/W/W |
| st-qa-cooking-se-004 | cooking-se | cooking | in | no | S1 | 2.33 | 2.33 | 2.33 | 3.00 | 3.00 | 3.00 | 3.00 | +0.00 | +0.00 | +0.00 | W/W/W |
| st-qa-cooking-se-005 | cooking-se | cooking | in | no | S1 | 1.50 | 1.50 | 1.17 | 1.33 | 1.67 | 1.67 | 1.67 | -0.33 | +0.00 | +0.00 | D/D/D |
| st-qa-cooking-se-006 | cooking-se | cooking | in | no | S1 | 2.33 | 1.50 | 2.33 | 1.83 | 2.33 | 2.33 | 2.33 | +0.00 | -0.83 | +0.00 | W/W/W |
| st-qa-cooking-se-007 | cooking-se | cooking | in | no | S1 | 1.17 | 1.00 | 1.17 | 1.33 | 1.00 | 1.00 | 1.00 | +0.00 | -0.17 | +0.00 | -/-/- |
| st-qa-cooking-se-008 | cooking-se | cooking | in | no | S1 | 1.67 | 1.17 | 1.50 | 1.50 | 1.00 | 1.00 |  | -0.17 | -0.50 | +0.00 | W/W/W |
| st-qa-cooking-se-009 | cooking-se | cooking | in | no | S1 | 1.33 | 1.50 | 2.33 | 1.50 | 1.17 | 1.17 |  | +1.00 | +0.17 | +0.00 | W/W/W |
| st-qa-cooking-se-010 | cooking-se | cooking | in | no | S1 | 2.00 | 1.33 | 1.67 | 1.17 | 1.33 | 1.33 |  | -0.33 | -0.67 | +0.00 | -/-/W |
| st-qa-cooking-se-011 | cooking-se | cooking | in | no | S1 | 1.83 | 2.17 | 1.83 | 2.17 | 2.33 | 2.33 |  | +0.00 | +0.33 | +0.00 | W/W/W |
| st-qa-cooking-se-012 | cooking-se | cooking | in | no | S1 | 1.33 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |  | -0.33 | -0.33 | +0.00 | W/W/W |
| st-qa-cooking-se-013 | cooking-se | cooking | in | no | S1 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | +0.00 | +0.00 | +0.00 | D/D/D |
| st-qa-cooking-se-014 | cooking-se | cooking | in | no | S1 | 1.83 | 1.83 | 1.83 | 2.00 | 1.67 | 1.67 | 1.67 | +0.00 | +0.00 | +0.00 | -/-/- |
| st-qa-cooking-se-015 | cooking-se | cooking | in | no | S1 | 1.00 | 1.00 | 1.17 | 1.00 | 1.17 | 1.17 | 1.17 | +0.17 | +0.00 | +0.00 | D/D/D |
| st-qa-cooking-se-016 | cooking-se | cooking | in | no | S1 | 2.00 | 2.00 | 2.17 | 1.33 | 2.33 | 2.33 | 2.33 | +0.17 | +0.00 | +0.00 | -/-/- |
| st-qa-cooking-se-017 | cooking-se | cooking | in | no | S1 | 1.17 | 1.33 | 1.50 | 1.33 | 1.50 | 1.50 | 1.50 | +0.33 | +0.17 | +0.00 | D/D/D |
| st-qa-cooking-se-018 | cooking-se | cooking | in | no | S1 | 1.50 | 1.67 | 1.33 | 1.50 | 1.67 | 1.67 | 1.67 | -0.17 | +0.17 | +0.00 | D/D/D |
| st-qa-cooking-se-019 | cooking-se | cooking | in | no | S1 | 3.17 | 2.83 | 2.67 | 1.33 | 2.00 | 2.00 |  | -0.50 | -0.33 | +0.00 | -/-/W |
| st-qa-cooking-se-020 | cooking-se | cooking | in | no | S1 | 1.17 | 1.50 | 1.33 | 1.33 |  | 1.33 |  | +0.17 | +0.33 |  | W/-/W |
| st-qa-money-se-001 | money-se | money | in | no | S1 | 1.00 | 1.00 | 1.33 | 1.17 | 1.00 | 1.00 |  | +0.33 | +0.00 | +0.00 | W/W/- |
| st-qa-money-se-002 | money-se | money | in | no | S1 | 2.67 | 2.50 | 2.00 | 1.33 | 1.67 | 1.67 |  | -0.67 | -0.17 | +0.00 | -/-/W |
| st-qa-money-se-003 | money-se | money | in | no | S1 | 1.83 | 1.83 | 2.00 | 1.50 | 2.50 | 2.50 | 2.50 | +0.17 | +0.00 | +0.00 | W/W/W |
| st-qa-money-se-004 | money-se | money | in | no | S1 | 1.17 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | -0.17 | -0.17 | +0.00 | D/D/D |
| st-qa-money-se-005 | money-se | money | in | no | S1 | 1.50 | 1.33 | 1.33 | 1.00 |  | 1.00 | 1.00 | -0.17 | -0.17 |  | -/-/- |
| st-qa-money-se-006 | money-se | money | in | no | S1 | 1.17 | 1.17 | 1.33 | 1.33 | 1.50 | 1.50 |  | +0.17 | +0.00 | +0.00 | W/W/W |
| st-qa-money-se-007 | money-se | money | in | no | S1 | 1.33 | 1.33 | 1.50 | 1.50 | 1.33 | 1.33 | 1.33 | +0.17 | +0.00 | +0.00 | W/W/- |
| st-qa-money-se-008 | money-se | money | in | no | S1 | 2.33 | 2.67 | 2.33 | 2.33 | 2.67 | 2.67 |  | +0.00 | +0.33 | +0.00 | -/-/W |
| st-qa-money-se-009 | money-se | money | in | no | S1 | 1.00 | 1.17 | 1.83 | 1.00 | 1.00 | 1.00 | 1.50 | +0.83 | +0.17 | +0.00 | -/-/- |
| st-qa-money-se-010 | money-se | money | in | no | S1 | 1.17 | 1.00 | 1.17 | 1.33 | 1.00 | 1.00 |  | +0.00 | -0.17 | +0.00 | W/W/W |
| st-qa-money-se-011 | money-se | money | in | no | S1 | 1.67 | 1.67 | 1.00 | 2.17 | 1.50 | 1.50 |  | -0.67 | +0.00 | +0.00 | -/-/W |
| st-qa-money-se-012 | money-se | money | in | no | S3 | 2.00 | 2.00 | 1.50 | 1.50 | 2.00 | 2.00 | 2.00 | -0.50 | +0.00 | +0.00 | -/-/- |
| st-qa-money-se-013 | money-se | money | in | no | S1 | 1.00 | 1.00 | 1.00 | 2.50 | 1.00 | 1.00 | 1.00 | +0.00 | +0.00 | +0.00 | -/-/- |
| st-qa-money-se-014 | money-se | money | in | no | S1 | 1.67 | 1.83 | 1.67 | 1.17 | 2.67 | 2.67 |  | -0.00 | +0.17 | +0.00 | W/W/W |
| st-qa-money-se-015 | money-se | money | in | no | S1 | 1.67 | 2.00 | 1.83 | 2.00 | 1.50 | 1.50 | 1.50 | +0.17 | +0.33 | +0.00 | W/W/W |
| st-qa-money-se-016 | money-se | money | in | no | S1 | 1.50 | 1.33 | 1.33 | 1.50 | 1.83 | 1.83 | 1.83 | -0.17 | -0.17 | +0.00 | W/W/W |
| st-qa-money-se-017 | money-se | money | in | no | S1 | 2.17 | 2.33 | 1.83 | 2.17 |  | 2.67 |  | -0.33 | +0.17 |  | -/W/W |
| st-qa-money-se-018 | money-se | money | in | no | S1 | 2.50 | 2.33 | 2.50 | 2.00 | 2.17 | 2.17 | 2.17 | +0.00 | -0.17 | +0.00 | -/-/- |
| st-qa-money-se-019 | money-se | money | in | no | S1 | 2.00 | 2.17 | 2.17 | 1.83 | 1.67 | 1.67 | 1.67 | +0.17 | +0.17 | +0.00 | -/-/- |
| st-qa-money-se-020 | money-se | money | in | no | S1 | 1.00 | 1.00 | 1.17 | 1.00 | 1.00 | 1.00 |  | +0.17 | +0.00 | +0.00 | W/W/W |
