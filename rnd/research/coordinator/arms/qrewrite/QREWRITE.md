# QREWRITE: answer-form query rewrite before search (2026-10-23) - STOPPED AT STAGE 0 (NO-CEILING)

**Leitura para o r4to (PT-BR):**
1. O caminho **não se confirmou**. Mesmo o teto com oráculo (buscar com a frase-resposta escrita por nós, sem modelo) não passa a regra de parada: MAIN 42 -> 51 fatos (+9, a regra pedia +10) e self-tests kept 100 -> 118 (+18, pedia +20).
2. A busca crua melhora (artigo certo no raw 73 -> 99 de 180), mas o keep perde 12 itens que antes achava (4 de saúde). Buscar só com a frase-resposta, sem a pergunta, é **pior** que hoje (kept 100 -> 56), porque perde o assunto ("Officers waived the fine..." não diz Tailândia).
3. Custo gasto: 0 LLM, 0 Haiku, 0 mini, ~25 min de replay no MacBook. O 1.7B nem foi chamado: se o oráculo não chega a +10, uma reescrita "sem responder" do 1.7B chega a menos.
4. Investimento completo, se alguém quisesse insistir: hook de duas buscas no engine, +1 chamada do 1.7B por pergunta (latência não medida), filtro de saúde para as 4 perdas e um screen Haiku. Estimo ganho máximo de ~+9 fatos de 92, abaixo do que F1/F2/F4 já deram (+14).
5. O que fica: a lacuna da primeira busca não se fecha reescrevendo a forma da pergunta. Os ganhos vêm de termos da resposta que o usuário não tem e o modelo pequeno não sabe. Fecho a linha.

Criterion: QREWRITE-criterion.md sha256 60fdc688dee20e7df41055e71e0ee11ce1af7254de5281f69208e740f864db14 (frozen before any run, verified after, not edited).
Calls: LLM 0, Haiku 0 (cap 300 unused), Opus 0, paid 0, phone 0, mini 0. MacBook replays only (shared replay cache, runs sequential).

## Setup
- Tree kiln-local/rs-SEFIX read-only, SEFIX-124 env (gidf + F1 + F2 + F4). No engine patch. Driver tools/replay-qrw.ts = retrieve-sweep replay-sweep.ts + one QREWRITE hook. The hook swaps the engine's search query inside the retrieve dependency (replace or concat) and leaves answer() the original question. The concat arm is the "two queries merged by gidf" (one FTS5 OR pool over both term sets).
- Identity: the driver with no map = sefix/replays/main.F1F2F4 on 97/97 raw titles and 97/97 kept ids (MAIN base 42 chunk-level facts). ST180 base on the same driver: raw own-article 73/180 (PACKPROOF live 40 %), kept 100/180 (live 98). Raw titles equal the PACKPROOF ON traces on 176/180.
- Oracle text (criterion rules). 24 ST items with a QFORM counterpart use the F5 answer-term statement. The other 156 ST items and cm 40 join the self-test's in_pack_facts `fact` strings. v0.1 48 use the question + the first answer term of each grading group. "re:" regex terms are skipped (implementation reading of "term"). 5 v0.1 items have no terms and get no entry. dng items get none.
- Own-article match uses the keptFull/rawFull docId (pack:local-<pack>:a<article>). This is PACKPROOF's url+title rule on the own pack copy, because the full records carry no source field.

## Stage 0 table (0 LLM)
| arm | MAIN chunk facts /92 (cm, v0.1) | MAIN gained / lost | MAIN kept lists changed | ST own raw /180 | ST own kept /180 | ST gained / lost (health lost) | QFORM-24 kept | crowding share / mean kept |
|---|---|---|---|---|---|---|---|---|
| base (SEFIX-124) | 42 (14, 28) | - | - | 73 | 100 | - | 10 | 0.698 / 4.02 |
| S0 replace (oracle only) | 50 (21, 29) | 11 / 3 | 68 | 63 | 56 | 14 / 58 (14) | 15 | 0.776 / 2.87 |
| **S0Q concat (oracle + question)** | **51 (23, 28)** | 11 / 2 | 65 | **99** | **118** | 30 / 12 (4) | 14 | 0.620 / 3.80 |
| S0W whole question replaced (secondary, keep sees the oracle too) | 57 (23, 34) | 19 / 4 | 75 | 62 | 63 | 18 / 55 (12) | 16 | 0.827 / 3.95 |

ST by pack, S0Q kept vs base: factbook 13/9, simplewiki 20/18, ethereum 15/10, health-se 15/11, outdoors 15/12, bitcoin 9/7, medlineplus 11/10, firstaid 4/6, travel 16/17.
MAIN losses: vit-cry-001 and cooking-007 in every arm. They are exact-term items, and P3 is confirmed on the oracle already. MAIN health losses: 0 in all arms. ST health losses: S0Q loses 4 (health-se-011, firstaid-007, firstaid-019, medlineplus-015).

## Stop rule (frozen): ceiling = better of S0 and S0Q
- MAIN: 51 = +9 < +10 (42 -> 52 needed). ST180: 118 = +18 < +20. **Both under -> STOP, verdict NO-CEILING.** Stages 1 and 2 were not run. The rewrite prompt, the 3 few-shot turns and the mini scripts (tools/rw_gen.py, tools/run_mini_rw.sh, items/rw_in.jsonl, 277 questions) are ready and unused.
- S0W is secondary by the criterion. Its MAIN +15 comes from v0.1 answer terms reaching the keep step too (oracle leak into grounding, v0.1 28 -> 34), and it costs ST -37. It does not enter the rule.

## Examples (oracle queries; no model rewrite exists, stage 1 not reached)
Good (S0Q gained the own fact / article):
1. cooking-003 "...cover a simmering pan with a round of baking paper..." + "Cartouche controls evaporation. Lids drip unevenly."
2. money-007 "What stops American credit unions from accepting any customer..." + "12 USC 1759(b) common bond..."
3. money-013 target-date fund expense ratio + "Pass-through, not an adder..."
4. health-se-004 "120 over 80" + "Cuff inflated to 200 and sounds. Diastolic definition."
5. factbook-001 Kyrgyzstan + the QFORM F5 statement "The average elevation of Kyrgyzstan is about 2,750 metres, right?"
Bad (lost vs base):
1. travel-001 (S0 replace): "Officers waived the fine for one day; two or more days would be fined..." loses the subject (Thailand, overstay).
2. health-se-011 (S0Q, health): "Criteria. Hypothermia." The terse fact labels pull other articles.
3. firstaid-007 (S0Q, health): "Don't ration. Seawater. Snow."
4. medlineplus-015 (S0Q, health): "Delayed symptoms. Rest." on a concussion question.
5. vit-cry-001: "+ hard fork stark" displaces the quantum/ECDSA chunk (exact-term item, lost in every arm).

## Predictions
| # | prediction | result |
|---|---|---|
| P1 | ceiling >= +15 facts on MAIN | +9 (S0Q). MISS (only the secondary S0W reaches +15) |
| P2 | RW+Q >= half the ceiling | not measured (stage 1 not run) |
| P3 | RW alone loses exact-term items | already on the oracle: S0 replace loses 3 MAIN items, vit-cry-001 in every arm. HIT on the oracle |
| P4 | ST ceiling kept >= +20 | +18. MISS |

## Reads
- Answer-form text helps the first stage (raw own-article 41 % -> 55 % with S0Q). The keep step and the OR-pool crowding give part of it back: 12 lost, 4 of them health items.
- Replace-only is harmful (kept 100 -> 56). A rewrite that drops the user's words loses the subject. Any deployment would have to be concat, and concat is under the bar even with oracle text.
- The oracle is weak for 156 ST and the 40 cm items (terse `fact` labels). The QFORM-24 subset, which has real answer statements, gains +4 to +6 of 24. That is consistent with QFORM but far from F5's 83 %. A 1.7B "do not answer" rewrite cannot supply the answer terms that drive the QFORM effect, so stage 1 would sit below this ceiling.
- Latency: not measured (no rewrite call). Replay wall MAIN 126-153 s, ST 229-341 s per arm on the MacBook.

## Caveats
Dev, agent-written self-tests (retrieval favoured). One deterministic replay per arm. The oracle for self-test items is built from paraphrased fact labels, not full answer sentences, so a stronger oracle (full gold answer) could cross the line. That would be an answer leak, not a rewrite the 1.7B can produce. Own-article = article level (ST) and chunk level (MAIN), as in PACKPROOF and CHUNKLEVEL.

Files: QREWRITE-criterion.md(.sha256), tools/{replay-qrw.ts,run.sh,chain0.sh,mk_oracle.py,score.py,rw_gen.py,run_mini_rw.sh}, items/{oracle.json,oracle.meta.json,rw_in.jsonl}, aggregates/{stage0.json,score.*.json}; replays/ and gen/ gitignored.
