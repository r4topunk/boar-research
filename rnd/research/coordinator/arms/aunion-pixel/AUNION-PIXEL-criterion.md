# AUNION-PIXEL criterion (frozen 2026-10-21, before any A-union run on the phone)

Hypothesis: ruler/hypotheses-2026-10-21.json id AUNION-PIXEL. Gate measurement, 0 judge calls, 0 paid.

## Setup
- Phone: Pixel 8a (7.15 GiB), airplane mode on, Wi-Fi/Bluetooth off, BOAR Bench in front, USB power. APK = the installed bench build used for gemma10-b / q17b10-a / q17b73-a (engine tree 0ca54d87 = cut7-cmp30off-batchret, gemma2 APK); unchanged.
- Kit: bench-app/kits/persona-a-union.kit.txt = 6 text packs into files/corpus/ + world-places.sqlite into files/poi/ (shas = shared-data/packs/persona-a-union/SHA256SUMS = mini MANIFEST.json). boar-crypto and boar-wikivoyage-en are already on the phone with the same shas (the claim kit); the push adds visa, medlineplus, firstaid, factbook and the gazetteer.
- Pack discovery (engine source, bench-app/engine/src/rag/packs.ts knowledgePacks()): every *.sqlite in files/corpus/ is a pack (catalog entries + local-<name>), checked only for format boar-knowledge-pack + embedding sha; searchWikiPacks() searches every installed format-2 pack sequentially per question with k = topK, hits merged by fusion and cut to topK (no per-pack quota, no request-level pack selection). Source codes 10/11 (medlineplus, factbook) are labelled enwiki by SOURCES[code] ?? enwiki (wikiPack.ts l.660): their FTS hits are retrieved; title resolution by source misses them. Gazetteer: files/poi/world-places.sqlite (rag/pois.ts PLACES_FILE), catalog size 22,962,176 B matches.
- Requests (handoff/pixel8-2026-10-20/bench/requests): aunion10-a = q17b10-a with requestId changed (gemma-10 set, models qwen3-1.7b-q4km; sha 953e8d3b...), aunion73-a = q17b73-a with requestId changed (final-3-bench 73; sha 38a07b94...). Order: smoke aunion10-a; aunion73-a only if the smoke is clean (10/10 rows, no error, at least one A-union-only pack in retrievedTitles). Thermal gate before each (arms/batchret/phone/thermal_gate.py, status 0, battery <= 34.0 C).
- Baselines (same phone, same APK, same model, claim kit only, 2026-10-21 earlier session): q17b10-a and q17b73-a. Deviation from the hypothesis's a-b-a order: the claim kit cannot be restored without deleting pushed packs (phone rule), so no re-run of (a); drift is bounded only by the earlier same-day runs (batchret-2b/4b 1.7B answer p50 7.7-9.2 s on the 10).

## Measures (summarize_aunion.py, sha256 58b8e76288a2ff00d3170e7ef039038d275ecd2903ccffb1d8b4740f7a03f3ba)
answer p50/p90 (row totalLatencyMs, all rows), TTFT p50 (row ttftMs), promptN p50/max, prefill tok/s and decode tok/s p50 (timeline llm-completion spans), retrieval wall p50/p90/max (timeline retrieve items), SQL ms by pack file, PSS peak (telemetry 5 s), battery/thermal, LMK kills (logcat lines naming the package, read locally, logcat not copied), pack hits by retrievedTitles mapped to pack articles (titles in several packs count for each).

## Rules (10-question smoke vs q17b10-a)
- PASS (A-union admissible on 8 GB): answer p50 - baseline <= +3.0 s AND TTFT p50 - baseline <= +2.0 s AND PSS peak <= 4.0 GB AND 0 LMK kills.
- KILL (A-union not the 8 GB verdict arm): any LMK kill, OR PSS peak >= 4.4 GB, OR answer p50 - baseline > +5.0 s.
- Between the two: MARGINAL, reported with numbers; the 73-run decides on the same thresholds vs q17b73-a.
- Flag: medlineplus or factbook never in retrievedTitles across both runs -> native PackSource enum gap note (not a fail of this gate).
