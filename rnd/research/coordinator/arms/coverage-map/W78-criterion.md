# W78-BINARY criterion (frozen before any run; 0 LLM, 0 judge, 0 Opus, 0 paid, 0 phone; MacBook replay only)
Date 2026-10-23. Base = SEFIX-124 (gidf + F1 + F2 + F4, F3 off) = kiln-local/rs-SEFIX with RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1,
recipe sefix/tools/run_main.sh (13-pack N10 kit from compose/tools/kits.py 10, packHeadPass a2 + packDense2 append-budget, funnel-K3 traces, MAIN 97).
Reference replay = sefix/replays/main.F1F2F4.jsonl (chunk-level 42 of MAIN 92 in sefix/chunklevel-124.json).

## What F1 reads (as found in SEFIX-F1.patch, stated before the run)
F1 (wikiPack.rsSeLead) scans the full int8 LEAD-vector matrix (one 384-dim int8 vector per thread, table lead_vecs) of every Stack Exchange pack
WITHOUT chunk_vecs; in the SEFIX-124 kit that is qa-cooking-se (25,698 threads) and qa-money-se (35,102 threads) = 60,800 x 384 B = 23.3 MB per
question (the matrix is cached in RAM after the first query). It does not read chunk vectors. The task's "float chunk vectors" premise is therefore
replaced by: int8 lead vectors (exact path) vs 1-bit sign lead vectors (W78 path).

## Arms
- B = base rerun on kiln-local/rs-W78 (rs-SEFIX clone + W78 patch), RS_SE_LEAD_BIN unset. Identity check: B kept ids AND reason codes per item = reference, 97/97 (if not 97/97, B replaces the reference for every comparison and the gap is reported).
- W32, W64, W128 = RS_SE_LEAD_BIN=N: Hamming scan over a bit-packed sign sidecar (48 B/thread, one file per pack, built by w78/tools/build_leadbits.py from lead_vecs), top-N by Hamming (ties: lower row index), exact int8 cosine rescore of only those N rows (SELECT ... WHERE article_id IN), then the unchanged F1 rule (tau 0.78, 1 thread, positions 1-2).

## Metrics (per arm)
1. bytes scanned per question per pack = rows x 48 + N x 384 (W) vs rows x 384 (B); also resident RAM of the cached matrix; first-load bytes.
2. sidecar size on disk (MB) per pack.
3. retrieval wall: mean and p50 of the replay row "ms" over 97, and the F1 scan ms per call (RS_SE_LEAD_LOG instrumentation, load excluded).
4. chunk-level delivered facts on MAIN 92 (tools/chunklevel.py rule, score()).
5. kept-set identity vs B per item (chunk ids, order-sensitive) /97; F1 thread-pick agreement per call vs B.

## Decision rule (frozen)
Gate per arm: (a) of the 42 items delivered at chunk level by SEFIX-124 (B), >= 41 still delivered; (b) 0 health items changed
(health item = any item whose B or arm reasonCodes contain a code starting "grounding:health" or "instant:off-health"; changed = kept chunk ids differ);
(c) bytes scanned per question <= 0.25 x B.
ADOPT-CANDIDATE = the smallest N in {32, 64, 128} that passes (a)+(b)+(c); report its identity and ms. NO = no N passes.
Wall ms is reported, not gated (MacBook load noise +-10 %, SEFIX caveat). Nothing here judges answers; an ADOPT-CANDIDATE still needs a phone read.
