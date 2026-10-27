# NOWIKI (2026-10-23; 0 LLM / 0 judge / 0 Opus / 0 paid / 0 phone; MacBook replays only): KEEP. Dropping Wikipedia costs 9 MAIN facts and 10 v0.1 items, and the small packs gain only +3 of 160

**Leitura para o r4to (PT-BR):**
1. Os packs pequenos sozinhos entregam 33 de 92 fatos no MAIN, contra 42 com Wikipedia. O lado cooking/money fica igual (cm 14 e 14; 16 no NOWIKI2). Quem perde é o lado geral v0.1: 28 viram 19, e 10 itens perdem o fato (lan-rsn x5, lan-exp-005, lan-cmp-004, lan-hlt-003, vit-hum-004/005).
2. O alívio de crowding existe, mas é pequeno: own-article kept nos 160 self-tests dos packs que ficam passa de 82 para 85 (+3; +4 no NOWIKI2). O factbook ganha +4 e o medlineplus +2. Travel, health e firstaid perdem 1-2 cada, e 2 self-tests de saúde perdem a fonte de saúde (firstaid-001, medlineplus-015 no NOWIKI2). Os 20 itens do simplewiki caem de 18 para 0.
3. O custo da Wikipedia é este: o kit lê 125 MB por pergunta, e sem ela lê 45 MB (só o scan do simplewiki pesa 80 MB). A busca leva 959 ms, contra 651 sem a Wikipedia e 536 sem Wikivoyage também. Em disco, o kit tem 1.85 GB, e cairia para 0.95 GB ou 0.60 GB. Com o stack W78 (IVF32) já adotado, o kit com Wikipedia cai para cerca de 21 MB por pergunta, então o custo de bytes já está resolvido por outro caminho.
4. Recomendação: o default fica K13 (KEEP). Os packs pequenos não buscam melhor sem a Wikipedia: o ganho de +3 está dentro do ruído de reordenação, e a perda de conhecimento geral é real. Nos 27 Research Topics, sem a Wikipedia só 11 de 27 mantêm o artigo esperado, contra 25 com o K13.

Criterion ../NOWIKI-criterion.md sha256 `5d40edcd6edc7008edfad86cd84f6abde3b7f6e95c1f14637ab5265e998095d7` (frozen before any replay, not edited). Tree kiln-local/rs-SEFIX read-only, SEFIX-124 env (gidf, SE_LEAD 0.78, SE_MAXDF 0.25, KEEP_NOPROPER 1, F3 off). Data: nowiki.json; replays in replay/ (gitignored).

## Commands
```
cd <workspace>/rnd/research/coordinator/arms/coverage-map/nowiki
tools/batch.sh        # = tools/run.sh main K13|NOWIKI|NOWIKI2 (sequential, timed), then st <kit> on-k13|on-k13+qa-ethereum-se|on-k13+qa-bitcoin-se, t27 <kit>
python3 -I tools/score.py    # -> nowiki.json
```
Kits are built by tools/kits.py (= compose kits.py kit(10) minus the dropped files). Identity: the K13 MAIN replay matches sefix/replays/main.F1F2F4.jsonl on kept chunk ids 97/97 and reason codes 97/97. Self-test K13 kept titles match the live PACKPROOF ON traces on 174/180.

## The 3-kit table
| set / metric | K13 (base) | NOWIKI (-simplewiki -vital5) | NOWIKI2 (also -wikivoyage) |
|---|---|---|---|
| MAIN chunk-level delivered /92 (gate >= 40) | **42** | **33** | **32** |
| cm /40 / v0.1 /52 | 14 / 28 | 14 / 19 | 16 / 16 |
| article-level /92 | 50 | 40 | 39 |
| v0.1 items losing the kept fact (gate <= 3) | - | **10** | **12** |
| MAIN items with a changed kept set /97 | - | 58 | 63 |
| MAIN health items changed / losses (of 11) | - | 1 / 0 | 3 / 0 |
| self-tests own article kept, 160 (packs installed in every kit; gate >= +5) | 82 | 85 (**+3**) | 86 (**+4**) |
| self-tests simplewiki 20 (own pack removed) | 18 | 0 | 0 |
| self-tests own article kept /180 | 100 | 85 | 86 |
| self-test health losses (of 27 health items) | - | 1 (firstaid-001) | 2 (firstaid-001, medlineplus-015) |
| 27 topics: expected/anchor kept (information) | 25 (vital5 only ref: 24) | 11 | 11 |
| 27 topics health losses | - | 1 (q4: qa-health-se a52) | 1 (q4) |
| bytes read / retrieving question (exact int8, W78C) | 125.09 MB (stage-1 101.75 + F1 23.35) | 44.98 MB (21.64 + 23.35) | 44.98 MB |
| vital5 format-1 pool re-rank (upper bound) | +0.15 MB | 0 | 0 |
| pack bytes on disk | 1.85 GB (13 packs) | 0.95 GB (11) | 0.60 GB (10) |
| retrieval ms p50, MAIN (timed) / 180 / 27 | 959 / 863 / 688 | 651 / 627 / 491 | 536 / 549 / 470 |

Per pack, own article kept (K13 -> NOWIKI -> NOWIKI2): travel 17/15/16, ethereum 10/11/11, bitcoin 7/7/7, health 11/10/10, outdoors 12/12/12, firstaid 6/5/6, medlineplus 10/12/11, factbook 9/13/13, simplewiki 18/0/0.

## Items that lose / gain
- MAIN NOWIKI lost (11): lan-rsn-001, -003, -004, -005, -006, lan-exp-005, lan-cmp-004, lan-hlt-003, vit-hum-004, vit-hum-005 (v0.1 10), st-qa-cooking-se-016 (cm). Gained: vit-hum-002, st-qa-cooking-se-006.
- MAIN NOWIKI2 lost (12): the NOWIKI v0.1 10 + lan-exp-001 and lan-ref-002, minus cooking-016. Gained: cooking-006, money-005.
- Self-tests NOWIKI gained 10: health-004, outdoors-016, medlineplus-009, -014, factbook-002, -004, -006, -011, -017, ethereum-018. Lost 7 (excluding simplewiki): travel-001, -019, health-002, -017, outdoors-006, firstaid-001, factbook-019. NOWIKI2 gained 11, lost 7 (lists in nowiki.json).

## Gate (frozen) and verdict
| clause | NOWIKI | NOWIKI2 |
|---|---|---|
| (a) MAIN delivered >= 40 | 33 FAIL | 32 FAIL |
| (b) v0.1 lost <= 3 | 10 FAIL | 12 FAIL |
| (c) self-test 160 relief >= +5 | +3 FAIL | +4 FAIL |
| (d) 0 health losses (MAIN + 180 + 27) | 2 FAIL | 3 FAIL |
**Verdict: KEEP** (no arm passes; no arm meets (c) and (d), so it is not KEEP-AS-OPTIONAL either). The recommended default kit stays K13.

## Reading
- Most of the MAIN loss is the reasoning and explain items (lan-rsn, lan-exp), whose facts sit in Simple English Wikipedia chunks. The cooking/money side does not move, because F1/gidf already lets those threads through.
- Crowding relief is real for factbook (+4) and medlineplus (+2), which compete with simplewiki for the same general topics. It is offset by reordering losses in travel/health/firstaid. The net +3 is about the size of the churn (92 of 180 kept sets change).
- The cost argument does not need the drop: W78C IVF32 + W78-PACKFMT take the K13 kit from 125 to about 21 MB per question at 96/97 identity. The remaining cost of Wikipedia is disk (0.9 GB) and about 300 ms of replay time per question on the MacBook.

## Caveats
Desktop replay (bench engine, not the native Kotlin path); 0 LLM, so kept chunks, not answers; dev items only; lexical chunk-level rule (lower bound); self-tests are agent-written from the packs; bytes are computed from the W78C B logs (pack rows x 384), not logged in these runs; ms is single-thread V8 on the MacBook, phone unpriced; wikivoyage lead vectors are outside the W78C accounting, so NOWIKI2 shows no byte change.
