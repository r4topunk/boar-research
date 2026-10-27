# STYLE-SEFIX (2026-10-23): Succinct vs Detailed on Qwen3-1.7B under the SEFIX-124 search tree, MAIN 97, seed 42

**Leitura para o r4to (PT-BR):**
1. Succinct continua vencendo mesmo com a busca nova (SEFIX-124): Detailed − Succinct = −0.028 U (CI −0.048…−0.008), 23 melhor / 35 empate / 39 pior.
2. Quando o fato chega no chunk, o Detailed NÃO aproveita melhor: o gap aumenta (−0.047, CI −0.084…−0.010) em vez de encolher (não entregue −0.012, CI −0.033…+0.009).
3. Erros confiantes por 100: Succinct 25.8 → Detailed 46.4 (entregue 31 → 50; não entregue 22 → 46); sem aviso 13.4 → 22.7.
4. Detailed = 400 tokens p50 vs 41 (9.8x), 13.9 s vs 7.2 s p50; 1 item de saúde pior (lan-hlt-002: fato certo + estudo inventado).
5. Recomendação não muda: Succinct segue padrão do 1.7B, e "Detailed quando o fato foi entregue" não se qualifica.

Criterion: STYLE-SEFIX-criterion.md, sha256 `25478a97f3f60431b25e580fee8746a9aa510a8c9c13b3a4c228380eddcf7ff2` (frozen before any generation or judge call, not edited). Calls: Haiku 146 of 400 (5.5-low judge.v1-low N 4 both orders), Opus 0, paid 0, phone 0. Wall: generation 20 min (mini, 1 slot), judge 3.5 min.

## Commands
- `python3 -I tools/mk_req.py` -> req/style-sefix-D-s42.requests.jsonl (sefix124-main-s42 requests + settings.personalityId detailed; 97 rows).
- `bash tools/run_gen.sh req/style-sefix-D-s42.requests.jsonl style-sefix-D-s42 D` = night-1023/b/tools/run_b_gen.sh (SEFIX-124 recipe: be-0cfd4a77-cut7-litepacks clone + H4-MERGE + SEFIX-ALL patches, env RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1, F3 unset, packs-k13) + adapter maxTokens 512 -> 1024 by sed in the per-run clone. 97/97, 0 errors, 0 at cap, persona detailed be0e6710 on every row (S: succinct 5e0de1c7). rs-SEFIX and other rs-* untouched.
- `python3 -I tools/plan.py` -> 24 D texts byte-identical to S (deterministic/extractive items: they reuse the cached row), 73 to judge.
- `bash tools/judge.sh traces/style-sefix-D-s42.traces.jsonl judge/need.ids judge D` (night-1023 judge_b.sh recipe, same references as the S rows: v01 40 + cooking 14 + money 19 ids x 2 = 146 calls).
- `python3 -I tools/agg.py` -> aggregates/style-sefix.json. S rows = cached SEFIX-124 s42 rows (agg_124.py cache), checked identical to answers-sefix124.json on 97/97.
- Deviation (logged before judging, outcome-blind): the criterion names coverage-map/chunklevel.json for the delivered flag, but that file has no "sefix F1F2F4" key; read from coverage-map/sefix/chunklevel-124.json (same tool and schema; the 42 of 92 used by SEFIX-124 and B-TABLE).

## Results (U = ratio of sums, paired item bootstrap B 2000, Random(11); CE = answered with corr <= 1.5, per 100 items)
| split | n | U S | U D | dU D-S (CI) | better/tie/worse | dcorr | CE/100 S -> D | CE-unwarned/100 S -> D | tok p50 S / D | ms p50 S / D |
|---|---|---|---|---|---|---|---|---|---|---|
| overall | 97 | 0.427 | 0.399 | **-0.028 (-0.048..-0.008)** | 23/35/39 | -0.63 | 25.8 -> 46.4 | 13.4 -> 22.7 | 41 / 400 | 7,228 / 13,852 |
| delivered | 42 | 0.425 | 0.377 | **-0.047 (-0.084..-0.010)** | 15/6/21 | -0.95 | 31.0 -> 50.0 | 14.3 -> 31.0 | 45 / 406 | 8,093 / 14,422 |
| not delivered (keyed) | 50 | 0.420 | 0.408 | -0.012 (-0.033..+0.009) | 8/25/17 | -0.41 | 22.0 -> 46.0 | 12.0 -> 16.0 | 36 / 394 | 6,858 / 13,673 |
| health (-hlt-, dng-) | 9 | 0.492 | 0.473 | -0.019 (-0.068..+0.011) | 1/7/1 | -0.44 | 22.2 -> 33.3 | 22.2 -> 33.3 | 0 / 0 | 1,069 / 1,023 |
Interaction dU(delivered) - dU(not delivered) = -0.035 (-0.078..+0.009). Health items worse: 1 (lan-hlt-002, delivered: D states the right 150-300 min guideline, then adds an invented journal study; corr 4.5 -> 1.5).
Secondary (not in the criterion): 24 D texts are identical to S (forced ties; 18 of them in not-delivered). Text-differs only: overall n 73 -0.037 (-0.064..-0.011); delivered n 40 -0.050 (-0.087..-0.011); not delivered n 32 -0.019 (-0.052..+0.012); CE counts S/D 17/37, 11/19, 6/18. Same reading.

## Predictions (frozen)
| | prediction | outcome | |
|---|---|---|---|
| P1 | overall dU < 0, about -0.04..-0.10 | -0.028 (CI excludes 0) | HIT on sign, MISS on size (smaller than predicted) |
| P2 | delivered gap shrinks vs not delivered, stays <= 0 | delivered -0.047 vs not delivered -0.012 | MISS on shrink (it widens), HIT on <= 0 |
| P3 | CE/100 D > S in both splits | 31 -> 50 and 22 -> 46 | HIT |
| P4 | tok p50 >= 5x, ms p50 >= 2.5x | 9.8x tokens, 1.9x ms | HIT tokens, MISS ms (prefill dominates the Succinct time) |

## Recommendation (criterion rule)
- Default change (overall dU >= 0, CE not up, 0 health worse): NO (dU -0.028, CE 25.8 -> 46.4, 1 health worse).
- Conditional "Detailed when the fact is delivered" (delivered dU >= 0 with CI low > -0.03, CE not up, 0 health worse): NO (dU -0.047, CE 31 -> 50, lan-hlt-002).
- Succinct stays the 1.7B default under the SEFIX-124 tree. Reading: when the right chunk arrives, Succinct states it in one or two sentences; Detailed states it and then pads from memory, and the padding is where corr drops (delivered dcorr -0.95). What would change this: Detailed >= Succinct on the delivered items with no CE increase, which a grounding-constrained long persona (only kept-source sentences) might reach; not tested here.

## Caveats
One seed (42); Haiku 5.5-low judge (compresses gaps; tends to over-call CE on long answers, so the CE gap may be inflated, the sign matches PARA135/STYLE15B); dev items (MAIN 97 = v0.1 57 + 40 cooking/money self-tests written from the packs, so delivery is optimistic); 1.7B only, bench engine tree (not the native app); delivered vs not delivered is observational (item difficulty differs between splits; the within-item D-S per split is the read, the interaction CI crosses 0); S rows are reused cached rows judged in earlier passes with the same judge and references, D rows are new.

Files: STYLE-SEFIX-criterion.md (+ .sha256), tools/{mk_req.py,run_gen.sh,plan.py,judge.sh,common.py,agg.py}, aggregates/{style-sefix.json,plan.json}; traces/, judge/, req/, logs/ gitignored.
