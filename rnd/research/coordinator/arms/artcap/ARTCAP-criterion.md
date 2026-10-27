# ARTCAP: when a pack article is found, does letting it bring more (or better-chosen) chunks put the fact chunk in the model's context? (frozen 2026-10-23, research agent, before any replay)

## Question
NEXT-RETRIEVAL-ARMS (h8st/tools/diag/diag137.json) classed 37 of the 137 unreached self-test items as "fact chunk in the pack's BM25 top-80 but cut by the per-article cap 2" and 19 as "article found via other chunks, fact chunk rank > 80". The cap lives in WikiPack.bm25Candidates (perArticle = 2). This arm changes only how many chunks a found article may contribute and which ones; the relevance gate, the per-pack limit (k), the fusion topK, compressContext, onSubject/health grounding and the SEFIX-124 append path (head pass a2 + packDense2 append-budget + F1 seLead) stay as they are.

## Arms (one env switch RS_ARTCAP, bench-only, absent = byte-identical to SEFIX-124)
Implementation point: WikiPack.searchDetailed, keyword candidates. With the switch on, bm25Candidates is read uncapped and re-grouped: an article keeps its BM25-best chunk at its own rank, and its other slots (cap - 1) follow it immediately, chosen by the within-article ranker; later siblings of that article are dropped. Same per-pack limit, same gate per chunk (coverage(title+text) >= 0.5 or article lead cosine >= 0.7), same nearDuplicate check. Within-article ranker: packs with chunk_vecs = cosine of every chunk of the article (excluding the first) to the question vector; packs without chunk_vecs = the article's other BM25 pool rows in score order. Grouping applies to the first 12 distinct articles of the candidate list; later articles keep the base cap-2 rank order.
- base = SEFIX-124 (rs-SEFIX recipe: RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1, settings packHeadPass a2 + packDense2 append-budget), run on kiln-local/rs-ARTCAP with the switch absent.
- CAP4 = RS_ARTCAP=cap4: cap 4 (3 extra slots per found article).
- CAPFACT = RS_ARTCAP=capfact: cap 2; the second slot is the within-article ranker's best instead of the BM25 second.
- CAP4+LEAD = RS_ARTCAP=cap4lead: CAP4, plus after the append path one short header chunk (article title + first sentence of the article's lead chunk, <= 240 chars) for the article of the first kept passage from a non-kit format-2 pack, when that lead chunk is not already kept; health-strict questions keep it only if it passes onHealthTopic; never on multi-pass.

## Fixed inputs
- Tree kiln-local/rs-ARTCAP = copy of kiln-local/rs-SEFIX + arms/retrieve-sweep/patches/ARTCAP.patch (sha recorded in ARTCAP.md). rs-SEFIX, wt/engfix and every other rs-* tree untouched.
- MAIN 97: questions decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl, tasks funnel-K3 traces, 13-pack kit compose/tools/kits.py 10, Qwen3-1.7B entry, wide 12 (sefix/tools/run_main.sh / qrewrite/tools/run.sh recipe). Scorer: coverage-map/tools/chunklevel.py score() (92 keyed).
- ST 180: packproof/in/{on-k13, on-k13+qa-bitcoin-se, on-k13+qa-ethereum-se}.requests.jsonl with their gen traces (qrewrite/tools/run.sh st recipe). Fact chunks: oracle-st/tools/oracle-facts.json fact_chunks (ids verified 318/318 inside the own article in the v3proto packs). Own article: packproof/in/own.json docId rule (qrewrite score.py).
- Driver: arms/artcap/tools/replay-artcap.ts = copy of qrewrite/tools/replay-qrw.ts (no map = the plain replay).
- Identity (required before any arm read): switch absent on rs-ARTCAP = sefix/replays/main.F1F2F4.jsonl on 97/97 raw titles and kept chunk ids, and = qrewrite/replays/st.base.jsonl on 180/180 kept chunk ids. Failure -> fix the patch, never read arm numbers first.

## Metrics
- MAIN: chunk-level facts /92 (base 42), gained / lost ids, health-family losses (ids lan-hlt-, vit-hlt-, dng-), kept lists changed (chunk ids), kept-context tokens = sum over kept chunks of ceil(len(title + body) / 4), p50 over items with >= 1 kept chunk and the total, arm / base.
- ST 180: fact chunk in kept (any oracle fact_chunk id in keptFull; base on the qrewrite replay = 77), fact chunk in raw, own article kept (base 100), gained / lost, health-pack losses (qa-health-se, boar-firstaid-en, boar-medlineplus-en), same context ratio.
- The 37 cap-cut items and the 19 other-chunk items (diag137 classes article_cap / article_found_other_chunk with S_kept_ST2 false): fact chunk kept under each arm, listed.

## Gate (stage 0, 0 LLM) - per arm
PASS iff (MAIN chunk-level >= 48, i.e. >= +6 over 42, OR ST fact-chunk-kept >= base + 25) AND MAIN health-family losses = 0 AND MAIN kept-context p50 <= 1.15 x base. ST health-pack losses and ST context are reported, not gating.
Stage-2 arm = the passing arm with the largest MAIN gain (ties: larger ST gain, then smaller MAIN context). No arm passes -> verdict NO at stage 0, no generation, no judge.

## Stage 2 (only if an arm passes)
Generation on the mini under the kiln lock (SEFIX ans-tools/run_124_gen.sh pattern + ARTCAP.patch as a third patch; the arm's RS_ARTCAP in the env file), Qwen3-1.7B, Succinct, seed 42, MAIN 97. Judge: Haiku 5.5-low judge.v1-low N 4, both orders, the changed MAIN items only (answer text differs from SEFIX-124 s42), divergence-first (items whose kept chunk ids changed first), cap 300 calls; base rows reused from the SEFIX-124 s42 cache keyed by (id, text). Decision: LEVER-CANDIDATE iff better >= worse + 3 AND no new confident error on a health-family item; else NO. One generation, no rerun except an infrastructure error before the first token.

## Predictions (written before any replay)
- P1 CAP4 has the fact chunk kept on >= 20 of the 37 cap-cut items (base on SEFIX-124: 18 of 37 already, via the head pass / dense appends).
- P2 CAP4 kept-context p50 <= 1.10 x base on MAIN.
- P3 no arm reaches +6 on MAIN (the cooking/money SE packs have no chunk_vecs, so CAPFACT is inert there and CAP4 adds BM25 siblings only).
- P4 CAPFACT >= CAP4 on ST fact-chunk-kept (better choice beats more slots under the same limit).
- P5 CAP4+LEAD adds <= 2 MAIN facts over CAP4 (the header rarely holds the fact).

## Budget and rules
0 paid API. MacBook replays only for stage 0 (sequential, shared replay cache). Mini only under the kiln lock, never touch Docker / ollama / :8094 beyond the detector use the gen script already makes, disk >= 25 GiB. Haiku <= 300, Opus 0. Never read blind/, rnd/veil/, boar-eval/bench/v0.4. This file is not edited after its sha is recorded.

## Outputs
arms/artcap/{ARTCAP.md (cites this sha), ARTCAP-criterion.sha256, artcap.json, aggregates/, tools/}; replays/ gitignored; patch arms/retrieve-sweep/patches/ARTCAP.patch + .sha256; one QUEUE row.
