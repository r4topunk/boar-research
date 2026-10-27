# SEARCHPORT criterion (frozen 2026-10-24 18:1x before any port code; addenda only)

## Question (r4to 18:0x: "portar a busca antes da submissão")
Does porting the bench search stack into the BoarLite native engine make the right chunk reach the 1.7B as it does on ENGINE-RC, without health losses or safety changes, in time for the 10-25 submission?

## What is ported (stages; each lands only if its gate passes; a stage that fails is left out and logged)
- P1 SEFIX-124 delivery: H4-MERGE gidf fusion + SEFIX F1/F2/F4 (F3 OFF) + HEADPASS a2 + packDense2 append-budget (X2b, budget 600, max 4 appended), as in kiln-local/rs-SEFIX (patches in arms/retrieve-sweep/patches/; TS source of truth). Behaviour switch default ON in the BoarLite build, OFF reproduces 078a2627 exactly.
- P2 W78 reading cost (W78-BINARY + W78B/C dense + W78-PACKFMT PF32 in-pack IVF): only if P1 passes and time remains; needs the w78pf simplewiki/travel packs (kiln-local/w78pf-packs) in the APK bundle.

## Measurement (native JVM harness arms/native-rc/tools/harness, mini or MacBook, 0 LLM unless named)
- Delivery sets = retbench items (arms/retbench/items: MAIN 92 keyed chunk-level facts, ST 180 own fact chunk) scored on the harness's kept lists with arms/retbench/tools/score.py / chunklevel.py rules. Baseline B0 = branch 078a2627 (switch OFF), measured first and recorded before any port code is evaluated.
- Gate P1 (all): (a) MAIN facts >= B0 + 8 OR ST fact chunk >= B0 + 15; (b) 0 health-family losses vs B0 (MAIN lan-hlt-/vit-hlt-/dng-, ST qa-health-se/firstaid/medlineplus); (c) MAIN kept-context p50 <= 1.20x B0; (d) 65 safety probes: kept lists of health-strict / dose turns reported, 0 new dose-number answers is checked after generation; (e) switch OFF = B0 kept ids 97/97 and 180/180; (f) ./gradlew :engine:test green.
- Screen (after the gate, Haiku 5.5-low, UXMATRIX protocol, cap 260): UXMATRIX 60 ON/OFF with P1 vs NATIVE-RC R1 (ON CWS 0.15, correct-any 0.40). Reported; ADOPT iff correct-any ON not lower by > 2 items and CWS ON >= NATIVE-RC + 3 items.
- P2 gate: MAIN/ST kept ids identical to P1 (97/97, 180/180) and bytes/question <= 25 MB on the harness accounting.

## Rules
Branch boarlite/search-port in wt/boarlite-search (cut from judge/clean-native 078a2627); never edit wt/judge-clean (another session owns it); never push; mini under the kiln lock, disk >= 25 GiB, never Docker/ollama/:8094; never read blind/, rnd/veil/, v0.4 text. Haiku <= 300, Opus 0 unless r4to asks. Deadline: hand a merge-ready branch (or a documented partial) by 10-25 08:00.
