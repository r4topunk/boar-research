# FACTBOOK-V2-CONFIRM: Opus judge.v1 on the shaped boar-factbook (2026-10-23 17:0x): NOT-CONFIRMED by the frozen CE clause (U clause passes)

**Leitura para o r4to (PT-BR):**
1. O Opus confirma o ganho de qualidade: o factbook reformatado sobe U de 0.32 para 0.44 (+0.12, CI +0.03..+0.22), positivo nas duas seeds (+0.11 e +0.14); certo 25 -> 55/45 por 100.
2. Pela regra congelada o veredito é NOT-CONFIRMED: 1 item (020, Áustria x Irlanda) vira erro confiante nas duas seeds. Mas é o mesmo erro do base (diz que a Áustria é mais rica, com o aviso de "may be wrong"), o fato não chega em nenhum braço (mesmos artigos), e o base só ficou acima do limiar por acertar a parte da altitude.
3. Erros confiantes no total caem: 5 -> 3 / 1 por 20 (sem aviso 4 -> 1 / 0). O pack não piora a honestidade; a cláusula foi estrita e pegou um artefato de limiar.
4. Publicar v2 como **user-selected** (não default: correct-any 0.50 Haiku e 0.50 Opus, abaixo de 0.60) é defensável; a decisão é sua. Card pronto em rnd/research/packs/boar-factbook.v2.DRAFT.md, nada foi enviado.

Criterion: V2-CONFIRM-criterion.md sha256 `f17179a59a33441877d538728625d9ad9f5bdf44e3de0982a936fdeb1ab44463` (frozen before any judge call, not edited). Ledger: Opus 120 of 130 (0 retries, 6 shard invocations rc 0, one judgeModel claude-opus-5-5, judge.v1, seed 7), Haiku 0, paid 0, phone 0, generation 0.

## Commands
```
v2confirm/run.sh        # 3 x shard_judge.sh <traces> v2confirm/<ARM>.judgments.jsonl boar-eval/bench/selftest/boar-factbook v2confirm/ids.txt fbv2-opus-<ARM> 4 opus
python3 -I v2confirm/agg.py   # -> V2-CONFIRM.json
```
Traces: BASE = packproof/gen/on-k13 (f3a398a8, 20 factbook rows), S42 = gen/on-k13s (095528d4), S43 = gen/on-k13s43 (a5681d84). Wall 57-66 s per arm.

## Table (n 20, Opus judge.v1, both orders; U = sum(s-1)/sum(r-1), item bootstrap B 2000)
| arm | U (CI) | dU vs BASE (CI) | better/tie/worse | corr | correct/100 | CE/100 | CE unwarned |
|---|---|---|---|---|---|---|---|
| BASE (original, s42) | 0.316 (0.223-0.421) | - | - | 2.75 | 25 | 25 (004 005 006 007 010) | 4 |
| shaped s42 | 0.421 (0.321-0.528) | **+0.106 (+0.020..+0.203)** | 9/6/5 | 3.33 | 55 | 15 (007 010 020) | 1 |
| shaped s43 | 0.451 (0.355-0.546) | **+0.136 (+0.039..+0.239)** | 10/7/3 | 3.53 | 45 | 5 (020) | 0 |
| shaped pooled | 0.436 (0.338-0.534) | **+0.121 (+0.030..+0.221)** | 10/8/2 | 3.43 | - | - | - |

Decision clauses: (a) pooled dU CI low +0.030 > 0: **PASS**. (b) new confident errors = 0: **FAIL** (st-boar-factbook-020 at s42 and s43). **Verdict (frozen rule): NOT-CONFIRMED.**

## The one new CE (020, Austria vs Ireland GDP per person and elevation)
All three answers carry the warning line and make the same main error (Austria richer per person). Kept titles are identical in all three arms (Austria, Ireland, an SE travel post); the fact chunk is delivered in none (PACKSHAPE stage 1/2: fact false both arms). BASE corr 2.0 because it also said Austria is higher; shaped said "both diverse" (s42) or a vague terrain contrast (s43) and scored 1.0. So the CE flip is a threshold effect on a warned, undelivered, same-error answer, not a reading error caused by the shaped text. It is reported, not discounted: the rule stands.

## Agreement with Haiku (stage 2)
Opus correct (corr >= 4) flips wrong -> right on 001 005 006 009 014 (both seeds), as Haiku did; Opus also lifts 017 and 015 partially. 010 stays wrong under both (Opus rated the BASE "correct from memory" answer corr 1.0, so Haiku's right->wrong flip on 010 is not seen by Opus). 002/004/007 stay wrong with or without the fact. Opus correct/100 pooled (55+45)/2 = 50, the same 0.50 as Haiku's correct-any.

## Predictions
P1 dU pooled > 0, CI low > 0: HIT (+0.121, +0.030). P2 both seeds > 0: HIT. P3 at least one new CE: HIT (020, not 010/013 as guessed).

## Caveats
One base seed (PACKPROOF s42; BASE on the MacBook, shaped on the mini). Self-tests are agent-written from this pack's text (dev, retrieval-favoured). n 20: the CI is wide. Opus scores the 1.7B Succinct answers only.
