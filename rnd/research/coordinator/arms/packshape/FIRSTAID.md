# PACKSHAPE-FIRSTAID (2026-10-23): NO. Shaping boar-firstaid-en into topic-named sentence blocks does not deliver more facts and loses 2 health sources

**Leitura para o r4to (PT-BR):** a receita que funcionou no factbook não serve para o firstaid. O fato certo chega 4/20 vezes (eram 5), e 2 self-tests de saúde perdem a fonte de saúde (001 ferida no peito, 006 acidente na estrada). Pela regra congelada, o gate falha e a etapa com o modelo não roda. Motivo: o firstaid já é prosa em chunks de cerca de 100 palavras, e 9 dos 20 itens não guardam nenhum chunk (o caminho de saúde barra antes). Prefixar o tópico só reordena a busca. O alavanca aqui é a busca e o caminho de saúde, não o formato. Pack AI-reviewed, not clinically reviewed; nenhuma palavra médica foi alterada.

Criterion: FIRSTAID-criterion.md sha256 `3638455a7e0bd9e751254f633784f969a2883901c297a136118b5ac5eea7f167` (frozen before the shaped build; shaper tools/shape_firstaid.py e3766d04, verified after the run). Haiku 0, Opus 0, paid 0, phone 0, generation 0.

## What was built
- Structure only, from the v3proto text read-only (0a7dffa6). F1 topic = the last segment of the title. F2 sentences and list items without the topic get "<topic>: ". F3 blocks of at most 120 words / 950 chars per section, with the section heading repeated verbatim. F4 no unit is cut.
- Pipeline check (unshaped text, same builder): 22,500/22,500 chunks, plus articles and article_meta, identical.
- Wording check (tools/check_words_fa.py): removing the prefixes and the repeated headings gives the original token sequence on 1,842/1,842 articles, with 0 new tokens. Two checker fixes were needed before it passed, both in the checker only: articles are matched by order (titles repeat across sources), and the heading de-duplication is applied to both texts.
- Pack: 26.33 MB -> 31.57 MB (+20 %); chunks 22,500 -> 30,432. Build 18 s plus sidecar 196 s (MacBook). File kiln-local/shape-packs/fa-shaped/boar-firstaid-en.sqlite (sha 5912d6c4); not in shared-data, not published.

## Stage 1 (0 LLM; rs-SEFIX SEFIX-124; BASE = the PACKSHAPE K13 replays; FASHAPED = K13 with firstaid swapped, factbook original)
| metric | BASE | FASHAPED |
|---|---|---|
| ST20 own article raw / kept | 3 / 6 | 3 / 5 |
| ST20 own fact chunk kept (primary) | 5 | **4** (gained 004; lost 001, 019) |
| ST20 loose rule | 4 | 4 |
| ST20 items with 0 kept chunks | 9 | 9 |
| self-test kept-set changes /140 (other packs) | - | 19 (8) |
| self-test health losses | - | **2** (firstaid-001: a1782, a804; firstaid-006: a600) |
| MAIN chunk-level /92 | 42 | 43 (+ cooking-004, 0 lost) |
| MAIN kept-set changes / health losses | - | 6 / 0 |
| MAIN firstaid share of kept slots | 2.8 % | 3.3 % |
**Gate: (a) -1 < +5 FAIL; (b) 43 >= 41 PASS; (c) 2 health losses FAIL. Verdict: NO. Stage 2 not run.**

## Predictions
P1 fact 5 -> 6 with gate (a) failing: HIT on the gate (actual 4). P2 MAIN 42 and 0 health losses: MISS (MAIN 43 and 0 losses on MAIN, but 2 losses on the self-tests). P3 size +10 to +40 %: HIT (+20 %).

## Reading
Factbook gained because its facts were buried in 17-19-row tables with label-only rows. Firstaid is already prose, sectioned by its own headings, with a median chunk of 104 words. Its misses come before the format: 9/20 items keep nothing, and the raw search reaches the own article on 3/20. The topic prefix only changes the ranking noise, and on two health items it pushes the right health source out. The recipe should be used for table-like packs only.

Files: firstaid.json, tools/{shape_firstaid.py, check_words_fa.py, score_fa.py, kits.py (FASHAPED)}, replay-fa.log (the first st run failed on a shared replay-cache lock while running in parallel with MAIN; it was re-run alone).
