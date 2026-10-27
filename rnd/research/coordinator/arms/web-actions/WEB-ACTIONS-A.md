# WEB-ACTIONS-A (2026-10-21 15:xx): 0-LLM actions from WEB-LOG-2026-10-21 ticks 5–23

0 LLM, 0 judge, 0 paid, no push. Not read: blind/, rnd/veil/, bench/v0.4 question text. boar-app/ not modified (wt/ and android-native read only).

## 1. T13.1 + T13.2: boar-crypto licence sources
- packs/boar-crypto.md had the licence list but no source URLs. Added one line: EIPs = CC0 1.0 (github.com/ethereum/EIPs/blob/master/LICENSE.md); ethereum.org non-code = CC BY 4.0, code MIT, "unless otherwise marked" (ethereum.org/en/terms-of-use/), incl. blog.ethereum.org and the per-chunk attribution note.

## 2. T13.3 + T14.2: FIPS 206 in the facts table
- Newest table: handoff/facts-r10-2026-10-21-0301/facts.v1.json (QUEUE 03:03, sha 307753ff; it exists, tick 14 looked for another name).
- Grep FALCON / Falcon / FIPS / FN-DSA / ML-KEM / ML-DSA / SLH-DSA / Kyber / Dilithium / SPHINCS / quantum: **0 hits**. r10 holds 4,233 Wikidata entities of kinds city, mountain, building, river, country, lake, dam + 1 award, 1 event, 1 other: no standards or PQ rows. CHANGES/AUDIT-r10: 0 hits.
- So no row marks FIPS 206 final, and no row carries 2024-08-13 for 203/204/205: **no fix needed** in facts.v1.json.
- Where PQ dates do live: the engine's PQ wiki fixture (wt/cut7/src/rag/testing/fixtures/pq-wiki.jsonl, read only) says FIPS 203/204/205 final on 2024-08-13 and FIPS 206 (FN-DSA) a draft "as of mid-2026", final expected late 2026 / early 2027: consistent with NIST (T13.3).
- Proposed row, only if a PQ standards kind is ever added (not now; the schema is Wikidata entities): `{"n":"FIPS 206","a":["FN-DSA","Falcon standard"],"k":"standard","status":"draft (not final as of 2026-10)","src":"https://csrc.nist.gov/projects/post-quantum-cryptography/post-quantum-cryptography-standardization"}` plus FIPS 203/204/205 rows with `"final":"2024-08-13"`.

## 3. T5.1 + T5.2 + T8.3 + T6.4: device-day pre-flight
- Appended "Pre-flight additions from the web log" to DEVICE-DAY-RUNSHEET-2026-10-22.md: meminfo split per 5 s (Private Dirty / Private Clean / Native Heap / .gguf mmap / SwapPss), battery level + charge counter µAh at start/end of every run, decode tok/s first third vs last third next to the p50.
- Load flags found: bench app `bench-app/engine/src/inference/LlamaEngine.ts` l.291–292 `use_mmap: true, use_mlock: false`; override `useMlock` exists (src/engineOverrides.ts) and was used once (litelat-05-mlock, bench.json use_mlock true). RC (android-native @ wt/native-qa 5f8cc8f4): default LoadMode.MMAP; preset "Run Boar Run" requests MMAP_MLOCK (code comment: Android grants 0 MB locked on the X6). Never enable mlock.

## 4. T18.2: CRAG-style truthfulness (written to RESEARCH-PAGE-OUTLINE §5 update)
| tier | refuse-by-default, Opus | show-all, Opus (est.) | refuse [Haiku] | show-all [Haiku] |
|---|---|---|---|---|
| 4B | 21.7 | 40.7 | 14.4 | 10.3 |
| Gemma E2B | 23.7 | 27.9 | 12.3 | 8.2 |
| 1.7B | 16.5 | 24.3 | 12.4 | 0.0 |
- correct − CE per 100, declines and partials 0; MAIN 97 dev, desktop K0 s42, one run; Opus show-all = 20-row hidden sample per tier. No CIs (sources bootstrap the two terms separately).

## 5. T22.2: FA-CARDS anaphylaxis sentence provenance
- "Inject it into the middle of the outer thigh (it works through clothing) and hold it in place as the pen's instructions say." shares only the standard site phrase "middle of the outer thigh"; structure is ours. Compared against the log's summary of the sources, not their fetched text.
- Provenance section with the 4 URLs added to arms/fa-cards/FA-CARDS.md; same URLs added to NOTE-1 row 13 evidence column (handoff/, outside git). Content reviewer step still required before shipping.

## 6. Literature priors bundle
- Added "Literature priors (from the web loop, 10-21)" to RESEARCH-PAGE-OUTLINE: 14 lines (T1.3, T2.5, T3.1, T3.2, T5.4, T6.1, T7.1, T9.2, T11.1, T12.1, T12.2, T18.1, T18.2, T23.2), each with what it supports, URL, date and confidence. 7 marked "verify by fetch". The T11.1 Jaccard figure and the OSF preprint are marked unverified.

## 7. T17.1: llama-server re-processing on mini deep runs
- Scope: <runner>/kiln, every *.log naming Qwen3.6-35B / 35B-A3B that is a server/run log: 62 logs, 52.5 k lines; 48 are b11010 llama-server (`-c 4096 -np 1 --cache-ram 0`), 14 older/other builds.
- "forcing full prompt re-processing": **0** in all 62. "checkpoint": **0** in deep logs (only in lesport/kvchk logs, non-deep-tier).
- 1,857 prompt evals; 1,773 "selected slot by LCP similarity" reuses, mean f_keep 0.218 (prefix reuse is small because RAG contexts differ per item).
- So desktop deep wall times did not carry the #24587 penalty. Deep-tier speed numbers stand as measured.

## 8. T23.2: hide vs warn priors
- RESEARCH-PAGE-OUTLINE literature line T23.2 (2402.07632, 2407.18418, OSF preprint unverified).

## 9. T23.3: prior art for BLOCKCACHE
- arms/blockcache/BLOCKCACHE.md caveats (maintainer-note line): libzim caches decompressed clusters and streams decompression lazily (Streamreader PR #421; 2020 partial-decompression PR #411: 59 s -> 37 s crawl), with the log's URLs.

Ledger: web/ACTIONS.md rows W16, W20, W21, W29, W31, W33, W38 (provenance only), W41 and W42 set to acted.
