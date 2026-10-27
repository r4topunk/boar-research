# W78-PACKFMT (2026-10-23; 0 LLM / 0 judge / 0 Opus / 0 paid / 0 phone; MacBook replay only) - ADOPT-CANDIDATE: in-pack IVF lists, lead matrix never loaded
Criterion ../W78PACKFMT-criterion.md sha256 7a81fd33d72c551db1224083b93326dbd3ac8f27865a053851ee1ab5b216669b (frozen 10:50 before any replay, not edited).
Patch ../../retrieve-sweep/patches/W78-PACKFMT.patch sha256 10192fb0f5631200463c98011ce773c9a42a3770ca5f2001b829c4fa9e0271a6 (on top of rs-W78 = rs-SEFIX + W78-BINARY + W78B-DENSE + W78C-DENSE; wikiPack.ts only; RS_DENSE_IVFP=<nprobe>, default off; + rssBefore/rssAfter in RS_DENSE_LOG). Tree kiln-local/rs-W78 (wikiPack.ts sha 7be8cfe7).

## Layout decision: new tables inside the pack (format 2, additive), not a sidecar file
- Why in-pack: the engines that ship (android-native WikiPack.kt, boar-ios WikiPack.swift) read packs only through SQLite queries + blob columns; a list-per-row table is a plain SELECT for them, no second file, no new file/mmap I/O path, one artifact to download and sha-check, and the lists can never drift from the lead vectors they index (a manifest-keyed sidecar can). Old readers ignore unknown tables, so format 2 stays readable.
- Why one row per list (not one big list-ordered blob + byte offsets): SQLite has no partial blob read through these APIs (no sqlite3_blob_open in node:sqlite or android.database.sqlite; substr() materialises the whole value) and Android's CursorWindow caps a row at 2 MB; per-list rows give page-granular reads (largest list 2,885 x 384 = 1.11 MB < 2 MB). The rowid b-tree is the offset table.
- Tables: lead_ivf(list_id INTEGER PRIMARY KEY, n, ids BLOB int32[n], vecs BLOB int8[n x 384]) members ascending article_id; lead_ivf_cent(id, k, dims, cents f32[k x dims], counts u32[k], pages u32[k] = leaf + overflow pages per list row from dbstat); meta.leadIvf JSON. lead_vecs and every other table byte-identical (kept: by-id lookups still use it).
- Cost: duplicates the lead vectors. simplewiki 735.5 -> 817.3 MB (+81.8 MB, +11.1 %), travel 212.0 -> 229.2 MB (+17.2 MB, +8.1 %); page overhead of the lists 1.4 % over payload. Removing lead_vecs (by-id reads through a position index) would cancel the duplicate; not done.

## Build (tools/pack_ivf.py; same k-means as W78C build_ivf.py, asserted byte-equal to the W78C .ivf256 lists, ids and centroids)
| pack | rows | lists min/p50/max | pages | one-off build (load + k-means + write + dbstat) | copy (APFS clone) | out sha256 |
|---|---|---|---|---|---|---|
| boar-simplewiki-en | 208,622 | 192 / 769 / 2,885 | 10,020 | 15.8 s (k-means 14.9 s) | 0.8 s | 9c316ff2... |
| qa-travel-se | 42,307 | 31 / 158 / 363 | 2,139 | 3.0 s (k-means 2.9 s) | 0.1 s | 6c7221a6... |
Copies in kiln-local/w78pf-packs/ (same basenames, not committed); published packs untouched. Build json: sidecars-pf/{simplewiki,travel}.pf.json.

## Commands
    python3 -I tools/pack_ivf.py $P/boar-simplewiki-en.sqlite kiln-local/w78pf-packs/boar-simplewiki-en.sqlite sidecars-pf/simplewiki.pf.json --check sidecars-c/9d2dfe7694c55c72.ivf256   (travel: 618741e43c91a3ed)
    tools/batch_pf_full.sh   # run_w78pf.sh PF32 1 32 RS_DENSE_IVFP=32 ; IVF32 0 32 RS_DENSE_IVF=32 ; B 0 0   (141-176 s each)
    tools/batch_pf.sh        # (its full-arm lines failed on a bash 3.2 empty-array bug, fixed and rerun by batch_pf_full.sh) 3 x cold start per arm: IDS=vit-hum-001 (first MAIN item, retrieves, 7 stage-1 calls)
    python3 -I tools/score_w78pf.py w78pf.json

## Arms (MAIN 97, W78C recipe; F1 through the W78 binary path in IVF32/PF32; bytes per retrieving question, n 86)
| arm | stage-1 bytes/q | whole kit (+F1) bytes/q | stage-1 scan ms/q | load ms total | kept identity vs W78C IVF32 | vs B | stage-1 lists = W78C IVF32 | facts of B's 42 | health changed | RSS growth 1st q (replay) | RSS growth full replay | process RSS at end |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B (all exact) | 101,747,712 | 125,094,912 | 120.7 | 471 | 96 | 97 | 462/602 | 42 | 0 | 362.8 MB | 451.9 MB | 723.3 MB |
| IVF32 (W78C, sidecar + resident matrix) | 17,907,277 | 20,850,253 | 24.1 | 564 | 97 | 96 | 602/602 | 42 | 0 | 306.0 MB | 328.8 MB | 595.8 MB |
| **PF32 (in-pack lists)** | **18,321,286** | **21,264,262** | 45.2 | 48 | **97/97** (+ codes 97) | 96 (money-005, as W78C) | **602/602** | **42** | **0** | 56.5 MB | 215.5 MB | 484.9 MB |
PF32 bytes: SQLite pages of the probed rows 12.14 MB/q (payload 11.85 MB/q) + centroids 0.39 MB x 2 packs per question (counted every call; resident after the first) + 5 small packs exact 5.39 MB + F1 2.94 MB. Per call: simplewiki 25,356 rows, 9.98 MB pages, 28.7 ms (read 7.7 ms); travel 5,190 rows, 2.16 MB, 9.7 ms (read 4.4 ms). Resident stage-1 state 6.29 MB (centroids + counts + the 5 small matrices) vs 8.30 MB + the 96.4 MB of the two big matrices in IVF32.
Scan ms doubles vs IVF32 (45 vs 24 ms/q): the SQL read (12 ms/q) + per-member object merge in JS; the matrix load (0.5 s once) is gone.

## Cold start (fresh process, one question vit-hum-001, 3 reps, medians; stage-1 lists identical across reps and PF32 = IVF32)
| arm | stage-1 ms incl. load | bytes read from storage, stage 1 | F1 | total | RSS growth over the question | process RSS after |
|---|---|---|---|---|---|---|
| B | 620 | 101.75 MB (whole matrices) | 23.35 MB | 125.09 MB | 360.6 MB | 633.2 MB |
| IVF32 | 539 | 104.54 MB (matrices + sidecars) | 3.19 MB | 107.73 MB | 301.0 MB | 573.1 MB |
| **PF32** | **92** | **17.10 MB** (probed list pages + centroids + small packs) | 3.19 MB | **20.28 MB** | **76.9 MB (0.256x IVF32)** | 351.0 MB |
RSS growth is measured over the whole first question (stage 1 + stage 2 + the rest between calls, V8 heap included), so it overstates the stage-1 share; PF32 reps 58.5 / 76.9 / 80.7 MB (GC noise).

## Verdict (frozen rule)
**ADOPT-CANDIDATE.** Kept lists = W78C IVF32 on 97/97 (reason codes too; 602/602 stage-1 article lists identical), 42/42 facts, 0/11 health changed, whole kit 21.26 MB/q <= 25, cold-start RSS growth 0.256x IVF32 <= 0.3. The IVF byte saving is now real on the desktop path: the lead matrix is never read; a question reads 20.3 MB cold instead of 107.7-125.1 MB, first-query stage 1 in 92 ms instead of 539-620 ms.

## What the phone measurement needs
- Port rsDenseStage1Ivfp to WikiPack.kt (one SELECT ids, vecs FROM lead_ivf WHERE list_id IN (32 ids); centroids row cached; exact int8 rescore with a float32 norm) and ship the two packs with the tables (pack_ivf.py at build time, new file sha, +11 % / +8 % download) - or run pack_ivf on device after download (k-means 15 s on M1, unmeasured on ARM).
- POCO X6 Pro read on 9-10 items: cold first-question stage-1 ms, warm ms/q, PSS before/after the first question vs the current build, and page-cache effect (storage reads measured at the OS, e.g. /proc/self/io read_bytes) - this replay counts SQLite pages, it cannot see the OS cache.

## Not run / limits
OS-level read bytes (no sudo for purge/fs_usage; bytes = SQLite pages from dbstat x 8 KiB, the pager's granularity); nprobe other than 32; IVF on the 5 small packs; int4 codes inside the lists; QFORM 216; Hermes/ARM timings; removing the duplicate lead_vecs. Dev items (MAIN 97), one kit, one k-means seed, kept chunks only (0 LLM).
Files: W78-PACKFMT.md, w78pf.json, tools/{pack_ivf.py, run_w78pf.sh, batch_pf.sh, batch_pf_full.sh, score_w78pf.py}, sidecars-pf/*.json; replays-pf/ gitignored.
