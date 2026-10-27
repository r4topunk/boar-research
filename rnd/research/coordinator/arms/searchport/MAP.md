# SEARCHPORT map: native retrieval (078a2627) vs the TS bench stack (kiln-local/rs-SEFIX, SEFIX-124)

TL;DR: the native engine is a port of an older TS retrieve/wikiPack with **no grounding/keep step and no health routing**: retrieve(k 4) -> Compress.forAnswer (450/700 tokens) -> prompt. Of SEFIX-124, H4 gidf, F2, F1 and HEADPASS a2 + X2b map onto native code (WikiPack.bm25Candidates / searchDetailed, Retriever.retrieveOne, a new post-compression step); F4 has no counterpart (nothing in the native path drops a source for a missing proper noun); the head pass's health filter (onHealthTopic) has no native counterpart (ported as: health questions get no appends). The APK bundle (stage-bundle.sh at 078a2627) already ships the v3proto builds with chunk_vecs for 6 packs; the dense path runs on them, not on crypto / wikivoyage / factbook v1 / cooking / money / visa.

## Pipelines side by side
| step | TS rs-SEFIX (ENGINE-RC, SEFIX-124 env + packHeadPass a2 + packDense2 append-budget) | native 078a2627 (AnswerPipeline PIPELINE path) |
|---|---|---|
| search query | english / action suffix / lexicon names (answer.ts l.1013) | FollowUp.search(query) |
| k | gen.retrieveK (lookup 3 / other 4 / deep 6) | 4 (ANSWER_CONTEXT_CHUNKS) |
| KB + format-1 | lexical + semantic, gateByRelevance 0.7, fuse | same port (Retriever.retrieveOne) |
| format-2 packs | searchWikiPacks: sequential; **H4 gidf** (RS_MERGE=gidf) global idf over all format-2 packs; **F2** (RS_SE_MAXDF 0.25) for SE packs without chunk_vecs; dense2 side lists | SearchPool parallel per pack, searchDetailed per pack, own idf |
| side lists | packDense2 "append": two-stage denseChunks (packs with chunk_vecs) + **F1** rsSeLead (SE packs without chunk_vecs, tau 0.78), attached beside the list (WeakMap) | none |
| PT second search | yes, side lists merged | yes (same structure) |
| substantive filter, pinning | isSubstantive, identifier pin | none |
| compression | compressContext(matchQuery, raw, budget ~1200) | Compress.forAnswer (lookup 450 / other 700) |
| grounding | onSubject keep (onTopic proper-noun rule; **F4** RS_KEEP_NOPROPER relaxes it); health-strict onHealthTopic + best-restored | **none** (every compressed passage is sent) |
| head pass | after grounding: X1 = positions 1-2 of the article of the first raw passage from a non-kit format-2 pack; F1 SE answers; X2 dense D 2; cap 4; budget 600 tokens of prompt chars; health: appends filtered by onHealthTopic | **none** |
| health routing | detector, health-strict, declines, cards, extractive | none at 078a2627 (fb6ffbf6 adds HealthGate after retrieval) |

## Piece by piece
| SEFIX-124 piece | native counterpart | port |
|---|---|---|
| H4 gidf (packs.ts searchWikiPacks + wikiPack.ts bm25Candidates rescoring) | WikiPack.bm25Candidates; Retriever.retrieveOne | ported: Retriever.globalStats (terms = union of each pack's portTerms, df summed, nRow summed) -> PackSearchOptions.global -> per-term one-term bm25 x idf ratio |
| F2 RS_SE_MAXDF 0.25 (SE packs without chunk_vecs) | WikiPack.queryTerms | ported: WikiPack.portTerms |
| F1 RS_SE_LEAD 0.78 (best SE thread, chunks 1-2) | none | ported: WikiPack.seLead + Result.seLead + SearchPort.Side |
| F3 | OFF in SEFIX-124 | not ported |
| F4 RS_KEEP_NOPROPER | no keep step in native | N/A (nothing to relax) |
| HEADPASS a2 (packHeadPass, headChunksOf) | none | ported: WikiPack.headChunksOf + SearchPort.headPass, kit = boar-crypto, boar-wikivoyage-en |
| HEADPASS-X2b (denseChunks, rankDense, pickDenseAppend, applyAppendBudget 600) | none | ported: WikiPack.denseChunks, SearchPort.rankDense / appendBudget; measure = chars of the chat messages (role + content) |
| head-pass health filter (onHealthTopic) | none (no healthTopicTerms / onHealthTopic in native) | replaced by: no appends on QueryContext.isHealthQuestion |

## Pack-format needs vs the APK bundle (stage-bundle.sh at 078a2627, factbook v1 per coordinator 18:2x)
| pack (catalog sha) | lead_vecs | chunk_vecs | SE | port path that runs |
|---|---|---|---|---|
| wiki-vital5 d3b87d56 | format 1 | - | - | none (format 1) |
| boar-crypto ae9fbd2c | yes | no | no | gidf only (kit: no head pass) |
| boar-wikivoyage-en ff8595e3 | yes | no | no | gidf only (kit) |
| boar-factbook v1 c5854353 | yes | **no** (v3proto 4ce447e8 / shaped v2 have it) | no | gidf, X1 |
| boar-firstaid-en 0a7dffa6 (v3proto) | yes | yes | no | gidf, X1, dense |
| boar-medlineplus-en e805ccea (v3proto) | yes | yes | no | gidf, X1, dense |
| qa-health-se f1ba1a4b (v3proto) | yes | yes | yes | gidf, X1, dense (F1/F2 only for SE without chunk_vecs) |
| qa-outdoors-se 11bcb96f (v3proto) | yes | yes | yes | gidf, X1, dense |
| qa-travel-se ffdebe54 (v3proto) | yes | yes | yes | gidf, X1, dense |
| boar-simplewiki-en 99bcec30 (v3proto) | yes | yes | no | gidf, X1, dense |
| qa-cooking-se 81990fa9 (wave3) | yes | **no** | yes | gidf, **F2, F1**, X1 |
| qa-money-se 37411234 (wave3) | yes | **no** | yes | gidf, **F2, F1**, X1 |
| boar-visa-en d1dd0ffb (wave4) | yes | no | no | gidf, X1 |
Same chunk ids between the catalog builds and v3proto (chunks count/start/end sums identical; checked on qa-travel-se, qa-health-se, factbook), so the retbench ST fact-chunk ids apply to the native kit. This kit = the retbench K13 kit except factbook (v1 here, v3proto there).

## Memory note (phone)
The lead matrix is read once per pack that scans it (int8, 384 B per article): simplewiki 208,628 articles = 80 MB, qa-travel 16 MB, qa-money 13.5 MB, qa-cooking 9.9 MB, others < 5 MB: about 125 MB resident after the first ported question (the TS engine holds the same matrices). P2 (W78 PF32 in-pack IVF) is the reading-cost fix.
