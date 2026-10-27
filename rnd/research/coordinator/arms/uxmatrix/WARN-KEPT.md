# WARN-KEPT (2026-10-23): "cited but unsupported" lexical rule gives back 9 of 26 wrong-unwarned answers with the pack on, 1 of 13 on SEFIX MAIN. NO

**Leitura (PT-BR)**
- Com o pack ligado, 26 das 120 respostas (Succinct 13, Detailed 13) saem erradas sem aviso; as 26 citam uma fonte que sobreviveu ao CT-1 (16 com a citação posta pelo próprio motor via atribuição), então nenhuma regra de release dispara e a linha some.
- A regra R-KEEP (citou, mas menos da metade dos números e nomes da resposta está no trecho citado) devolve o aviso a 9 de 26 (35 %), ao custo de 5 de 37 certas (14 %); no SEFIX MAIN devolve 1 de 13 (8 %).
- Motivo: em 17 das 26 o trecho citado contém os específicos da resposta (11) ou a resposta não tem específico (6); o erro está no raciocínio ou na leitura, não num número ou nome inventado. Origem da citação (modelo vs motor) também não separa (WC 16 vs certas 17 no motor).
- Gate falha nos dois conjuntos (precisa >= 50 % de recuperação): sem patch. A ausência do aviso com pack ligado continua não sendo sinal de acerto (ON cited unwarned: 26 erradas, 22 certas).

Criterion: WARN-KEPT-criterion.md, sha256 d5b5436d102ae50138bd9bf76c3db1f1b45548e99f0952c64aedd26825fdcd54 (frozen before any per-answer count). Script tools/warnkept.py (sha256 f12758ae...), output warnkept.json (sha256 d80c0390...). Cost: 0 LLM, 0 generation, 0 judge, 0 Haiku (labels complete), 0 paid, 0 phone. rs-SEFIX only read; no rs-WARNKEEP tree, no patch.

## 1. Why the line drops (engine, rs-SEFIX src/routing/answer.ts)
The CMP30OFF line is written only by release(): all-citations-removed (CT-1 removed every [n]), uncited-with-sources (no [n] after attribution), uncited (no on-topic source), false-claim. An answer that keeps at least one [n] after CT-1 (checkCitations) or gains one from attributeCitations (reason code citations:added-n) passes every branch and gets no line; finish() emits the separate "No offline source backs this answer." event only when cited is empty. So with the pack on, any surviving or attributed citation silences the warning.

## 2. Classification, Set A pack ON, the 26 WRONG_CONFIDENT answers (all unwarned)
| mode | why no line | citation origin | key specific in cited chunk | n |
|---|---|---|---|---|
| succinct | cited-kept | engine-attributed | present (share >= 0.5) | 4 |
| succinct | cited-kept | engine-attributed | absent (< 0.5) | 1 |
| succinct | cited-kept | engine-attributed | no specific | 3 |
| succinct | cited-kept | model | present | 2 |
| succinct | cited-kept | model | absent | 2 |
| succinct | cited-kept | model | no specific | 1 |
| detailed | cited-kept | engine-attributed | present | 3 |
| detailed | cited-kept | engine-attributed | absent | 4 |
| detailed | cited-kept | engine-attributed | no specific | 1 |
| detailed | cited-kept | model | present | 2 |
| detailed | cited-kept | model | absent | 2 |
| detailed | cited-kept | model | no specific | 1 |
- 26/26 cited-kept (0 health route, 0 uncited); 9/26 also carry citations:removed-* (CT-1 removed some, not all). Totals: specific present 11, absent 9, no specific 6.
- Pack-ON surface (120): warned 56 (WW 43, CWS 8, CFM 5); unwarned uncited 16 (HU 14 = engine declines, CFM 2); unwarned cited 48 (WC 26, CWS 20, CFM 2).
- Set B (SEFIX-124 MAIN s42) CE-unwarned 13: 6 are engine declines scored CE (5 health-route: 4 cooking/money detector misfires + dng-005; 1 places route), 7 cited-kept (specific present 4, absent 1, no specific 2).

## 3. R-KEEP counts (recall = wrong-unwarned now warned / WU; cost = correct now warned / all correct)
| set | rule | WU | warned | recall | correct | warned | cost | fires |
|---|---|---|---|---|---|---|---|---|
| **A ON 120** | **R-KEEP** | 26 | 9 | **0.35** | 37 | 5 | **0.14** | 14 |
| A ON succinct 60 | R-KEEP | 13 | 3 | 0.23 | 21 | 2 | 0.10 | 5 |
| A ON detailed 60 | R-KEEP | 13 | 6 | 0.46 | 16 | 3 | 0.19 | 9 |
| A ON 120 | R-KEEP-any (sens.) | 26 | 18 | 0.69 | 37 | 9 | 0.24 | 27 |
| A ON 120 | R-KEEP-num (sens.) | 26 | 5 | 0.19 | 37 | 6 | 0.16 | 11 |
| A OFF 110 (report) | R-KEEP | 13 | 4 | 0.31 | 23 | 2 | 0.09 | 6 |
| **B MAIN 97** | **R-KEEP** (correct = corr >= 3.5) | 13 | 1 | **0.08** | 32 | 2 | **0.06** | 5 |
| B MAIN 97 | R-KEEP-any (sens.) | 13 | 3 | 0.23 | 32 | 4 | 0.13 | 13 |
| B MAIN 97 | R-KEEP (correct = non-CE, sens.) | 13 | 1 | 0.08 | 72 | 4 | 0.06 | 5 |
- OFF is 110, not 120: the 5 gen-nopack items have ON = OFF and appear once per mode under ON.
- Gate (both sets: recall >= 0.50 and cost <= 0.15): A 0.35 / 0.14 FAIL on recall; B 0.08 / 0.06 FAIL on recall. The looser any-missing variant reaches recall on A (0.69) at cost 0.24 (Detailed 0.44) and still fails on B (0.23).
- Flags Set B: 0 proxy rows; 4 items whose live kept titles differ from the F1F2F4 replay (counted, as frozen); every cited title found in the replay.

## Verdict: NO
No patch written (WARN-KEPT.patch not created, rs-WARNKEEP not made), so no engine replay of the warning stage was run. The lexical "cited but unsupported" check cannot restore the line because most pack-ON confident errors cite a chunk that does contain their names and numbers (or have none): the failure is a wrong reading of a relevant chunk, not an unsupported specific. Post hoc (not in the criterion): citation origin does not separate either (cited unwarned ON: engine-attributed WC 16 vs correct 17, model WC 10 vs correct 5), so dropping engine attribution would not be a fix. What remains as UX wording, not a rule: the absence of the line with the pack on should not read as "verified" (cited unwarned ON = 26 wrong vs 22 correct).

Caveats: 1 seed; Haiku labels (UXMATRIX hand read: 1 of 8 WC labels wrong, lan-ref-003, which R-KEEP does not fire on); Set A chunk text = compressed Context blocks the model saw, engine fullOf would use the full chunk (more lenient, so recall could only fall); Set B correct cut at corr >= 3.5 fixed in the criterion.

Files: WARN-KEPT-criterion.md (+ .sha256), tools/warnkept.py, warnkept.json (per-answer rows A and B with specifics, missing list, reason codes).
