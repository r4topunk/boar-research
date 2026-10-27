# FMT1-SCAN criterion (frozen 2026-10-23 before any replay; never edited after)
Question: in format-1 packs the semantic step only re-ranks the bm25 top-400 FTS5 pool (packs.ts PACK_CANDIDATES) and the relevance gate drops chunks under cosine 0.70 (pure.ts ANSWER_MIN_SIMILARITY). Does a larger pool or a full chunk-vector scan, with or without a 0.65 floor for format-1 pack chunks, deliver more facts without harm?
Scope note (checked before freezing): in the N10 13-pack kit the only format-1 pack is wiki-vital5 (115,813 chunks, 384-d int8); boar-simplewiki-en (v3proto) and boar-wiki-en-top100k are format 2 (formatVersion 2), so the arms act on wiki-vital5 only, on both sets. The bundled corpus keeps the 0.70 gate in every arm.

## Tree and switches
kiln-local/rs-FMT1 = cp -Rc kiln-local/rs-SEFIX + arms/retrieve-sweep/patches/FMT1-SCAN.patch (default off = byte-identical behaviour). Base recipe = SEFIX-124 (RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1, no F3).
- RS_FMT1_POOL: unset/400 = base; 2000 = the FTS5 pool for the semantic list is the bm25 top 2000 (the keyword list stays computed from the first 400 rows, unchanged); full = the semantic list is the top by cosine over ALL chunk vectors of the pack (vectors read once per process into memory; first-load ms logged separately and excluded from per-item ms), keyword list unchanged.
- RS_FMT1_FLOOR: unset = 0.70; 0.65 = the relevance gate for format-1 pack chunks (packs.lexical and packs.semantic) is 0.65; the bundled corpus stays at 0.70.
Arms (6): P400 (base), P400f65, P2000, P2000f65, FULL, FULLf65.

## Sets
- MAIN 97: sefix/tools/run_main.sh recipe (13-pack N10 kit, funnel-K3 traces, packHeadPass a2 + packDense2 append-budget, wide 12) with TREE=rs-FMT1 and the SEFIX-124 env. Scored on MAIN 92 (v0.1 52 + cm 40) with tools/chunklevel.py score() (chunk-level delivered fact).
- TOPICS 27: topics27/misses/run.sh recipe (wiki-vital5 only + essential corpus, persona detailed) on rs-FMT1 with the SEFIX-124 env; base = that run (= MISSES A1).

## Identity checks (before reading any arm)
P400 on rs-FMT1 vs sefix/replays/main.F1F2F4.jsonl: raw, wide, kept chunk ids, reason codes on 97/97; P400 topics vs topics27/replay/misses.A1.jsonl on 27/27. A failure stops the arm reads until explained.

## Metrics (per arm vs P400)
1. MAIN 92 chunk-level delivered facts (count, gained/lost item ids, cm / v0.1 split).
2. TOPICS: recovered = a MISSES topic (b13 b15 b19 b20; expected titles as in misses/score.py EXP) whose kept list holds an expected title the base kept list lacks; changed = other 23 topics whose kept title list differs from base.
3. Kept-set changes per item (kept chunk-id set differs from base), both sets.
4. Health losses: MAIN = on health items (base reasonCodes hold a code starting "grounding:health" or "instant:off-health", or the id holds "-hlt-") any base-kept chunk from qa-health-se, boar-firstaid-en, boar-medlineplus-en or wiki-vital5 missing in the arm; TOPICS = on q2 q4 b2 b8 b13 b14 b21 any base-kept title missing in the arm.
5. Retrieval wall: the replay's per-item `ms` (first retrieve call), p50 / p95 over items with a retrieve call, per set; arms run sequentially on the MacBook.

## Gate (per arm)
LEVER-CANDIDATE iff
(a) MAIN chunk-level delivered >= base + 3, OR (topics recovered >= 2 of 4 AND changed <= 2 of the other 23); AND
(b) health losses = 0 on both sets; AND
(c) retrieval p95 <= 2 x base p95 on each set.
Otherwise NO. 0 LLM, 0 judge, 0 paid, 0 phone. Never reads blind/, rnd/veil/, boar-eval/bench/v0.4.
