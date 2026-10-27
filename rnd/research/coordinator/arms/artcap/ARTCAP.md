# ARTCAP: per-article cap 2 -> 4 / vector-chosen second chunk / + lead header (2026-10-23) - NO at stage 0

**Leitura para o r4to (PT-BR):**
1. Não chegam mais fatos ao modelo. MAIN fica em 42 -> 39/40/39 (perde 3-4, ganha 1), self-tests 77 -> 80/80/81 (+3/+3/+4; o gate pedia +25). Nenhum braço passa.
2. Custo de contexto: nulo (p50 0.997-1.008x). O braço não falhou por custo, falhou porque não acrescenta nada.
3. Por quê: o cap realmente segurava o chunk certo (fato no raw nos 37 "cortados pelo cap" 2 -> 9), mas 9 dos 11 chunks que passam a chegar ao raw já chegavam ao contexto pelo head pass/dense (X2b) do SEFIX-124. O SEFIX-124 já resolve metade dos 37 (18). Abrir o cap só troca o caminho e ainda desloca vizinhos de outros artigos.
4. Saúde: os três braços perdem lan-hlt-003 (o chunk "Mosquito-borne disease" sai quando o artigo SE ocupa mais vagas). Isso sozinho já reprova.
5. As respostas não foram testadas (0 Haiku). A classe "artigo achado, chunk errado" está essencialmente coberta pelo X2b. O que falta está em outras classes (gate de relevância, keep de saúde, misses lexicais). Fecho a linha do cap.

Criterion: ARTCAP-criterion.md sha256 4069ae83dfe0bc2876e0fcc78b6e8bf8c45e137f38aab6d59c58c7510d51db14 (frozen before any replay, verified after, not edited).
Calls: LLM 0, Haiku 0 (cap 300 unused), Opus 0, paid 0, phone 0. Stage 2 not run (gate failed).
Patch: arms/retrieve-sweep/patches/ARTCAP.patch sha256 c9ed983d323eccb65d315d4348f0707449c4fbcc4c73f512152e514981b0b5af (diff -ruN rs-SEFIX/src rs-ARTCAP/src, applies with patch -p1 on rs-SEFIX; switch RS_ARTCAP=cap4|capfact|cap4lead, absent = SEFIX-124). Files: src/rag/wikiPack.ts (searchDetailed reads bm25Candidates uncapped and calls rsArtcapGroup; rsLeadHeaderOf), src/rag/packs.ts (packLeadHeader), src/routing/answer.ts (cap4lead header after the head-pass append path).

## Setup and hosts
- Tree kiln-local/rs-ARTCAP = copy of rs-SEFIX + ARTCAP.patch; rs-SEFIX and other trees untouched. Driver tools/replay-artcap.ts = qrewrite replay-qrw.ts without a map. SEFIX-124 env + settings (tools/run.sh).
- Identity, switch absent: MacBook MAIN = sefix main.F1F2F4 on 97/97 raw titles, kept chunk ids and reason codes; MacBook ST = qrewrite st.base on 180/180 kept ids and raw titles.
- On the coordinator's request (MacBook load 56), part ran on the Mac mini (<runner>/kiln/artcap: tree + adapter copy, mini K13 packs compose/packs-k13 with the same byte sizes, embedder threads 4 via BOAR_EMBED_THREADS in a mini-only shim copy, tools/run_mini.sh, replay-artcap-mini.ts). Mini base = MacBook base on MAIN 97/97 (raw, kept, reason codes) and ST 180/180 (kept, raw) before any mini arm was used.
- Host per run: MacBook = MAIN base, MAIN cap4, MAIN capfact, ST base, ST cap4. Mini = MAIN cap4lead, ST capfact, ST cap4lead (+ the two identity bases). Wall ms are host-specific and under load, so they are not compared.

## Stage 0 table (0 LLM)
| arm | MAIN chunk facts /92 (cm, v0.1) | MAIN gained / lost | MAIN health lost | MAIN kept changed | MAIN ctx p50 (x base) / total | ST fact chunk kept /180 | ST fact in raw | ST own article kept | ST gained / lost (health) | ST ctx p50 / total | cap-37 kept | other-19 kept | gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base (SEFIX-124) | 42 (14, 28) | - | - | - | 732 tok | 77 | 41 | 100 | - | 1.0 | 18 | 4 | - |
| CAP4 | 39 (13, 26) | 1 / 4 | lan-hlt-003 | 43 | 0.997 / 0.982 | 80 | 48 | 101 | 5 / 2 (0) | 0.980 / 0.988 | 17 | 4 | FAIL |
| CAPFACT | 40 (13, 27) | 1 / 3 | lan-hlt-003 | 34 | 0.997 / 0.986 | 80 | 48 | 102 | 5 / 2 (0) | 0.998 / 0.991 | 17 | 4 | FAIL |
| CAP4+LEAD | 39 (13, 26) | 1 / 4 | lan-hlt-003 | 61 | 1.008 / 1.014 | 81 | 48 | 101 | 6 / 2 (0) | 1.035 / 1.027 | 17 | 4 | FAIL |

Gate (frozen): MAIN >= 48 or ST >= 102, MAIN health losses 0, MAIN ctx p50 <= 1.15x. All three fail the fact bar and the health clause; context passes.
- MAIN gained vit-cry-010 in every arm. Lost: st-qa-cooking-se-016, lan-hlt-003 and vit-cry-006 in every arm, plus vit-cry-001 in CAP4 / CAP4+LEAD. The cause is crowding: the found article's extra siblings take the per-pack limit slots of other articles (Mosquito-borne disease, a ZK chunk, an ERC page).
- ST gained travel-012, -016, -020, medlineplus-014, factbook-014 (+ factbook-009 with LEAD). Lost factbook-019 and ethereum-017. By pack, the gain is almost all qa-travel-se (10 -> 13).

## The 37 cap-cut items (diag137 article_cap, not kept on ST2)
- Fact chunk kept: base 18, every arm 17. Kept in base: factbook-003, -007, -008, -012, firstaid-001, -017, bitcoin-008, ethereum-005, -011, -017, health-se-008, -013, -016, outdoors-012, -014, travel-003, -005, -011. The arms keep the same set minus ethereum-017. **Recovered by any arm: 0 of the 19 not kept in base.**
- Reach did move: fact chunk in raw 2 -> 9 of 37 (wide-12: 2 -> 12). Over all 180, 11 fact chunks newly reach raw under CAP4, but 9 of those 11 were already in the base context through the SEFIX-124 append path (head pass a2 / X2b dense / F1 seLead). The other 2 are dropped by grounding.
- The 19 "other chunk" items: 4 kept in base and in every arm.

## Predictions
| # | prediction | result |
|---|---|---|
| P1 | CAP4 has the fact kept on >= 20 of 37 | 17. MISS |
| P2 | CAP4 MAIN ctx p50 <= 1.10x | 0.997x. HIT |
| P3 | no arm reaches +6 on MAIN | all arms are negative (-2 to -3). HIT |
| P4 | CAPFACT >= CAP4 on ST | 80 = 80. HIT (tie) |
| P5 | LEAD adds <= 2 MAIN facts over CAP4 | +0. HIT |

## Reads
- The diagnosis of the 37 was made on cut 7. On SEFIX-124, the head pass and the budgeted dense appends already put the found article's fact chunk in context on 18 of the 37. A larger or smarter per-article cap moves the same chunks from "appended" to "raw" and adds no new ones. The extra siblings it adds displace other articles, and on MAIN that costs facts, one of them on a health item.
- Within-article vector choice does not reach the 20 cap-cut items left unkept under CAP4 either: their fact chunk is in raw on 3 (dropped by the keep step) and in wide-12 on 4. The other 16 never pass the relevance gate and per-pack limit, even with the article found. Relaxing those is a gate change (R44 / R47 territory), outside this criterion.
- The lead header (ORACLE ONLY shape) adds +1 ST fact chunk (factbook-009, where the fact chunk is the article lead) at +3.5 % ST context. It is no lever on its own.
- Verdict: **NO** (stage 0). The "article found, wrong chunk" class is closed for the cap lever on the SEFIX-124 stack.

## Files
ARTCAP-criterion.md + .sha256, artcap.json (per-arm metrics, gained/lost ids, cap-37 lists, by pack), tools/ (replay-artcap.ts, replay-artcap-mini.ts, run.sh, run_mini.sh, chain.sh, chain2.sh, chain_mini.sh, score.py), replays/ (gitignored; mini copies under replays/mini/). Commands: tools/run.sh <main|st> <label> [RS_ARTCAP=...] on the MacBook, tools/run_mini.sh on the mini, then python3 -I tools/score.py.
