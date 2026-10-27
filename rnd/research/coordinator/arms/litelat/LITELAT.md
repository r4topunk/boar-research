# LITELAT result (2026-10-20, main): on a Pixel 8a, retrieval (format-2 pack search, ~435 serial one-row SQL calls) is 57 % of the 1.7B's TTFT, and prefill is 36 %; no bench override reaches the -20 % TTFT bar

Criterion: LITELAT-criterion.md, sha256 22c987fc (frozen and committed in rnd e882a07a before any candidate run). 0 LLM calls, 0 judge calls, 0 paid. Phone: Pixel 8a (GrapheneOS, Tensor G3, 8 GB), airplane mode on, Wi-Fi off, BOAR Bench in front, USB power. Build: bench-app live-view + LITELAT observer taps (APK sha f97f74a5…, engine tree 7c96e59e = cut 7, engine source unchanged). Model qwen3-1.7b-q4km (thinking off), claim kit. Set litelat-9 (7 v0.1 dev items that reach the model + 2 retrieval-wait safety cards). 7 runs x 9 questions (C6 combo not run: fewer than 2 LEADs).

## TL;DR
- TTFT p50 9.4 s on the 7 model items (R0 + R1 pooled, n 14) = retrieval 5.3 s + prefill 3.3 s (283 new prompt tokens at 85 tok/s) + < 0.4 s for everything else. Query embedding takes 20 ms, the detector 55 ms, corpus dense search 70 ms and context build + grounding 28 ms, so none of them is worth optimizing.
- Retrieval is not FTS and not embedding. It is the format-2 pack search (Wikivoyage + crypto) making about 435 serial expo-sqlite calls per question at 7–9 ms each (3.65 s of serial SQL). Most return one row: title and redirect probes (190 calls, 1.5 s), per-hit article, meta and zstd block fetches, and per-term df lookups. The BM25 query itself runs once per pack (78 ms).
- The safety cards (CO alarm, burn) wait 8.9 s for a retrieval with 665 SQL calls (5.7 s) before showing a fixed card.
- Overrides: 5 threads is the only gain (prefill +15.8 %, TTFT -4.4 %). It is NO by the frozen rule because of one new decline, but the baseline repeat shows that declines move with sampling (2 vs 4 in identical configs). FA off, KV q8 and 6 threads are LOSS. mlock is NO (no effect).
- The next lever is an engine change: batching or caching the pack lookups is projected at -2.5 to -3.3 s TTFT (-30 to -35 %). Showing the safety card before retrieval would take card TTFT from 8.9 s to about 0.2 s.

## 1. Stage breakdown (engine defaults; medians, ms)
R0 + R1 pooled (litelat-00-base, litelat-07-base-repeat). Spans come from the observer taps (runs/*.breakdown.json, analyze.py). Instant tier is from live-17b-final2 rows (the same build without taps, 4 items).

| stage | fast tier, model answer (n 14) | fast tier, retrieval-wait card (n 4) | instant tier (n 4) |
|---|---|---|---|
| question → "retrieving" (routing, detector, telemetry read) | 175 | 128 | — |
| of which emergency detector (mmBERT) | 55 | 63 | — |
| retrieve() wall | **5 309** | **8 824** | 0 (no retrieval) |
| of which query embedding (native) | 20 | 20 | — |
| of which corpus FTS / corpus dense (300 chunks) | 21 / 70 | 20 / 75 | — |
| of which format-2 pack search wall (Wikivoyage + crypto) | 5 276 | 8 803 | — |
| of which serial pack SQL: calls / summed ms | 435 / 3 650 | 665 / 5 729 | — |
| of which title + redirect probes: calls / ms | 190 / 1 507 | 200 / 1 475 | — |
| format-1 packs | 13 | 17 | — |
| retrieve end → LLM stage (compress, grounding, route) | 28 | — | — |
| model load (first model question only; llm init 1.7–2.2 s) | 1 900–2 404 | — | — |
| prefill (llama.cpp prompt_ms; 283 new tokens, 552 cached) | **3 345** | — | — |
| prefill end → first token | 75 | — | — |
| **TTFT** | **9 370** | **8 944** | 100–931 (facts 931 on a cold first question, calculator 551, CO fact 100, snakebite card 102) |
| decode (52 tokens at 14.3 tok/s) | 3 348 | — | — |
| **total** | **13 216** | 8 945 | = TTFT |

Where the pack SQL goes (18 questions, R0 + R1; 9 398 calls, 76.8 s summed):

| statements | calls | s | ms/call |
|---|---|---|---|
| crypto: title probe + redirect probe | 3 210 | 23.3 | 7.3 |
| wikivoyage: article row + zstd block fetch | 1 690 | 14.7 | 8.7 |
| crypto: article row + meta (url, license) + block fetch | 2 044 | 15.6 | 7.6 |
| wikivoyage: title probe + redirect probe | 984 | 7.3 | 7.4 |
| both: df / fts_v / qtok_v term lookups | 978 | 7.5 | 7.7 |
| wikivoyage BM25 query (the real search) | 18 | 1.4 | 78 |

Caveat: a call's wall time includes waiting for the JS thread and expo-sqlite's async queue, so the per-call cost is round-trip overhead and not SQLite work. The JS work inside the pack search (zstd decompression, scoring) is the remainder, about 1.6 s per question (5.28 - 3.65). It was not timed separately.

## 2. Candidates vs the same-session baseline (7 model items; noise band from R1 vs R0)
Noise band: TTFT 5.0 %, total 8.9 %, prefill tok/s 5.0 %, decode tok/s 5.0 % (all at or near the 5 % floor except total). Card TTFT works as a control because the overrides do not touch retrieval: it varied -3 % to -13 %.

| run | battery C | TTFT p50 | total p50 | prefill tok/s | decode tok/s | card TTFT | declines (of 7) | verdict |
|---|---|---|---|---|---|---|---|---|
| R0 base | 31.9 | 9 180 | 13 022 | 84.7 | 14.7 | 8 944 | 2 | baseline |
| C1 flash attention off | 33.6 | 11 119 (+21.1 %) | 14 376 (+10.4 %) | 52.3 (-38.2 %) | 14.0 (-4.9 %) | 8 638 | 2 | **LOSS** |
| C2 KV q8_0 (K+V) | 33.8 | 9 989 (+8.8 %) | 13 122 (+0.8 %) | 69.0 (-18.5 %) | 15.5 (+5.9 %) | 7 757 | 4 (+2) | **LOSS** |
| C3 threads 5 | 34.0 | 8 774 (-4.4 %) | 12 282 (-5.7 %) | 98.0 (+15.8 %) | 14.8 (+0.7 %) | 8 528 | 3 (+1) | **NO** (speed meets LEAD; quality clause fails on 1 new decline) |
| C4 threads 6 | 33.9 | 9 632 (+4.9 %) | 14 187 (+8.9 %) | 68.3 (-19.3 %) | 13.2 (-9.9 %) | 8 456 | 5 (+3) | **LOSS** |
| C5 mlock | 34.0 | 9 515 (+3.6 %) | 12 795 (-1.7 %) | 82.1 (-3.0 %) | 14.3 (-2.4 %) | 8 528 | 2 | **NO** |
| R1 base repeat | 33.9 | 9 559 (+4.1 %) | 14 183 (+8.9 %) | 83.1 (-1.9 %) | 14.1 (-3.9 %) | 8 642 | 4 (+2) | noise |
| C6 combo | — | — | — | — | — | — | — | not run (fewer than 2 LEADs) |

- Byte identity: the only identical answers are the fixed texts (2 cards plus the declines). The model texts differ in every run, including R1 vs R0, because device sampling is not deterministic (as in the A15 sweep). The visual check of every model answer in R0, R1, C2 and C3 found no garbled, truncated or off-topic text. The only differences are wording and declines.
- Declines are sampling noise. With identical settings, R0 declined 2 of 7 and R1 declined 4 of 7. Each decline is the compact "The passages found don't support this answer." line (vit-hum-004 and vit-cry-006 in every run; lan-exp-002, lan-exp-005 and lan-hlt-003 come and go). The frozen "no new decline" clause therefore cannot separate a setting from sampling at n 7. That is why C3 is NO and not LEAD. This is input for LITEDECLINE: the 1.7B's decline rate under the cut 7 policy moves between 2/7 and 5/7 across these 7 runs.
- Battery temperature crept from 31.9 to 34.0 C. The phone was charging, and thermal status was 0 throughout. C3 to R1 each waited about 5 min at the 34.0 C gate (thermal.jsonl). R1, the warmest base, is within 4 % of R0 on TTFT, so the drift is inside the noise band.
- Model load (llm init) took 2.2 s for R0 and 1.6–1.7 s for every later run, which is page cache. mlock did not change it.

## 3. What an engine change (not an override) could gain next (projections from R0 + R1 spans)
| change | what it removes | projected effect | evidence / caveat |
|---|---|---|---|
| E1. Batch the format-2 pack lookups: title and redirect probes as one IN (…) query per pack; article, meta and block rows fetched together; cache decompressed blocks and df rows per query | ~435 serial calls (3.65 s summed) → ≤ 20 statements per pack | TTFT -2.5 to -3.3 s (9.4 → about 6.1–6.9 s, -27 to -35 %). Cards: 8.9 → about 3.5 s. Total -2.5 to -3.3 s | Per-call cost is round-trip overhead (7–9 ms for 1-row reads, versus 78 ms for the one BM25 query). The JS remainder (~1.6 s) stays. Must return identical hits: replay with replay-retrieval.sh, byte-identical retrieved lists |
| E2. Safety card before retrieval when the detector fires or a CO, burn or other condition card matches | the 8.9 s retrieval wait | card TTFT 8.9 s → about 0.2 s (pre 128 ms + detector 63 ms) | Design and safety change: the card shows first, sources follow. Needs a Compass-style review of the health-no-source path |
| E3. Preload the answer model at app start or idle | first-question model load | first model question -1.9 to -2.4 s. Later questions 0 | The engine already prefills the tone prefix after load |
| E4. Default n_threads 5 on 9-core big.LITTLE phones (set_best_cores = X3 + 4 A715) | prefill compute | prefill +15.8 % (-0.5 s TTFT), decode flat. 6 threads loses (-19 % prefill: adds a little core) | NO by the frozen rule only through decline noise. Needs one repeat pair and a desktop judged check. Device-specific (POCO X6: 8 cores) |
| E5. Smaller kept context | prefill tokens | about -1.2 s TTFT per 100 fewer new prompt tokens (85 tok/s) | Quality trade-off. Judged check required (PACKREAD, LITEPACKS) |
| Not worth it | embedding 20 ms, detector 55 ms, corpus dense 70 ms, compress/grounding 28 ms, FA off, KV q8, mlock | — | measured above |

Order by gain per effort: E1 (largest, deterministic, no quality risk if hits stay identical), then E2 (8.7 s on safety questions, the worst user-facing wait), then E3, then E4.

## 4. Deviations and notes
- The question set is litelat-9 and not final-2-cut7: 7 of its 9 items reach the model, against 3 of 9 in final-2-cut7, so the LLM-side candidates have n 7 instead of n 3. All items are public dev (v0.1 plus the probe-co-alarm probe).
- R0 ran before the freeze. That run was the breakdown measurement the criterion allows, and no candidate ran before the freeze.
- Instrumentation: observer taps only (bench-app live-view commit below). Metro caches a resolution per (origin directory, name), so the pack and expo-sqlite taps match every importer in engine/src/rag. They re-export the real modules and only time calls. The answer-path behaviour matches the live build, and spans add about 9 400 small array pushes per run on the JS thread. Overhead was not measured separately. On the shared items, TTFT in live-17b-final2 (no taps) vs R0 was: vit-hum-004 12.0 vs 12.2 s, vit-cry-001 13.2 vs 13.9 s, lan-exp-005 7.8 vs 8.7 s. R0 is 2 to 12 % slower, within the noise of a single item. Any tap overhead is at most that and applies equally to every run.
- The bench.json timeline of R0 is kept as runs/litelat-00-base.bench.json.gz. The full results are in handoff/pixel8-2026-10-20/bench/results/litelat-*.

Files: LITELAT-criterion.md (+ .sha256), requests/, thermal_gate.py, thermal.jsonl, analyze.py, compare.py, compare.json, runs/.
