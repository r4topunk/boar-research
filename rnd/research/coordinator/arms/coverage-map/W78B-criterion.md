# W78B criterion (frozen before any replay; 0 LLM, 0 judge, 0 Opus, 0 paid, 0 phone; MacBook replay only)
Date 2026-10-23. Extends W78-BINARY (W78-criterion.md e9d5e44a, ADOPT-CANDIDATE N = 32 for the SEFIX F1 scan) to the two parts it did not cover.
Tree = kiln-local/rs-W78 (rs-SEFIX + W78-BINARY.patch) + W78B-DENSE.patch (arms/retrieve-sweep/patches/W78B-DENSE.patch). The patch is written before any replay but changes
nothing while its switches are unset; B arms below prove it (identity vs the W78 B replay).

## What packDense2 reads (stated before the run, from wikiPack.denseChunks in rs-W78)
Stage 1 of denseChunks (every pack that carries chunk_vecs, i.e. the v3proto copies; all calls of packDense2 true / "extra" / "append" / "append-budget" go through it): full int8 LEAD-vector
matrix (lead_vecs, 384 B per article) scanned by exact cosine, top m = DENSE2_ARTICLES = 50 articles by cosine (no tau, ties: lower row), then stage 2 scores only those articles' chunk_vecs.
In the MAIN 97 kit (compose/tools/kits.py 10, 13 packs) the packs with chunk_vecs are simplewiki 208,622 rows, qa-travel-se 42,307, qa-outdoors-se 5,872, qa-health-se 5,048,
firstaid 1,842, medlineplus 1,016, factbook 261 (264,968 rows = 101.75 MB int8 if every pack is scanned per question). Cooking and money (F1) have no chunk_vecs and are not scanned by denseChunks.
Switch W78B: RS_DENSE_BIN=N (+ RS_SE_LEAD_BIN_DIR, the W78 sidecar dir): Hamming top-N of sign(query) over the 1-bit sidecar (W78 format, 48 B/article), exact int8 cosine of only those N rows,
then the top min(50, N) of them by exact cosine (same arithmetic, same tie rule) replace the stage-1 top-50. N is the number of Hamming candidates, so at N = 32 the stage-2 pool is at most 32 articles
(not 50): a real, not only numerical, difference from base, measured as is. Stage 2 and everything after are unchanged. A pack without a sidecar falls back to the exact scan.

## Arms
Part A (MAIN 97, recipe sefix/tools/run_main.sh F1F2F4 as in W78: 13-pack N10 kit, gidf, RS_SE_LEAD 0.78, RS_SE_MAXDF 0.25, RS_KEEP_NOPROPER 1, packHeadPass a2 + packDense2 append-budget, funnel-K3 traces):
- B   : both switches unset. Identity gate: B kept ids AND reason codes = w78/replays/main.B.jsonl on 97/97 (else the W78 B replaces nothing and this B is the reference for part A; the gap is reported).
- D32, D64 : RS_DENSE_BIN = 32 / 64, F1 exact (isolates the packDense2 scan).  D128 = diagnostic only (not gated).
- K32, K64 : RS_DENSE_BIN = 32 / 64 plus RS_SE_LEAD_BIN = 32 (the whole kit through the binary path = what the phone would run).
Part B (the 216 QFORM items of factbook / firstaid / medlineplus, arms/retrieve-sweep/g-chunkvecs/q3.jsonl, kit = the three v3proto packs shared-data/packs/v3proto/boar-{factbook,firstaid-en,medlineplus-en}.sqlite,
same tool replay-sweep.ts, gate search, --cpu-embed, --wide 12, no --tasks-from, tree rs-W78, no env except the switches), one run per mode M:
- M = "true" (settings {"packDense2": true}) and M = "extra" (settings {"packDense2": "extra"}), the two arms of RETRIEVE-SWEEP Arm G.
- B_M : RS_DENSE_BIN unset.  N32_M, N64_M : RS_DENSE_BIN = 32 / 64.  N128_M = diagnostic only (not gated).

## Metrics
1. Bytes scanned per question: per pack and summed over the kit; exact = rows x 384; binary = rows x 48 + (rescored rows) x 384. Whole-kit total per retrieving question = F1 scan bytes + denseChunks stage-1 bytes
   (B vs K32 / K64), from the RS_SE_LEAD_LOG and the new RS_DENSE_LOG lines (calls per question stated). Resident RAM of the cached matrices, sidecar bytes on disk per pack, first-load bytes.
2. Stage-1 scan ms per call (mean, p50; load excluded) and replay ms/q (reported, not gated; MacBook noise +-10 %).
3. Kept identity vs B per item (chunk ids, order-sensitive), and stage-1 article-set agreement per call (diagnostic).
4. Part A: chunk-level delivered facts on MAIN 92 (coverage-map/tools/chunklevel.py score(), the W78 scorer rule), of B's 42; health items changed.
5. Part B: QFORM "found" = the verbatim gold quote (items/facts.json gold.quote, normalised: lowercase, punctuation stripped, whitespace collapsed) is contained in the title+body of a chunk of keptFull
   (qform/tools/matrix.py hit_kept rule, quote branch only: merged chunk ids do not exist in the v3proto packs), counted per form (n 24 per form, 216 total) and pooled, per mode, vs B_M. Also raw and wide-12 found (diagnostic).
   Sanity: B_true and B_extra pooled found are compared with the Arm G numbers (69 and 78 of 216); a difference is reported, B (this tree) stays the comparison base.
Health item = any item whose B or arm reasonCodes contain a code starting "grounding:health" or "instant:off-health"; changed = kept chunk ids differ.

## Decision rule (frozen)
Gate for an N in {32, 64} (both parts must pass at the same N):
 Part A (arms D_N and K_N, each): (a) of B's 42 chunk-level delivered items, 42 still delivered (no loss); (b) 0 health items changed; (c) kept ids identical to B on >= 93 of 97 items (>= 95 %);
          (d) whole-kit stage-1 bytes per retrieving question: K_N total <= 0.25 x B total.
 Part B (arms N_M for M in {true, extra}, each): (e) kept ids identical to B_M on >= 206 of 216 items (>= 95 %); (f) QFORM found count within -1 of B_M in EVERY form (arm >= B_M - 1 per form of 24);
          (g) 0 health items changed (QFORM health items by the definition above); (h) denseChunks stage-1 bytes per question over the 3-pack kit <= 0.25 x B_M.
ADOPT-CANDIDATE = the smallest N in {32, 64} that passes all of (a)-(h); report its identity, found deltas, bytes, ms. NO = neither passes (the loss is then reported per gate, with the failing item ids).
A pass in one part only is reported as such (verdict stays NO overall). Nothing here judges answers; an ADOPT-CANDIDATE still needs a phone read. All items are dev (MAIN 97, QFORM agent-written); no blind/, veil/, v0.4 file is read.
