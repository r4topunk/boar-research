# E1 PARTIME: what a parallel or bounded pack search would remove from T_8GB (replay-only, 2026-10-21)

TL;DR: Promise.all in searchWikiPacks alone takes T_8GB p50 from 7.57 s to about 5.5-6.0 s, not to 5.0 s, because 66 % of the pack search is JS-thread work (fzstd block decompress + materialize, 194 blocks per question) that cannot overlap on one JS runtime. Reaching <= 5.0 s from retrieval alone needs one of: (i) Promise.all + dropping the two packs with 0 kept hits on this set (4.77 s, kit choice + engine change), (ii) two-lane search with the JS work off the main thread (4.95 s), (iii) full parallel off-thread (2.80 s, the native app's natural shape), or (iv) bounded materialization (1.80 s if the block phase vanished; ranking-changing). X2b is already OFF on the phone engine, so (b) adds 0 s; the system-prompt prefix KV is already reused on every call, so (c) adds about 0 s on single-turn questions.

0 LLM calls, 0 judge calls, 0 paid. No llama.cpp or engine source change; no instrumentation needed (the phone traces already carry per-pack sql spans).

## Inputs
- Phone traces: handoff/pixel8-2026-10-20/bench/results/aunion73-a (A-union: 6 packs + gazetteer) and q17b73-a (claim kit: crypto + wikivoyage). Pixel 8a, Qwen3-1.7B Q4_K_M, quickFirst, BOAR Bench engine tree 0ca54d87, cool phone (thermal 0; AUNION-PIXEL.md). n = 73 rows each; 58 rows run the pack search; 34 rows call the LLM (38 completions).
- bench.json timeline: span t = end time (ms from question t0), start = t - ms. Each pack window runs from its first sql span start (pack 1: search-wikipacks start) to the next pack's first sql span start (last pack: search-wikipacks end). SQL_p = sum of the pack's sql spans; JS_p = window - SQL_p.
- Script: partime_analyze.py (this folder); outputs aggregates/partime-summary.json, partime-extra.json, partime-drop.json, perq-*.json.
- Desktop replay not run: the phone traces give per-pack time directly, so no desktop scaling was needed. For reference, PK-5 measured the same six packs at retrieve() p50 226 ms on the MacBook vs 3.99 s on the phone (ratio about 18x).

## 1. Per-pack search time on the phone (aunion73-a, n = 57-58 searches per pack)
| pack | window p50 / p90 / max (ms) | sum over 73 (s) | SQL share |
|---|---|---|---|
| crypto | 780 / 1774 / 2369 | 48.4 | 0.34 |
| wikivoyage | 811 / 1428 / 2336 | 48.6 | 0.36 |
| factbook | 712 / 987 / 2499 | 38.4 | 0.31 |
| firstaid | 663 / 975 / 1510 | 34.8 | 0.36 |
| visa | 602 / 1016 / 1954 | 34.0 | 0.31 |
| medlineplus | 505 / 752 / 1110 | 27.1 | 0.40 |
| all six | search p50 3947 (retrieve p50 3992) | 231.3 | 0.34 |
- The AUNION-PIXEL "about 0.15 s per small pack" was SQL time only; the full window per small pack is 0.5-0.7 s, about 3x the SQL.
- Where the window goes: 73.2 % is the block phase (block fetch + fzstd decompress + materialize; 194 blocks per search p50, 16.0 ms per block); the rest is stemming, df lookups, bm25 and article rows. Kit run: 74.8 %, 70 blocks per search.
- Visa and medlineplus put 0 titles into retrievedTitles on this set (AUNION-PIXEL pack hits), yet cost 1.1 s per question.

## 2. Serial vs parallel vs 2-at-a-time (search wall per question, 58 searches)
| schedule | assumption | search p50 (ms) | mean |
|---|---|---|---|
| serial (measured) | today's for-loop | 3947 | 3988 |
| full parallel, ideal | every pack incl. its JS on its own thread (max window) | 1063 | 1183 |
| Promise.all on one JS runtime, LB | native SQL overlaps; JS serial: max(sum JS, max window) | 2534 | 2642 |
| Promise.all on one JS runtime, UB | as LB but the longest pack's SQL does not overlap | 2892 | 2988 |
| 2 lanes, ideal | LPT on 2 lanes of whole windows | 2050 | 2089 |
| 2 lanes, JS serial | max(sum JS, 2-lane makespan) | 2534 | 2654 |
Kit (2 packs): serial 1498, ideal 1043, Promise.all 1098-1307.
Reading: on the JS engine the bottleneck is JS, not SQL (66 % of the window), so Promise.all and a 2-lane bound give the same 2.5 s; only moving the decompress/materialize off the JS thread (native module, worklet, or the native Kotlin app) reaches the 1.1-2.1 s lines.

## 3. Where the 7.6 s goes (share of answer time; aunion73-a)
| scope | n | retrieval | prefill | decode | llm-init | other |
|---|---|---|---|---|---|---|
| all 73 rows (544 s) | 73 | 44.0 % | 24.7 % | 26.1 % | 0.3 % | 4.9 % |
| LLM rows | 34 | 30.8 % | 31.5 % | 33.2 % | 0.4 % | 4.1 % |
| 15 rows around the p50 | 15 (7 LLM) | 61.6 % | 15.7 % | 15.6 % | 1.6 % | 5.5 % |
| kit run, all 73 rows | 73 | 25.9 % | 32.6 % | 34.0 % | 0.6 % | 6.9 % |
- The distribution is bimodal: 39 rows never call the LLM (24 of them still run the full pack search: declines and safety items), 34 do. The p50 row itself (7.6 s) is a no-LLM row whose time is 7.3 s of pack search. So T_8GB p50 is mostly a measure of pack-search time on declines; it moves a lot with retrieval and is fragile near the mode gap (rows 32-38 jump 5.7 -> 7.6 s).
- LLM rows: answer p50 12.43 s (kit 9.66); with search removed 8.28 s (kit 8.58), so the model side is the same in both runs.

## 4. Projected T_8GB (73 rows, p50 / p90 s; new total = total - (serial search - new search), other rows unchanged)
| scenario | change type | p50 | p90 | LLM-row p50 |
|---|---|---|---|---|
| measured (A-union) | - | 7.57 | 15.05 | 12.43 |
| measured (claim kit) | - | 4.16 | 12.07 | 9.66 |
| (a) Promise.all, JS-bound | engine change | 5.53-6.02 | 13.57-13.85 | 11.08 |
| (a') 2 lanes, ideal (JS off-thread) | engine change | 4.95 | 12.99 | - |
| (a'') full parallel, ideal (JS off-thread) | engine change | 2.80 | 12.00 | 9.46 |
| (b) (a) + X2b OFF | none on the phone | = (a) | = (a) | = (a) |
| (c) (a) + more prefix-KV reuse | none available single-turn | = (a) | = (a) | = (a) |
| kit lever: drop visa + medlineplus, serial | kit file choice | 5.67 | 13.81 | - |
| kit lever + Promise.all | kit + engine change | 4.77 | 12.80 | - |
| bounded materialization ceiling (block phase -> 0) | engine change, ranking risk | 1.80 | - | 9.31 |
| ceiling: pack search free | - | 0.87 | - | 8.28 |
- (b): the phone engine (bench-app/engine, tree 0ca54d87) has no head pass (no HEADPASS/denseAppend code; it exists only in the kiln-local litepacks trees), so T_8GB was already measured X2b OFF: promptN p50 250 (A-union) / 276 (kit) vs 729 ON -> 420 OFF on the desktop LITEPACKS runs. Counterfactual: porting X2b ON to the phone would scale evaluated prompt tokens by about 1.74x, i.e. LLM-row prefill p50 3.8 s -> about 6.6 s (+2.8 s per LLM row, linear at constant prefill speed). The X2B-OFF-MAIN -42 % is therefore a cost avoided, not a saving available.
- (c): every completion reuses a cached prefix (cacheN - promptN = 244-300 tokens on all 38 calls; 4 calls fully cached). What is still evaluated (promptN p50 250 per LLM row) is the question + retrieved context, unique per question. Single-turn reuse ceiling on this set: about 0 s. The hard bound (all prefill removed, impossible) is 2.59 s p50 with ideal parallel; prefix work only pays in multi-turn sessions, where it is not measured here.
- Retrieval-side ceiling on T_8GB: 2.80 s p50 for a schedule change that keeps ranking identical (full parallel, off-thread); 0.87 s if pack search were free. The <= 5.0 s target is reachable from retrieval alone, but not with Promise.all on the JS runtime alone (5.5-6.0 s).

## 5. Flag vs engine change
| lever | type | ranking identical? | who |
|---|---|---|---|
| Promise.all in searchWikiPacks (bench-app engine/src/rag/packs.ts) | engine change (bench APK rebuild) | yes, by construction (per-pack lists, then the same fusion) | us for BOAR Bench; maintainer for the native app |
| off-thread decompress / per-pack coroutines | engine change | yes | maintainer (native Kotlin already runs off a JS thread: its bound is nearer the ideal line; unmeasured) |
| bounded materialization (only candidates that can reach fused topK) | engine change | no; needs a PK-5-style parity replay + judged screen | us first (replay), then maintainer |
| drop packs with 0 kept hits (visa, medlineplus) from the default install | kit/catalog file choice, no code | yes on this set (0 retrieved titles), loses persona coverage elsewhere | product decision |
| engineOverrides (threads, KV type, flash attn) | flag | n/a (LLM side only) | - |

## UNKNOWN
- Whether expo-sqlite runs async calls on different connections concurrently on Android (each pack has its own connection). If it serializes them, Promise.all still reaches the JS-bound LB because JS (66 %) > SQL (34 %), as long as SQL and JS can overlap.
- Pack windows include the next pack's temp-table DELETE/INSERT (not logged as sql spans): a few ms per boundary, inside the noise.
- One run per kit, one phone, one seed of the question set; the p50 sits at a mode gap, so a 10-item device check is the real test.
- Whether the native RC shows the same serial pattern and block costs (step 4 of the device day reads it only if the RC is debuggable).

## Device-day A/B: appended to coordinator/DEVICE-DAY-2026-10-22.md (section "Step E1-PAR").
