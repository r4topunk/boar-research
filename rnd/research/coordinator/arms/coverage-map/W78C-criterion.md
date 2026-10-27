# W78C criterion (frozen before any replay; 0 LLM, 0 judge, 0 Opus, 0 paid, 0 phone; MacBook replay only)
Date 2026-10-23. Follows W78B (criterion e3279284, NO: the 1-bit sidecar cannot rank the packDense2 stage-1 top-50 tail; identity 82-86/97).
Question: does a 4-bit or 2-bit per-vector-scaled lead sidecar with an exact int8 rescore of the top N, or an IVF-256 coarse pre-filter over the int8 lead vectors, keep the
packDense2 stage-1 result (wikiPack.denseChunks, top m = DENSE2_ARTICLES = 50 articles by exact int8 lead cosine, no floor) while reading fewer bytes per question?

## Tree, switches, sidecars
Tree = kiln-local/rs-W78 (rs-SEFIX + W78-BINARY + W78B-DENSE) + W78C-DENSE.patch (arms/retrieve-sweep/patches/W78C-DENSE.patch, wikiPack.ts only, default off).
- RS_DENSE_Q=<4|2> + RS_DENSE_QN=<N> + RS_DENSE_Q_DIR: approximate score of every lead row from the quantised sidecar (per-row codes + one float32 row factor), the N best
  (ties: lower row), exact int8 cosine of only those N rows (same arithmetic as the exact scan), top min(50, N) by exact cosine (ties: scan order) replace stage 1.
  int4: per row scale = max|v|/7, code = round(v/scale) in [-7, 7] (4 bits, 2 per byte); int2: 4 levels (-3, -1, +1, +3) x step/2, per-row step chosen by a fixed grid search
  minimising squared error (2 bits, 4 per byte). Row factor = scale / ||v_int8|| (so the approximate score is a cosine estimate). Built by tools/build_leadq.py from lead_vecs.
- RS_DENSE_IVF=<nprobe> + RS_DENSE_Q_DIR: per pack a spherical k-means with k = 256 centroids over the L2-normalised int8 lead vectors (seed 42, init = 256 random rows, 25
  Lloyd iterations, each row assigned to its max-cosine centroid), built by tools/build_ivf.py; only packs with rows >= 39 x 256 = 9,984 get an IVF sidecar (faiss's minimum
  points per centroid; here simplewiki 208,622 and qa-travel-se 42,307 = 96.4 MB of the 101.75 MB); smaller packs keep the exact scan. At query time: cosine of the query to the
  256 centroids, the nprobe best lists, exact int8 cosine of their member rows in ascending row order (same tie rule), top 50.
- A pack without a sidecar falls back to the exact scan. Stage 2 and everything after are unchanged.
- Every arm runs the F1 scan through the W78 binary path (RS_SE_LEAD_BIN = 32, the adopt-candidate, lossless 97/97 in W78) so the arm is the whole kit the phone would run; B is all exact.

## Set and recipe
MAIN 97, the SEFIX-124 recipe exactly as W78B part A (w78/tools/run_w78b_a.sh: 13-pack N10 kit, gidf, RS_SE_LEAD 0.78, RS_SE_MAXDF 0.25, RS_KEEP_NOPROPER 1, packHeadPass a2 +
packDense2 append-budget, funnel-K3 traces, --cpu-embed --wide 12). No blind/, veil/, v0.4 file is read.

## Arms
- B : all switches unset. Identity check: B kept ids AND reason codes = w78/replays-b/main.B.jsonl (W78B B) on 97/97; if not, the gap is reported and this B is the reference.
- Q4-64, Q4-128 : RS_DENSE_Q = 4, N = 64 / 128.
- Q2-128 : RS_DENSE_Q = 2, N = 128.
- IVF8, IVF32 : RS_DENSE_IVF = 8 / 32 over int8.

## Metrics
1. Stage-1 bytes read per retrieving question (sum over the 7 chunk_vecs packs, from RS_DENSE_LOG, the W78B accounting): exact = rows x 384; quantised = rows x (code bytes + 4)
   + rescored rows x 384 (int4 196 B/row, int2 100 B/row); IVF = 256 x 384 x 4 (float32 centroids) + member rows read x 384; exact-fallback packs = rows x 384.
   Whole-kit bytes/q = stage 1 + F1 (binary 2.94 MB/q from W78, read from RS_SE_LEAD_LOG). Sidecar bytes on disk per pack, build seconds (the IVF k-means one-off cost incl. assignment).
2. Stage-1 scan ms per question (load excluded), replay ms/q (reported, not gated).
3. Kept identity vs B (chunk ids of keptFull, order-sensitive) /97.
4. Chunk-level delivered facts on MAIN 92 (coverage-map/tools/chunklevel.py score(), the W78 rule), of B's 42.
5. Health items changed (item whose B or arm reasonCodes contain a code starting "grounding:health" or "instant:off-health" and whose kept chunk ids differ).
6. Recall of B's exact top-50 articles per stage-1 call (mean over calls), and B's top-1 kept.

## Decision rule (frozen), per arm
ADOPT-CANDIDATE iff kept identity >= 93/97 AND chunk-level delivered 42 of B's 42 AND 0 health items changed; else NO.
Among ADOPT-CANDIDATE arms the report names the one with the fewest whole-kit bytes/q as best. Nothing here judges answers; a candidate still needs a phone read.
