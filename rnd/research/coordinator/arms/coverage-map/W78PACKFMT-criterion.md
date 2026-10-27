# W78-PACKFMT criterion (frozen before any replay; 0 LLM, 0 judge, 0 Opus, 0 paid, 0 phone; MacBook replay only)
Date 2026-10-23. Follows W78C (criterion f26642ca, IVF32 ADOPT-CANDIDATE: 96/97 kept identity, 42/42 facts, 0 health, 20.85 MB/q whole kit) whose replay still
loads the whole int8 lead matrix of each pack (103.9 MB resident) and only scans the probed lists. Question: with the lead vectors stored list-ordered inside the pack
(new tables, format-2 additive) and a reader that fetches only the probed lists, is the stage-1 result unchanged while bytes read and resident memory drop?

## Layout (in-pack, additive; published packs untouched: copies under kiln-local/w78pf-packs/, same basenames)
Builder w78/tools/pack_ivf.py copies a pack and adds, from the same spherical k-means as W78C build_ivf.py (k 256, seed 42, 25 Lloyd iterations; asserted equal to the
W78C .ivf256 sidecar lists):
- lead_ivf(list_id INTEGER PRIMARY KEY, n INTEGER, ids BLOB int32[n], vecs BLOB int8[n x dims]) : one row per list, members in ascending article_id;
- lead_ivf_cent(id INTEGER PRIMARY KEY, k, dims, cents BLOB float32[k x dims], counts BLOB uint32[k], pages BLOB uint32[k]) : centroids + the list table
  {list_id -> rowid (offset), count} + the SQLite pages each lead_ivf row occupies (leaf + overflow, from dbstat);
- meta key leadIvf (JSON: k, dims, seed, iters, source sidecar sha). lead_vecs and every other table are kept byte-identical.
Applied to simplewiki (208,622 rows) and qa-travel-se (42,307 rows), the two packs W78C put under IVF; the 5 small chunk_vecs packs keep the exact scan.

## Reader (W78-PACKFMT.patch on top of rs-W78 = rs-SEFIX + W78-BINARY + W78B-DENSE + W78C-DENSE; wikiPack.ts only; RS_DENSE_IVFP=<nprobe>, default off)
First call per pack: read lead_ivf_cent (resident: centroids + counts + pages). Each call: cosine to the k centroids, the nprobe best lists (ties: lower list id),
SELECT ids, vecs FROM lead_ivf WHERE list_id IN (...), member rows merged in ascending article_id, exact int8 cosine with the W78C arithmetic (norm = float32
sqrt of the int8 sum of squares), top 50. The pack's lead matrix is never loaded on this path; a pack without lead_ivf falls back to the exact scan.

## Arms (MAIN 97, the W78C recipe: run_w78c.sh, SEFIX-124 13-pack N10 kit, F1 through W78 binary RS_SE_LEAD_BIN 32 in every arm)
- IVF32 : W78C arm rerun on this tree (RS_DENSE_IVF=32, sidecar + full resident matrix), published packs. Reference for RSS.
- PF32  : RS_DENSE_IVFP=32 over the pack copies (simplewiki + travel replaced by the copies in --packs, same basenames).
- B     : all exact (run_w78c.sh B 0), reported only.

## Metrics
1. Stage-1 bytes read per retrieving question (86), whole kit: for PF32 = sum over calls of (pages of the probed lead_ivf rows x page size 8192) + centroids
   k x dims x 4 counted at every call (conservative, = W78C accounting) + exact-fallback packs rows x 384 + F1 binary bytes from RS_SE_LEAD_LOG. Also the payload
   bytes returned by SQLite (ids + vecs) per question. IVF32/B: W78C accounting from RS_DENSE_LOG.
2. Stage-1 RSS growth (the part the layout controls; absolute process RSS is dominated by the embedder and V8 and is reported only): process.memoryUsage().rss
   logged before and after every stage-1 call; growth at first query = rss after the last stage-1 call of the first retrieving question minus rss before its
   first stage-1 call. Measured in the cold-start runs (metric 5), median of 3 fresh processes per arm; also reported for the full 97 replay (rss after the
   last call minus before the first).
3. Stage-1 scan ms per question (load excluded) and load ms; replay ms/q (reported, not gated).
4. Kept identity (chunk ids of keptFull, order-sensitive) of PF32 vs the W78C IVF32 replay (w78/replays-c/main.IVF32.jsonl) /97; chunk-level delivered facts on
   MAIN 92 (coverage-map/tools/chunklevel.py score(), W78 rule) of B's 42; health items changed vs B (W78C definition); stage-1 article lists identical to the
   W78C IVF32 denselog per call.
5. Cold start: fresh process (replay-sweep --ids <the first MAIN 97 item in file order that retrieves>), one question; bytes read, stage-1 ms incl. load (first
   call per pack), RSS growth; 3 fresh processes per arm (IVF32, PF32, B), medians.
6. One-off build seconds per pack (k-means + assignment, table write + dbstat page map; the file copy reported separately) and added bytes per pack.

## Decision rule (frozen)
ADOPT-CANDIDATE iff PF32 kept lists identical to the W78C IVF32 replay on 97/97 (hence 96/97 vs B) AND facts 42 of B's 42 AND 0 health items changed vs B AND
whole-kit bytes read <= 25 MB per retrieving question (metric 1) AND median cold-start stage-1 RSS growth of PF32 <= 0.3 x that of IVF32 (metric 2/5); else NO.
Nothing here judges answers; a candidate still needs a phone read.
