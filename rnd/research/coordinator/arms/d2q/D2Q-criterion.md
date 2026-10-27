# D2Q criterion: doc2query at pack build time on boar-factbook (frozen 2026-10-23 before any generation; never edited after)

Direction (r4to 15:3x): no model change; make the right content reach the small model; we build the packs. Prior on this idea: MICROD2Q (10-14, cut 7 engine, 9 packs, 5,975 target chunks, 4B Metal) FAIL by its rule: index-only column factbook article kept 5 -> 7, X2 (gate + onTopic see the questions) pooled chunk kept 35 -> 43 of 180, no gain on lexical misses. This run asks the narrower question on the adopted SEFIX-124 stack, on the worst pack by PACKPROOF (boar-factbook correct-any ON 0.25, own article kept 9/20 in the live run and 9/20 in the NOWIKI K13 replay).

## Generator (local, no paid API, no Haiku for generation)
- Mini (M4 16 GB), llama-server b11010 (<runner>/spikes/llama-b11010/build-cpu/bin/llama-server, CPU build: the only b11010 build on the mini), model <runner>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf (present on the mini; sha recorded in D2Q.md), own port 8131, -np 4 -c 8192 -t 8, --reasoning off not needed (instruct model). Inside a kiln slot lock (<runner>/kiln/slots/gen1|gen2, same protocol as mini_gen_multi.sh), never touching Docker, ollama or :8094; disk >= 25 GiB checked before start.
- One chat request per chunk, user message only, exactly:
  `Write 4 short questions a user might ask that this passage answers; one per line; use the passage's key terms.\n\nTitle: {title}\nSection: {section}\nPassage:\n{text}`
  where title = article title, section = the engine's sectionAt heading path ("" when none), text = article text slice(start, end).trim() (as WikiPack.hit).
- Sampling: temperature 0.7, top_p 0.8, top_k 20, seed 42, max_tokens 160, 4 requests in flight.
- Parse: split on newlines, strip leading numbering/bullets/quotes, drop empty lines, lines with CJK characters and lines under 3 words; keep the first 4. No cosine or inflation filter.
- 3 filled-prompt examples (inputs only; outputs are reported in D2Q.md): chunk 0 of Kyrgyzstan (Key facts block), a People and Society chunk of Malta, a random-sample chunk of another country (the first random chunk in the seeded list).

## Chunk set
boar-factbook (v3proto build, the K13 copy, sha 4ce447e8...) has 10,543 chunks (> 6,000), so the run is capped: all chunks of the 22 own articles of the 20 factbook self-tests (20 sources + partners Seychelles, Ireland; 876 chunks) plus random.Random(42).sample of 2,000 of the other 9,667 chunk ids (sorted id list) = 2,876 chunks. The other 7,667 chunks get an empty questions field. Caveat declared now: the own articles all carry questions while most competitor chunks inside factbook do not, so within-pack competition is favoured (an upper bound for a full build).
Budget rule: if the measured speed after the first 100 chunks projects > 5 h for the set, the random part is cut to the first 1,000 of the seeded list (declared now, applied mechanically).

## Pack variant boar-factbook-d2q
Copy of the K13 boar-factbook.sqlite at kiln-local/d2q-packs/boar-factbook.sqlite (same filename so the pack id is unchanged), plus fts_d2q(title, section, body, questions) (title/section/body rebuilt exactly as the builder, fidelity = per-column token counts equal to fts on every row) and d2q(chunk_id, q). Everything else byte-identical (articles, chunks, blocks, df, lead_vecs, chunk_vecs, meta). No per-chunk vector over title + questions: the dense path reads chunk_vecs/lead_vecs built by the bge embedder in the pack builder, and adding a second vector set needs an engine stage change; FTS only (said in D2Q.md). Not in shared-data, not published.

## Engine
kiln-local/rs-D2Q = copy of rs-SEFIX + d2q switch RS_D2Q (default off; port of MICROD2Q's d2q.vs-cut7.patch to the SEFIX tree): x1 = bm25Candidates and the gidf per-term rescore read fts_d2q with weights [title, section, body, 1] when the pack has it (the gidf ratio denominator counts rows on fts_d2q so its own idf cancels; global df unchanged from fts); x2 = x1 + the relevance-gate coverage and onTopic also read the chunk's questions (never shown in the prompt). Identity check: RS_D2Q unset on the d2q kit = K13 on rs-SEFIX (MAIN 97 kept ids and codes vs coverage-map/sefix/replays/main.F1F2F4.jsonl; 180 self-test kept ids vs nowiki/replay st.K13.*).
Driver: retrieve-sweep/tools/replay-sweep.ts, SEFIX-124 env (RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1), settings packHeadPass a2 + packDense2 append-budget, qwen3-1.7b-q4km, --cpu-embed --wide 12, same requests and tasks-from files as NOWIKI (main + st groups). MacBook, 0 LLM.

## Sets and measures
- 20 factbook self-tests (in on-k13 group; all 180 replayed for health and crowding): own article in raw (rawFull), own article kept (NOWIKI own_kept rule: pack boar-factbook, url + title of an own.json article), own fact chunk kept (normalised in_pack_facts quote substring of a kept factbook chunk body, any quote).
- MAIN 97: chunk-level facts (chunklevel.py score, base 42), kept-set changes, health losses (NOWIKI health() rule over MAIN and the 180), crowding share = items with >= 1 factbook chunk kept (base vs arm).
## Gate (0 LLM), on the primary arm X1; X2 reported with the same gate
factbook own-article kept >= base + 6 of 20 (base = rs-D2Q off replay, expected 9) AND MAIN chunk-level facts >= 42 - 1 = 41 AND 0 health losses.
If X1 passes, stage 2 uses X1; if only X2 passes, stage 2 uses X2 and the verdict carries "X2 (gate-side read)".
## Stage 2 (only if the gate passes)
PACKPROOF outcome labels (Haiku 5.5-low, N 1, blinded, same prompt and label.mjs as PACKPROOF) on the 20 factbook self-tests ON with the d2q pack (1.7B Succinct seed 42, SEFIX-124 tree + d2q switch, K13 with the d2q copy), compared with the PACKPROOF ON labels; cap 60 Haiku calls. Decision LEVER-CANDIDATE if correct-any rises >= +4 of 20 (PACKPROOF ON 5/20 -> >= 9/20); the OFF side is unchanged by construction (no pack, no new wrong-confident possible). Else NO-ANSWER-GAIN.
## Verdicts
Gate fail -> NO (doc2query does not make factbook findable on this stack). Gate pass + stage 2 >= +4 -> LEVER-CANDIDATE. Gate pass + stage 2 < +4 -> REACH-ONLY.
## Predictions (written before any generation)
P1 own-article kept X1: 9 -> 10..12 (gate fails at X1). P2 X2: 9 -> 11..13. P3 own fact chunk kept rises more than article kept (+2..+4), because the question terms ("capital", "population", "elevation") select the right chunk inside an article that already competes. P4 MAIN facts 42 +/- 1, 0 health losses (factbook rarely competes on MAIN). P5 crowding share of factbook on MAIN rises by <= 3 items. P6 generation 1.5-3 s/chunk on the mini CPU with -np 4 (1.2-2.4 h for 2,876 chunks). P7 the main failure mode is cross-pack crowding: vital5, simplewiki and the SE packs hold the same country names, so a better factbook score inside its own pack does not reach the 6-slot kept list.
## Never
Edit this file after freezing; read blind/, rnd/veil/, boar-eval/bench/v0.4; touch wt/engfix, rs-ARTCAP, rs-PACKSHAPE; publish or push.
