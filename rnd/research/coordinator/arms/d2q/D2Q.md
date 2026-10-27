# D2Q: doc2query at pack build time on boar-factbook (2026-10-23; feasibility result after the coordinator scope cut)

**Leitura para o r4to (PT-BR):**
1. Indexar perguntas geradas **não torna o factbook achável** nesta pilha. O artigo certo entra no kept em 9 de 20 sem perguntas e em 10 de 20 com perguntas (x1 e x2). O gate pedia 15. GATE FAIL, então o stage 2 (Haiku) não rodou.
2. O motivo é o P7. O factbook perde para outros packs que têm o mesmo nome de país (vital5, simplewiki, SE), não para os próprios chunks. As perguntas só põem o chunk no raw em 2 itens a mais (5 → 7).
3. Custo de build: 4B no mini (CPU b11010) gasta 3.5 s por chunk. O factbook inteiro (10.543 chunks) levaria cerca de 10 h e +4.4 MB de índice (+37 %).
4. Plano para todos os packs: os 12 packs pequenos somam 754 mil chunks, cerca de 730 h de mini (30 dias). O kit K13 com os packs grandes soma 2,04 M chunks, cerca de 2.000 h (83 dias). Não vale, ainda mais com MAIN parado em 42.
5. O PACK-SHAPE (0 LLM, 8 → 18/20) resolve melhor o que o D2Q tentava. O D2Q só valeria para a classe lexical-miss, e aqui ele quase não a moveu (raw +2).

Criterion: D2Q-criterion.md sha256 83b06185b8cd63c103a972e7ba1be6629fa71116f6085d4d3f6a5f292a9cea7a (frozen before any generation; verified; not edited). Scope cut (coordinator, about 16:3x): the full generation was stopped at 896 of 2,876 target chunks, the variant was built with partial coverage, and the 0-LLM gate was run as planned. Read this as a feasibility result.

## Generator
- Mini M4, llama-server b11010 CPU build (the only b11010 build there), Qwen3-4B-Instruct-2507-Q4_K_M.gguf (sha 3605803b982cb64a…), port 8131, -np 4 -c 8192 -t 8. It ran inside kiln slot gen1, with disk at 28 GiB. Docker, ollama and :8094 were not touched. The slot and server were freed at 16:36.
- Prompt (exact user message): `Write 4 short questions a user might ask that this passage answers; one per line; use the passage's key terms.\n\nTitle: {title}\nSection: {section}\nPassage:\n{text}`. Sampling: temperature 0.7, top_p 0.8, top_k 20, seed 42, max_tokens 160.
- Output: 896 rows, 0 errors, 0 cut at max tokens, 896/896 gave 4 questions (3,584 questions), 0 duplicates within a chunk, 0 CJK. Mean tokens: 269 prompt and 65 output.
- Time: 280 s for the first 100 (2.80 s/chunk), then 2,873 s for 796 more. Overall 3,153 s for 896 = **3.52 s/chunk** (4 in flight; the mini was shared).

### 5 example question sets
| chunk | passage | questions | read |
|---|---|---|---|
| Malta, Key facts | Official name, Capital: Valletta… | official name; **capital of Malta**; main religion and share; GDP per capita 2024 | good: the user's terms |
| Malta, Transportation | aircraft prefix 9H, airports 1 (2025)… | prefix; how many airports 2025; merchant marine types; key ports | good, but the same template appears for every country |
| Kyrgyzstan, Key facts (criterion example 1) | Capital: Bishkek, population… | official name; languages; % Muslim; currency | bad for the self-test: capital and population are never asked, which the item needs |
| Malta, Economy | GDP composition by end use… | services share; household consumption; exports share; "what does the negative value in imports indicate" | mixed: the last question is interpretation the passage does not answer |
| Montserrat, People and Society | sex ratio, infant mortality, fertility… | sex ratio; infant mortality; fertility and GRR; "% with access to improved drinking water" | mixed: the last question may come from a neighbouring field |

Random-sample example (criterion example 3, Sierra Leone, Transportation): the same four questions as Malta's with the name swapped. Templated questions add the same terms to every country, so they do not tell countries apart.

## Chunk set and pack
- boar-factbook (K13 v3proto copy) has 10,543 chunks. The cap rule gave 876 own-article chunks (22 articles) plus a seeded random 2,000 = 2,876 targets. Generated: 896 = **all 876 own chunks (100 %) + 20 random**. Coverage = 8.5 % of the pack. Within-pack competition is favoured even more than the criterion's declared upper bound.
- Variant: kiln-local/d2q-packs/boar-factbook.sqlite (sha b3487ba0…, not in shared-data, not published). It adds fts_d2q and d2q. Fidelity check: docsize of the first 3 columns matches on 10,543/10,543 rows.
- Index delta from questions only: +376,832 B for 896 chunks, measured against the same build with empty questions. Extrapolated to the whole pack: about +4.4 MB on 11.8 MB (+37 %, d2q table included).
- FTS only. No per-chunk vector over title + questions, because that needs a second embedder pass and a change to the dense-stage engine.

## Engine
kiln-local/rs-D2Q is rs-SEFIX plus RS_D2Q (patch d2q.vs-rsSEFIX.patch), with two modes:
- **x1:** bm25Candidates and the gidf rescore read fts_d2q with weights (title, section, body, 1). The gidf ratio denominator counts rows on fts_d2q.
- **x2:** x1, plus the gate coverage and onTopic also read the questions.

Identity with the switch off on the d2q kit, against K13 on rs-SEFIX: MAIN kept 97/97, reason codes 97/97, self-test kept 180/180. Driver: replay-sweep with the SEFIX-124 env, MacBook, 0 LLM. The off arm was replayed while the kit held the 100-chunk smoke copy. Off never reads fts_d2q, and the other tables are byte-identical.

## Tables (0 LLM)
| arm | factbook own article in raw | own article kept | own fact chunk kept | factbook chunk kept (items) | 180 own kept | MAIN chunk-level facts | MAIN kept-set changes | factbook crowding on MAIN | health losses |
|---|---|---|---|---|---|---|---|---|---|
| off | 5 | **9** | 8 | 9 | 100 | 42 (cm 14, v0.1 28) | — | 2 items | — |
| x1 | 7 | **10** | 8 | 10 | 101 | 42 | 0 | 2 | 0 |
| x2 | 7 | **10** | 9 | 10 | 101 | 42 | 0 | 2 | 0 |

Item changes:
- **factbook-017 (Pakistan languages):** raw no → yes, kept no → yes, fact 0/3 → 1/3 (x1 and x2).
- **factbook-019 (Maldives vs Seychelles):** raw no → yes; fact 1/3 → 0/3 under x1 and 2/3 under x2.

The other 18 items do not change. The other packs do not change (180 own-kept +1 = factbook). Self-test kept-set changes: 3 items. Replay p50 times are not comparable, because the MacBook was loaded by another agent's replays (load 80).

## Gate
own-article kept +1 (needs +6), MAIN 42 (≥ 41 ok), 0 health losses (ok). **FAIL on x1 and x2.** Stage 2 was not run (0 Haiku).

## Predictions
- P1 (x1 10..12): HIT at 10.
- P2 (x2 11..13): MISS at 10.
- P3 (fact chunk rises more than article, +2..+4): MISS, +0/+1.
- P4 (MAIN 42 ±1, 0 health): HIT.
- P5 (crowding ≤ +3): HIT, +0.
- P6 (1.5-3 s/chunk): MISS at 3.5.
- P7 (cross-pack crowding is the failure mode): HIT. Own article in raw is only 5 → 7 of 20, even though every own chunk carries questions. The questions raise factbook scores inside its own index, but under gidf the merged pool stays led by vital5, simplewiki and SE threads that share the country name.

## Verdict
**NO.** doc2query does not make boar-factbook findable on SEFIX-124. This repeats MICROD2Q (10-14) on the adopted stack.

## Cost to do all packs (extrapolated at 3.5 s/chunk on the mini CPU)
| scope | chunks | mini time |
|---|---|---|
| factbook | 10,543 | ≈ 10 h |
| the 12 small packs (crypto, cooking, money, factbook, medlineplus, firstaid, visa, health, travel, outdoors, ethereum, bitcoin) | 754,095 | ≈ 730 h |
| K13 + ethereum/bitcoin with wikivoyage, simplewiki and vital5 | 2,039,641 | ≈ 2,000 h |

The index would grow by about +37 % per pack, at the factbook rate. A Metal or rented-GPU build would cut the time (MICROD2Q put a GPU at [usage detail removed]-25), but that does not matter when the reach gain is +1/20.

## Files
- Criterion: D2Q-criterion.md, .sha256.
- Generation: targets.json, chunks.jsonl (2,876 filled prompts), gen/ (gen.jsonl, gen.log, STATUS, STATUS.probe, server.log), questions.json.
- Build: build.json.
- Replays and results: replay/ (main/st × off/x1/x2 + logs), d2q.json.
- Patch: d2q.vs-rsSEFIX.patch.
- Tools: tools/ (targets.py, extract.mjs, gen.mjs, mini_gen.sh, parse.py, build_d2q.mjs, kits.py, run.sh, batch.sh, score.py).

Ledger: 0 Haiku, 0 Opus, 0 paid, 0 phone, local 4B generation 53 min. Public items only, so there is no EXPOSURES row.
