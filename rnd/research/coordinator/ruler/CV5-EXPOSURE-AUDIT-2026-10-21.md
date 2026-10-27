# CV5-EXPOSURE-AUDIT (2026-10-21): no v0.4 text exposure, no held-out ids in any run file outside blind/ beyond one known smoke; 5 held-out/v0.4 rows missing from EXPOSURES.md (below the kill line of 3 per set)

TL;DR (0 LLM, 0 judge, 0 paid; criterion ruler/CV5-criterion.md sha 78f43da6; script tools/exposure_audit.py sha b96d2367378a; output CV5-EXPOSURE-AUDIT-2026-10-21.json sha 0590a4b906de). EXPOSURES.md not edited: the coordinator appends the rows below.
- **Scan:** 2,203 judgment / trace / phone-rows files modified since 2026-10-06 under rnd/ (minus rnd/veil, rnd/archive), boar-eval/runs, boar-eval/reports, boar-eval/adapters, handoff/, bench-app/, deep/; blind/ and node_modules skipped. Ids pulled by regex only (no line parsed or printed); 264 (arm, set) groups, each with its sorted-id-set sha (12 hex) in the JSON.
- **v0.4: clean.** 0 run files carry a cw-/cx- id (no generation, no judge pass). Code audit: only tools/inpack_map.py opens bench/v0.4/items.jsonl; it uses id, family, type, tags (minus anchor_vexact_question) and the presence of lat/lon keys; RV4 reads INPACK-STRATUM json only; tilepath.py has an items mode but TILE-PATH never ran it on v0.4 (TILE-PATH.md TL;DR). One wording gap: inpack_map.py json-parses each full line in-process (question text in memory, never stored or printed); the ledger row says "script read id, family, ..." and should add that.
- **V-para: no run file outside blind/** (all 10-06+ V-para runs live under blind/, consistent with the ledger). **v0.2: one group outside blind/**: boar-eval/runs/kiln/deepiter/di-smoke-I.traces.jsonl (3 v0.2 ids, traces with question text, researcher-readable). DEEPITER's ledger row counts the smoke but not this location: latent exposure, quarantine proposed.
- **Missing held-out / v0.4 rows: 5** (v0.2 2, v0.4 2, V-para 1); no set reaches 3, so the hypothesis is **not killed**. The page statuses match the rulings: V-para dev-style since 10-06 (ruling 10-09), v0.2 burnt → dev (10-06 D5), both also exposed to an OpenAI judge (XFAM rows 10-16/10-17); v0.4 held-out, no system result.
- **Dev sets:** 129 arms with dev-set runs since 10-06 (v0.1, MAIN 97, self-tests, longsession, probes, phone sets) have no ledger row. The ledger's own rule (l.78) says v0.1 dev runs are not exposures, but the 10-21 COVERAGE-MATRIX and REFVAR rows started logging dev sets; proposed backfill rows are in the appendix (status "dev (unchanged)"). Judge rows on dev sets since 10-06: Haiku 5.5 16,910 self-tests + 8,484 v0.1 + 1,032 longsession; Opus 4,390 self-tests + 2,609 v0.1; local Gemma 26B 290 and Qwen3.6-35B 118; Sonnet 228; Haiku 4.5 47.
- **Limits:** blind/ was not listed or opened, so held-out runs stored only there are checked against QUEUE entries since l.1180 and arm reports (grep), not against files; the mini's <runner>/kiln run dirs were not scanned; ledger matching is by arm name + set keyword (heuristic: a few dev groups "match" rows that only mention the arm).

## Proposed rows for EXPOSURES.md (held-out and v0.4; coordinator appends)
| date | set | event/arm | kind | items/seeds | judge | who saw what | status after | source |
|---|---|---|---|---|---|---|---|---|
| 10-16 18:0x | bench-v02 | SMALLROUTE S0 (router ceiling probe a2fa9572; deep half on v0.2) | script-read of per-item Opus ratios, n_kept, path and jev labels from arms/lossmap/aggregates/lossmap-{K,H}-v02-s42.json + DEEPTHINKV02 aggregates; ids + scores only | 110 ids, s42 (TV 2-seed aggregate-only) | 0 calls | opus agent; no question text read (S0.md scoped exception) | dev (unchanged) | QUEUE l.1265; arms/smallroute/S0.md |
| 10-10 (found 10-21) | bench-v02 | DEEPITER smoke traces stored outside blind/ (boar-eval/runs/kiln/deepiter/di-smoke-I.traces.jsonl) | latent (researcher-readable path; traces hold question text) | 3 ids, smoke | none | any boar-eval reader since 10-10; CV5 audit read ids only | dev (unchanged); move the file to blind/bench-v02/runs-deepiter/ | this audit; ledger DEEPITER row l.116 |
| 10-21 04:39 | v0.4 ruler (items.jsonl f9ad2f2f…) | RV4-CITY-BOUND (ruler/tools/rv4_city_bound.py) | script-read of INPACK-STRATUM json (id, tags.has_location, health_safety, anchor_vexact); items.jsonl not opened | 71 headline ids, 7 has_location | 0 calls | coordinator/agent: ids, weights, counts | held-out ruler (unchanged) | QUEUE l.1528; ruler/RV4-CITY-BOUND-2026-10-21.md |
| 10-21 05:2x | v0.4 ruler (items.jsonl f9ad2f2f…) | CV5-EXPOSURE-AUDIT (ruler/tools/exposure_audit.py) | script-read: items.jsonl streamed, id field extracted by regex; nothing else kept or printed | 75 ids | 0 calls | opus subagent: ids and counts only | held-out ruler (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md |
| 10-21 05:2x | V-para | CV5-RECOMPUTE (ruler/tools/recompute_page_numbers.py) | script-read of derived aggregates outside blind/: lossmap-K-vpara-s42.json items (id, Opus ratio, loss, ref scores, n_kept, jev labels), deepvpara dv-vpara-2seed.L2.json, dt512 L2-H-2seed.opus.json | 51 ids, s42 (+2-seed aggregates) | 0 calls | subagent: ids, scores, aggregates; no text | dev-style (unchanged) | ruler/CV5-RECOMPUTE-2026-10-21.md |
Amend (wording, no new row): INPACK-STRATUM 10-21 03:3x row: add "inpack_map.py json-parses each items.jsonl line in-process; question/turn/checklist fields are loaded in memory but never used, stored or printed".
Not rows (checked): HEALTHFALLBACK RESCOPE 10-16 (v0.2 aggregates quoted from QUEUE only); TILE-PATH (no v0.4 read); LITEREACH2 "random20" = self-tests (seed 888), not random20-v02; QWRITE (v0.2 clause unused); SAFEPACK "blind Opus" = blinded reviewer on public safepack items.

## Group table (264 groups; held-out first)
| arm | set | held-out | dates | gen files | judge files | judge calls (rows) | id-set sha(s) | max ids | ledger rows |
|---|---|---|---|---|---|---|---|---|---|
| kiln/deepiter | v0.2 | yes | 10-10 | 1 | 0 | - | 59568cfc9c90 | 3 | 1 |
| _lib | other:fx |  | 10-15 | 1 | 0 | - | f805819a7998 | 10 | 0 |
| aunion-pixel | other:probe-co-alarm+other:saf+v0.1 |  | 10-21 | 1 | 0 | - | e8af221db33e | 10 | 0 |
| aunion-pixel | MAIN (v0.1 + cooking/money SE) |  | 10-21 | 2 | 0 | - | 46b611664ba2 | 16 | 0 |
| aunion-pixel | v0.1 |  | 10-21 | 0 | 2 | haiku-5-5 38 | 2d1f41b320c2 6d298665351e | 15 | 0 |
| aunion-pixel | other:saf+other:warmup+v0.1 |  | 10-21 | 3 | 0 | - | 5963e226454a | 73 | 0 |
| b-honest | MAIN (v0.1 + cooking/money SE) |  | 10-20 | 1 | 0 | - | 1aa15b215ed3 | 37 | 0 |
| b-honest | self-tests |  | 10-20 | 0 | 2 | haiku-5-5 26 | 4cd16354ac5a 95eaaae05f33 | 7 | 0 |
| b-honest | v0.1 |  | 10-20 | 0 | 1 | haiku-5-5 26 | e2712599c82b | 13 | 0 |
| bench-app/dry-run/out | other:sweep-ns+other:warmup+v0.1 |  | 10-06 | 1 | 0 | - | 7faae98a413e | 5 | 0 |
| bench-app/dry-run/out | other:probe-co+other:probe-co-alarm+other:warmup+v0.1 |  | 10-06 | 3 | 0 | - | 63b6cf05679d | 9 | 0 |
| bench-app/dry-run/out | other:probe-greet+other:sweep-ns+other:warmup+v0.1 |  | 10-06 | 1 | 0 | - | 2d1583f5e9f4 | 5 | 0 |
| bench-app/dry-run/out | other:warmup+v0.1 |  | 10-20 | 2 | 0 | - | 76a5407c2db9 | 4 | 0 |
| bonsai2 | v0.1 |  | 10-15 | 5 | 0 | - | 949b3484c461 | 3 | 1 |
| bonsai2 | other:h+other:m+other:n+other:nm+v0.1 |  | 10-15 | 2 | 0 | - | da37c183f77d | 64 | 0 |
| ce-opus-check | self-tests |  | 10-20 | 4 | 4 | opus-5-5 46 | 4cd16354ac5a cc82724f3a9a d538be28c7a4 +1 | 7 | 0 |
| ce-opus-check | v0.1 |  | 10-20 | 2 | 2 | opus-5-5 48 | 49b4dacccdc1 9829c436af95 | 12 | 0 |
| chainwhen | self-tests |  | 10-19 10-20 | 2 | 2 | haiku-5-5 472 | a9a538c2f0d6 e18cd16900aa | 150 | 0 |
| chatfail | v0.1 |  | 10-18 | 2 | 2 | haiku-5-5 228 | 33e51a74cdb9 | 57 | 0 |
| chunkclean | v0.1 |  | 10-21 | 2 | 2 | haiku-5-5 102 | 4c2b5577bc84 73059c668419 b1f2cae632c4 | 30 | 0 |
| citesup | selftest+selftest-cm+v0.1 |  | 10-21 | 4 | 0 | - | ac30e67845ff b017a3b6b469 | 50 | 0 |
| citesup | v0.1 |  | 10-21 | 0 | 4 | haiku-5-5 28 | 471e2eec8aa8 5c4ea6005b4c 758b9e3c3169 +1 | 6 | 0 |
| citesup | self-tests |  | 10-21 | 0 | 26 | haiku-5-5 154 | 03a4ccb7fe3a 0661ea36261e 0fd1ce8304eb +22 | 9 | 0 |
| complete | v0.1 |  | 10-06 | 1 | 1 | opus-5-5 114 | 33e51a74cdb9 | 57 | 0 |
| coverage-matrix | self-tests |  | 10-21 | 5 | 22 | haiku-5-5 564 | 04972df22177 0af3a3c0459e 0b4e34d2e28b +11 | 80 | 1 |
| coverage-matrix | MAIN (v0.1 + cooking/money SE) |  | 10-21 | 1 | 0 | - | d7d2f021d9d3 | 97 | 1 |
| coverage-matrix | v0.1 |  | 10-21 | 0 | 1 | haiku-5-5 82 | 93d28001e04d | 41 | 1 |
| crowdq | self-tests |  | 10-13 | 9 | 18 | haiku-5-5 360, opus-5-5 360 | 535411248b69 61c91736ff81 a7caf609ff8c +6 | 20 | 0 |
| deeppar | v0.1 |  | 10-07 | 1 | 1 | opus-5-5 114 | 33e51a74cdb9 | 57 | 0 |
| deepread | v0.1 |  | 10-06 | 1 | 4 | haiku-4-5-20251001 47, opus-5-5 114, sonnet-5-5 228 | 33e51a74cdb9 8bf336b06d9c | 57 | 0 |
| densechunk-st | self-tests |  | 10-12 10-13 | 37 | 36 | haiku-5-5 360, opus-5-5 1080 | 21dd3a86877c 535411248b69 61c91736ff81 +7 | 20 | 0 |
| device-tester-a15/cut3-v01-partial | other:warmup+v0.1 |  | 10-06 | 2 | 0 | - | 9380884220c6 | 43 | 0 |
| device-tester-a15/cut3-v01-partial | v0.1 |  | 10-06 | 0 | 1 | opus-5-5 50 | 83ba7d30ba43 | 25 | 0 |
| device-tester-a15/final-cut6-v01 | other:saf+other:warmup+v0.1 |  | 10-06 | 2 | 0 | - | 5963e226454a | 73 | 0 |
| device-tester-a15/final-cut6-v01 | v0.1 |  | 10-06 | 0 | 2 | opus-5-5 115 | 33e51a74cdb9 bfa58e924174 | 57 | 0 |
| device-tester-a15/sweep-cut5 | other:sweep-ns+other:warmup+v0.1 |  | 10-06 | 8 | 0 | - | 7faae98a413e | 5 | 0 |
| device-tester-a15/sweep-cut5 | other:probe-co+other:probe-co-alarm+other:warmup+v0.1 |  | 10-06 | 2 | 0 | - | 63b6cf05679d | 9 | 0 |
| device-pixel8a/cmp30-q15 | other:saf+other:warmup+v0.1 |  | 10-20 | 2 | 0 | - | d53d06eacc3b | 31 | 0 |
| device-pixel8a/cmp30-q15 | v0.1 |  | 10-20 | 0 | 1 | haiku-5-5 52 | 00287b0a8a9f | 26 | 0 |
| device-pixel8a/cmp30-q17 | other:saf+other:warmup+v0.1 |  | 10-20 | 2 | 0 | - | d53d06eacc3b | 31 | 0 |
| device-pixel8a/cmp30-q17 | v0.1 |  | 10-20 | 0 | 1 | haiku-5-5 52 | 00287b0a8a9f | 26 | 0 |
| device-pixel8a/cmp30off-q15 | other:saf+other:warmup+v0.1 |  | 10-20 | 2 | 0 | - | d53d06eacc3b | 31 | 0 |
| device-pixel8a/cmp30off-q15 | v0.1 |  | 10-20 | 0 | 1 | haiku-5-5 52 | 00287b0a8a9f | 26 | 0 |
| device-pixel8a/cmp30off-q17 | other:saf+other:warmup+v0.1 |  | 10-20 | 2 | 0 | - | d53d06eacc3b | 31 | 0 |
| device-pixel8a/cmp30off-q17 | v0.1 |  | 10-20 | 0 | 1 | haiku-5-5 52 | 00287b0a8a9f | 26 | 0 |
| device-pixel8a/final-cut7-v01 | other:saf+other:warmup+v0.1 |  | 10-21 | 2 | 0 | - | 5963e226454a | 73 | 0 |
| device-pixel8a/final-cut7-v01 | v0.1 |  | 10-21 | 0 | 1 | haiku-5-5 114 | 33e51a74cdb9 | 57 | 0 |
| device-pixel8a/gemma73-a | other:saf+other:warmup+v0.1 |  | 10-21 | 2 | 0 | - | 5963e226454a | 73 | 0 |
| device-pixel8a/gemma73-a | v0.1 |  | 10-21 | 0 | 1 | haiku-5-5 114 | 33e51a74cdb9 | 57 | 0 |
| device-poco-x6pro/final-cut7-v01 | other:saf+other:warmup+v0.1 |  | 10-14 | 2 | 0 | - | 5963e226454a | 73 | 0 |
| device-poco-x6pro/final-cut7-v01 | v0.1 |  | 10-14 | 0 | 1 | haiku-5-5 114 | 33e51a74cdb9 | 57 | 0 |
| device-poco-x6pro/native-x6-v01 | other:saf+other:warmup+v0.1 |  | 10-14 | 1 | 0 | - | 5963e226454a | 73 | 0 |
| device-poco-x6pro/native-x6-v01 | v0.1 |  | 10-14 | 0 | 1 | haiku-5-5 114 | 33e51a74cdb9 | 57 | 0 |
| device-x6 | other:saf+other:warmup+v0.1 |  | 10-14 | 2 | 0 | - | 5963e226454a | 73 | 0 |
| device-x6 | v0.1 |  | 10-14 | 0 | 2 | haiku-5-5 228 | 33e51a74cdb9 | 57 | 0 |
| dilution-k | v0.1 |  | 10-21 | 3 | 2 | haiku-5-5 100 | 56bc7dda8d31 73059c668419 9ffa0970d461 | 30 | 0 |
| drift17 | longsession |  | 10-21 | 2 | 1 | haiku-5-5 160 | ef5b1ae19ea9 | 80 | 0 |
| facts | v0.1 |  | 10-06 | 1 | 1 | opus-5-5 16 | 9a4df220e1ff | 8 | 0 |
| floor-anchors | v0.1 |  | 10-21 | 4 | 16 | haiku-5-5 1046 | 0a8058b08784 33e51a74cdb9 3efcd26de8cd +2 | 57 | 0 |
| floor-anchors | self-tests |  | 10-21 | 0 | 8 | haiku-5-5 64 | 0785a8b220b9 7c7a2b47e49c a60860215f56 +1 | 6 | 0 |
| fotapol-lora | selftest+v0.1 |  | 10-21 | 2 | 0 | - | 6331eacc1dd5 | 5 | 0 |
| fotapol-lora | selftest+selftest-cm+v0.1 |  | 10-21 | 2 | 0 | - | ac30e67845ff b017a3b6b469 | 50 | 0 |
| fotapol-lora | self-tests |  | 10-21 | 0 | 20 | haiku-5-5 154 | 03a4ccb7fe3a 11acd8bfe45b 2aa17655967e +17 | 9 | 0 |
| fotapol-lora | v0.1 |  | 10-21 | 0 | 2 | haiku-5-5 26 | 4e827d9611d7 6971e02fae8a | 7 | 0 |
| g41e | MAIN (v0.1 + cooking/money SE) |  | 10-21 | 1 | 0 | - | 1f3e0dc9b67c | 5 | 0 |
| g41e | self-tests |  | 10-21 | 0 | 1 | haiku-5-5 2 | 35fd15136463 | 1 | 0 |
| g41e | v0.1 |  | 10-21 | 0 | 1 | haiku-5-5 8 | cf3bb2c3ff31 | 4 | 0 |
| g41g | MAIN (v0.1 + cooking/money SE) |  | 10-21 | 1 | 0 | - | 1f3e0dc9b67c | 5 | 0 |
| gate17 | MAIN (v0.1 + cooking/money SE) |  | 10-20 | 2 | 0 | - | 543009bc5f59 d7d2f021d9d3 | 97 | 0 |
| gemma-safety | other:epi+other:h+other:m+other:n+other:nm+v0.1 |  | 10-21 | 2 | 0 | - | 7ca142dae883 | 65 | 0 |
| gemma4-e2b | selftest+selftest-cm+v0.1 |  | 10-20 | 4 | 0 | - | ac30e67845ff b017a3b6b469 | 50 | 0 |
| gemma4-e2b | self-tests |  | 10-20 10-21 | 2 | 54 | haiku-5-5 678 | 037e69a33327 03a4ccb7fe3a 04972df22177 +29 | 80 | 0 |
| gemma4-e2b | v0.1 |  | 10-20 10-21 | 1 | 10 | haiku-5-5 468 | 33e51a74cdb9 4e827d9611d7 a6c946439370 +3 | 57 | 0 |
| gemma4-e2b | MAIN (v0.1 + cooking/money SE) |  | 10-20 10-21 | 4 | 0 | - | 1f3e0dc9b67c d7d2f021d9d3 | 97 | 0 |
| gemma4-e2b | other:saf+other:warmup+v0.1 |  | 10-21 | 4 | 0 | - | 5963e226454a | 73 | 0 |
| gemma4-e2b | other:probe-co-alarm+other:saf+v0.1 |  | 10-21 | 2 | 0 | - | e8af221db33e | 10 | 0 |
| gemma4-e2b-confirm | MAIN (v0.1 + cooking/money SE) |  | 10-21 | 3 | 0 | - | d7d2f021d9d3 | 97 | 0 |
| gemma4-e2b-confirm | self-tests |  | 10-21 | 0 | 6 | haiku-5-5 198 | 037e69a33327 59758d0929e8 | 19 | 0 |
| gemma4-e2b-confirm | v0.1 |  | 10-21 | 0 | 3 | haiku-5-5 242 | 603539ed04bb cf9473633b02 | 42 | 0 |
| granite4-1b | selftest+selftest-cm+v0.1 |  | 10-21 | 4 | 0 | - | ac30e67845ff b017a3b6b469 | 50 | 0 |
| granite4-1b | self-tests |  | 10-21 | 0 | 42 | haiku-5-5 374 | 037e69a33327 03a4ccb7fe3a 11acd8bfe45b +19 | 19 | 0 |
| granite4-1b | v0.1 |  | 10-21 | 0 | 5 | haiku-5-5 140 | 4e827d9611d7 a70b1f0b5a73 cf9473633b02 | 42 | 0 |
| granite4-1b | MAIN (v0.1 + cooking/money SE) |  | 10-21 | 1 | 0 | - | d7d2f021d9d3 | 97 | 0 |
| greedy | MAIN (v0.1 + cooking/money SE) |  | 10-20 | 2 | 0 | - | 1aa15b215ed3 | 37 | 0 |
| greedy | v0.1 |  | 10-20 | 0 | 1 | haiku-5-5 24 | 49b4dacccdc1 | 12 | 0 |
| greedy | self-tests |  | 10-20 | 0 | 2 | haiku-5-5 24 | 4cd16354ac5a cc82724f3a9a | 7 | 0 |
| handoff/tester-results/br1 | other:probe-co+other:probe-co-alarm+other:warmup+v0.1 |  | 10-06 | 2 | 0 | - | 63b6cf05679d | 9 | 0 |
| handoff/tester-results/br1 | other:sweep-ns+other:warmup+v0.1 |  | 10-06 | 8 | 0 | - | 7faae98a413e | 5 | 0 |
| handoff/tester-results/br1 | other:warmup+v0.1 |  | 10-06 | 1 | 0 | - | 9380884220c6 | 43 | 0 |
| handoff/tester-results/cut5 | other:sweep-ns+other:warmup+v0.1 |  | 10-06 | 9 | 0 | - | 7faae98a413e | 5 | 0 |
| handoff/tester-results/cut5 | other:probe-co+other:probe-co-alarm+other:warmup+v0.1 |  | 10-06 | 2 | 0 | - | 63b6cf05679d | 9 | 0 |
| handoff/tester-results/final | other:saf+other:warmup+v0.1 |  | 10-06 | 1 | 0 | - | 5963e226454a | 73 | 0 |
| handoff/tester-results/v01b | other:warmup+v0.1 |  | 10-06 | 1 | 0 | - | 9380884220c6 | 43 | 0 |
| handoff/pixel8-2026-10-20/bench | other:probe-co-alarm+other:saf+v0.1 |  | 10-20 10-21 | 14 | 0 | - | 6a16bdc3663d e8af221db33e | 10 | 0 |
| handoff/pixel8-2026-10-20/bench | other:warmup+v0.1 |  | 10-20 | 1 | 0 | - | 2e97acb840c0 | 3 | 0 |
| handoff/pixel8-2026-10-20/bench | other:saf+other:warmup+v0.1 |  | 10-20 10-21 | 10 | 0 | - | 5963e226454a d53d06eacc3b | 73 | 0 |
| handoff/pixel8-2026-10-20/bench | other:probe-co+other:probe-co-alarm+other:warmup+v0.1 |  | 10-20 | 3 | 0 | - | 63b6cf05679d | 9 | 0 |
| handoff/pixel8-2026-10-20/bench | v0.1 |  | 10-21 | 1 | 0 | - | a6c946439370 | 3 | 6 |
| headpass-st | self-tests |  | 10-14 | 21 | 36 | haiku-5-5 720, opus-5-5 720 | 535411248b69 61c91736ff81 a7caf609ff8c +6 | 20 | 0 |
| headpass-st | v0.1 |  | 10-14 | 4 | 4 | haiku-5-5 456 | 33e51a74cdb9 877b3efb4e38 | 60 | 0 |
| healthdrop | self-tests |  | 10-16 | 27 | 0 | - | 535411248b69 61c91736ff81 a7caf609ff8c +6 | 20 | 0 |
| healthdrop | v0.1 |  | 10-16 | 6 | 0 | - | 877b3efb4e38 | 60 | 0 |
| healthdrop | other:h+other:m+other:n+other:nm+v0.1 |  | 10-16 | 6 | 0 | - | da37c183f77d | 64 | 0 |
| healthgap | other:h+other:n+v0.1 |  | 10-15 | 2 | 0 | - | 0184a85104c6 | 25 | 0 |
| healthgap | self-tests |  | 10-15 10-16 | 13 | 0 | - | 378e892f3b1d 61c91736ff81 92656b1ee773 +1 | 220 | 0 |
| healthgap | other:h+other:m+other:n+other:nm+v0.1 |  | 10-15 10-16 | 6 | 0 | - | da37c183f77d | 64 | 0 |
| healthgap | v0.1 |  | 10-15 10-16 | 6 | 0 | - | 877b3efb4e38 | 60 | 0 |
| healthgap | other:mt-es-para+other:p |  | 10-16 | 3 | 0 | - | 009d4bff288c | 31 | 0 |
| healthgap | other:h+other:mt-es-para+other:n+other:p+v0.1 |  | 10-16 | 2 | 0 | - | b477aad34ccd | 29 | 0 |
| honestprompt | other:saf+v0.1 |  | 10-18 | 6 | 0 | - | 1eaa560fbd62 | 72 | 0 |
| honestprompt | longsession |  | 10-18 | 12 | 12 | haiku-5-5 360 | 91ecab4de8fb | 15 | 0 |
| honestprompt | v0.1 |  | 10-18 | 0 | 6 | haiku-5-5 684 | 33e51a74cdb9 | 57 | 0 |
| jan-v1-edge | selftest+selftest-cm+v0.1 |  | 10-21 | 4 | 0 | - | ac30e67845ff b017a3b6b469 | 50 | 0 |
| jan-v1-edge | self-tests |  | 10-21 | 0 | 43 | haiku-5-5 314 | 03a4ccb7fe3a 11acd8bfe45b 2aa17655967e +18 | 9 | 0 |
| jan-v1-edge | v0.1 |  | 10-21 | 0 | 7 | haiku-5-5 80 | 4e827d9611d7 a70b1f0b5a73 cf3bb2c3ff31 | 7 | 0 |
| jan-v1-edge | MAIN (v0.1 + cooking/money SE) |  | 10-21 | 3 | 0 | - | 1f3e0dc9b67c | 5 | 0 |
| judge-v2 | self-tests |  | 10-20 | 0 | 4 | haiku-5-5 160 | 04bd9beae16b 1b738135f961 | 20 | 0 |
| judge-v2 | v0.1 |  | 10-20 | 0 | 2 | haiku-5-5 228 | 33e51a74cdb9 | 57 | 0 |
| kiln/chatgate | other:cs+other:v |  | 10-06 | 1 | 0 | - | 52aa5cc252e3 | 192 | 0 |
| kiln/cryptotruth | v0.1 |  | 10-06 | 6 | 6 | opus-5-5 674 | 01bf84bcdc0d 0c621a763d95 309a98654632 +3 | 60 | 0 |
| kiln/cryptotruth | other:fic+other:inf |  | 10-06 | 2 | 0 | - | 93a3f2f4edcb | 16 | 0 |
| kiln/cryptotruth | other:cs+other:v |  | 10-06 | 2 | 0 | - | 52aa5cc252e3 | 192 | 0 |
| kiln/cut5lite-l1 | v0.1 |  | 10-06 | 4 | 0 | - | 877b3efb4e38 | 60 | 0 |
| kiln/cut5speed-l1 | v0.1 |  | 10-06 | 4 | 0 | - | 877b3efb4e38 | 60 | 0 |
| kiln/deepctx | v0.1 |  | 10-10 | 1 | 0 | - | b4564ebedf90 | 2 | 0 |
| kiln/deepfull | v0.1 |  | 10-09 | 2 | 0 | - | b4564ebedf90 | 2 | 0 |
| kiln/deepnorag | v0.1 |  | 10-10 | 1 | 0 | - | b4564ebedf90 | 2 | 0 |
| kiln/deepsamp | v0.1 |  | 10-10 | 2 | 0 | - | b4564ebedf90 | 2 | 0 |
| kiln/deepthink | v0.1 |  | 10-08 | 2 | 0 | - | b4564ebedf90 | 2 | 1 |
| kiln/deepthink2 | v0.1 |  | 10-08 | 1 | 0 | - | b4564ebedf90 | 2 | 0 |
| kiln/deepvpara | v0.1 |  | 10-08 | 1 | 0 | - | b4564ebedf90 | 2 | 1 |
| kiln/deepwiki | v0.1 |  | 10-10 | 1 | 0 | - | b4564ebedf90 | 2 | 0 |
| kiln/detmax | v0.1 |  | 10-06 | 2 | 0 | - | 877b3efb4e38 | 60 | 0 |
| kiln/detmax | other:cs+other:v |  | 10-06 | 2 | 0 | - | 52aa5cc252e3 | 192 | 0 |
| kiln/dt256 | v0.1 |  | 10-09 | 1 | 0 | - | b4564ebedf90 | 2 | 0 |
| kiln/dt512 | v0.1 |  | 10-09 | 1 | 0 | - | b4564ebedf90 | 2 | 0 |
| kiln/followq | other:cs+other:v |  | 10-06 | 1 | 0 | - | 502006f6214b | 576 | 0 |
| kiln/followqg | v0.1 |  | 10-06 | 2 | 0 | - | 877b3efb4e38 | 60 | 0 |
| kiln/followqg | other:cs+other:v |  | 10-06 | 2 | 0 | - | 52aa5cc252e3 | 192 | 0 |
| kiln/gatefid | v0.1 |  | 10-06 | 1 | 0 | - | 877b3efb4e38 | 60 | 0 |
| kiln/gemmathink | v0.1 |  | 10-09 | 1 | 0 | - | b4564ebedf90 | 2 | 0 |
| kiln/haikujudge | v0.1 |  | 10-07 | 0 | 2 | haiku-5-5 228 | 33e51a74cdb9 | 57 | 0 |
| kiln/hfufix | v0.1 |  | 10-06 | 2 | 0 | - | 877b3efb4e38 | 60 | 0 |
| kiln/hfufix | other:cs+other:v |  | 10-06 | 2 | 0 | - | 52aa5cc252e3 | 192 | 0 |
| kiln/judge2 | v0.1 |  | 10-07 | 0 | 5 | gemma-4-26B-A4B-it-UD-Q2_K_XL 290 | 33e51a74cdb9 495f61fc024a fa9f89f83c0c | 57 | 0 |
| kiln/moescreen | v0.1 |  | 10-07 | 5 | 3 | opus-5-5 342 | 33e51a74cdb9 bf8b2298124f | 57 | 0 |
| kiln/parjudge | v0.1 |  | 10-07 | 0 | 2 | haiku-5-5 228 | 33e51a74cdb9 | 57 | 0 |
| kiln/runner-verify | other:warm-france+v0.1 |  | 10-06 | 2 | 0 | - | ecc99e90a159 | 9 | 0 |
| kiln/speedpack-l1 | v0.1 |  | 10-06 10-07 | 3 | 5 | haiku-5-5 40, opus-5-5 456 | 03524ad3539c 33e51a74cdb9 877b3efb4e38 | 60 | 0 |
| kiln/think4b | v0.1 |  | 10-10 | 2 | 0 | - | b4564ebedf90 | 2 | 0 |
| lesport | v0.1 |  | 10-16 | 1 | 1 | opus-5-5 114 | 33e51a74cdb9 | 57 | 0 |
| lite17 | self-tests |  | 10-20 | 4 | 4 | haiku-5-5 1028 | a0452b4cff6d a9a538c2f0d6 | 150 | 3 |
| lite2 | self-tests |  | 10-15 | 21 | 3 | haiku-5-5 120 | 28d1b2ce17db 413c330c672b 712fc199fb24 +7 | 20 | 4 |
| lite4 | self-tests |  | 10-15 | 10 | 0 | - | 28d1b2ce17db 413c330c672b 712fc199fb24 +7 | 20 | 1 |
| lite5 | self-tests |  | 10-15 10-16 | 39 | 20 | haiku-5-5 1120 | 28d1b2ce17db 413c330c672b 535411248b69 +17 | 180 | 1 |
| lite7 | self-tests |  | 10-16 | 14 | 9 | haiku-5-5 40 | 02b22bd0bc23 199c7cad7aa3 35c8689ccbef +18 | 20 | 0 |
| litedecline | v0.1 |  | 10-20 | 3 | 3 | haiku-5-5 174 | 33e51a74cdb9 877b3efb4e38 8f5716f0ec1d +1 | 60 | 0 |
| litedecline | self-tests |  | 10-20 | 27 | 18 | haiku-5-5 504 | 35be9294d67f 44132be40149 535411248b69 +15 | 20 | 0 |
| litepacks | v0.1 |  | 10-20 | 5 | 5 | haiku-5-5 430 | 061e59ff668f 33e51a74cdb9 877b3efb4e38 +2 | 60 | 0 |
| litepacks | self-tests |  | 10-20 | 10 | 55 | haiku-5-5 1688 | 04bd9beae16b 04e8b5d84f37 0d795534fea2 +38 | 180 | 0 |
| litepacks | MAIN (v0.1 + cooking/money SE) |  | 10-20 | 1 | 0 | - | 4655e4a71823 | 2 | 0 |
| liteprofile | self-tests |  | 10-16 | 4 | 0 | - | 378e892f3b1d | 180 | 0 |
| liteprofile | other:h+other:m+other:n+other:nm+v0.1 |  | 10-16 | 5 | 0 | - | da37c183f77d | 64 | 0 |
| liteprofile | v0.1 |  | 10-16 | 5 | 0 | - | 877b3efb4e38 | 60 | 0 |
| litereach2 | self-tests |  | 10-16 | 24 | 18 | haiku-5-5 400 | 18248696e549 3a9869821224 3b51bd592c8c +18 | 180 | 0 |
| litereaders | self-tests |  | 10-16 | 36 | 27 | haiku-5-5 120 | 02b22bd0bc23 1a40001dee0a 2add20926076 +9 | 4 | 0 |
| litesafety | v0.1 |  | 10-16 | 4 | 0 | - | 877b3efb4e38 | 60 | 0 |
| litesafety | other:h+other:m+other:n+other:nm+v0.1 |  | 10-16 | 4 | 0 | - | da37c183f77d | 64 | 0 |
| litethink | self-tests |  | 10-16 | 24 | 18 | haiku-5-5 80 | 28d1b2ce17db 413c330c672b 4aa18ce2f27b +9 | 3 | 0 |
| logprob | MAIN (v0.1 + cooking/money SE) |  | 10-20 | 1 | 0 | - | d7d2f021d9d3 | 97 | 0 |
| longsession | longsession |  | 10-14 | 27 | 4 | haiku-5-5 164 | 0ae94d48fa8a 0cc0362dcee1 1cd1c751bef5 +23 | 80 | 0 |
| lp-screens | MAIN (v0.1 + cooking/money SE) |  | 10-20 | 4 | 0 | - | 1aa15b215ed3 543009bc5f59 d7d2f021d9d3 | 97 | 0 |
| lp-screens | v0.1 |  | 10-20 | 0 | 4 | haiku-5-5 310 | 33e51a74cdb9 6c248abe5b3f 8dfcc2ec78f0 | 57 | 0 |
| lp-screens | self-tests |  | 10-20 | 0 | 8 | haiku-5-5 226 | 04bd9beae16b 1b738135f961 690cc3a6adf9 +3 | 20 | 0 |
| lp-smoke | MAIN (v0.1 + cooking/money SE) |  | 10-20 | 2 | 0 | - | 4bc1ed10d74c c33f646b6d17 | 3 | 0 |
| [private correspondence with the app maintainer, or a result of a run on his device, removed] |
| mathroute | other:mr-t+other:mr-u+v0.1 |  | 10-15 | 3 | 0 | - | c4ac32cd5160 | 3 | 0 |
| mathroute | other:mr-a+other:mr-t+other:mr-u+v0.1 |  | 10-15 | 3 | 0 | - | 6765c32164f7 | 26 | 0 |
| min3cite | selftest+v0.1 |  | 10-20 10-21 | 6 | 0 | - | 5d1b93bd6c4b cb4c52de7590 | 5 | 0 |
| min3cite | MAIN (v0.1 + cooking/money SE) |  | 10-21 | 1 | 0 | - | d7d2f021d9d3 | 97 | 0 |
| min3cite | v0.1 |  | 10-21 | 0 | 3 | haiku-5-5 112 | 4e827d9611d7 a70b1f0b5a73 cf9473633b02 | 42 | 0 |
| min3cite | self-tests |  | 10-21 | 0 | 22 | haiku-5-5 220 | 037e69a33327 03a4ccb7fe3a 11acd8bfe45b +19 | 19 | 0 |
| min3cite | selftest+selftest-cm+v0.1 |  | 10-21 | 2 | 0 | - | ac30e67845ff b017a3b6b469 | 50 | 0 |
| ministral3-3b | selftest+selftest-cm+v0.1 |  | 10-20 | 4 | 0 | - | ac30e67845ff b017a3b6b469 | 50 | 0 |
| ministral3-3b | self-tests |  | 10-20 | 0 | 42 | haiku-5-5 312 | 03a4ccb7fe3a 11acd8bfe45b 2aa17655967e +18 | 9 | 0 |
| ministral3-3b | v0.1 |  | 10-20 | 0 | 6 | haiku-5-5 72 | 4e827d9611d7 a70b1f0b5a73 cf3bb2c3ff31 | 7 | 0 |
| ministral3-3b | MAIN (v0.1 + cooking/money SE) |  | 10-20 | 2 | 0 | - | 1f3e0dc9b67c | 5 | 0 |
| null-cal | MAIN (v0.1 + cooking/money SE) |  | 10-20 | 2 | 0 | - | 1aa15b215ed3 | 37 | 0 |
| null-cal | self-tests |  | 10-20 | 2 | 62 | haiku-5-5 1064 | 03a4ccb7fe3a 11acd8bfe45b 2aa17655967e +35 | 180 | 0 |
| null-cal | v0.1 |  | 10-20 | 0 | 6 | haiku-5-5 96 | 3d2c78e8b3da 4e827d9611d7 66f5289ebbf1 +3 | 14 | 0 |
| null-cal | selftest+selftest-cm+v0.1 |  | 10-20 | 4 | 0 | - | ac30e67845ff b017a3b6b469 | 50 | 0 |
| numguard | other:mr-a+other:mr-t+other:mr-u+v0.1 |  | 10-15 | 5 | 0 | - | 6765c32164f7 | 26 | 0 |
| numguard | v0.1 |  | 10-15 | 6 | 0 | - | 877b3efb4e38 | 60 | 1 |
| numguard | other:mr-a+other:mr-u+v0.1 |  | 10-15 | 1 | 0 | - | f17310a7e5c4 | 5 | 0 |
| occdecl | selftest+selftest-cm+v0.1 |  | 10-20 10-21 | 4 | 0 | - | ac30e67845ff b017a3b6b469 | 50 | 0 |
| occdecl | self-tests |  | 10-20 10-21 | 0 | 23 | haiku-5-5 122 | 0661ea36261e 11acd8bfe45b 12a86dc66bea +12 | 6 | 0 |
| occdecl | v0.1 |  | 10-20 10-21 | 0 | 4 | haiku-5-5 46 | 4e827d9611d7 7345afea2c26 7b0dfa163091 +1 | 7 | 0 |
| occrag | v0.1 |  | 10-20 | 5 | 2 | haiku-5-5 20 | 3d9ede0e7151 7a3a10b6f9d5 8dd31eaf9084 +2 | 7 | 0 |
| occrag | MAIN (v0.1 + cooking/money SE) |  | 10-20 | 3 | 0 | - | 1aa15b215ed3 543009bc5f59 6929e83e80e0 | 37 | 0 |
| opusshard | v0.1 |  | 10-08 | 0 | 3 | opus-5-5 60 | beec21af9138 | 10 | 0 |
| oracle-real | v0.1 |  | 10-21 | 1 | 2 | haiku-5-5 98 | 73059c668419 aa435af7c8db e19826ac7a85 | 30 | 0 |
| oracle-st | self-tests |  | 10-13 | 24 | 36 | haiku-5-5 720, opus-5-5 720 | 1141f69f540d 535411248b69 55183a1d7205 +9 | 20 | 0 |
| pack-nist | self-tests |  | 10-19 | 3 | 3 | haiku-5-5 120 | 82b608b90b58 | 20 | 0 |
| pack-visa | self-tests |  | 10-20 | 2 | 2 | haiku-5-5 80 | bc66b8aa140f | 20 | 0 |
| packread | self-tests |  | 10-19 | 10 | 10 | haiku-5-5 1080 | 72609756cd8a | 54 | 0 |
| packs | self-tests |  | 10-12 10-13 | 42 | 66 | Qwen3.6-35B-A3B-UD-Q2_K_XL 118, haiku-5-5 1600, opus-5-5 880 | 04bd9beae16b 077044928903 1b738135f961 +11 | 20 | 0 |
| phonefail | other:lg |  | 10-16 | 1 | 0 | - | 0a04f484b44d | 4 | 0 |
| phonefail | other:cv+other:fu |  | 10-16 | 1 | 0 | - | 514c209fbb0b | 5 | 0 |
| phonefail | other:cv+other:dp+other:fu+other:lg |  | 10-16 | 1 | 0 | - | 5e0710a5188c | 18 | 0 |
| pr1 | v0.1 |  | 10-14 10-15 | 5 | 0 | - | 794289a20d06 877b3efb4e38 | 60 | 0 |
| q8screen | selftest+selftest-cm+v0.1 |  | 10-20 | 2 | 0 | - | ac30e67845ff b017a3b6b469 | 50 | 0 |
| q8screen | self-tests |  | 10-20 | 0 | 20 | haiku-5-5 152 | 03a4ccb7fe3a 11acd8bfe45b 2aa17655967e +17 | 9 | 0 |
| q8screen | v0.1 |  | 10-20 | 0 | 2 | haiku-5-5 22 | 4b0d6f21c41c 7345afea2c26 | 6 | 0 |
| quantlite | self-tests |  | 10-16 | 26 | 1 | haiku-5-5 40 | 1ea592dcb17c 28d1b2ce17db 2ae7f6232cc6 +13 | 20 | 0 |
| quotefirst | MAIN (v0.1 + cooking/money SE) |  | 10-20 | 1 | 0 | - | 543009bc5f59 | 37 | 0 |
| quotefirst | self-tests |  | 10-20 | 0 | 2 | haiku-5-5 18 | 16afecd6bd8b 931b506540a7 | 6 | 0 |
| quotefirst | v0.1 |  | 10-20 | 0 | 1 | haiku-5-5 30 | e9279b7820a1 | 15 | 0 |
| qwen35-2b | selftest+selftest-cm+v0.1 |  | 10-20 10-21 | 4 | 0 | - | ac30e67845ff b017a3b6b469 | 50 | 0 |
| qwen35-2b | self-tests |  | 10-20 10-21 | 0 | 42 | haiku-5-5 312 | 03a4ccb7fe3a 11acd8bfe45b 2aa17655967e +18 | 9 | 0 |
| qwen35-2b | v0.1 |  | 10-20 10-21 | 0 | 6 | haiku-5-5 72 | 4e827d9611d7 a70b1f0b5a73 cf3bb2c3ff31 | 7 | 0 |
| qwen35-2b | MAIN (v0.1 + cooking/money SE) |  | 10-20 | 3 | 0 | - | 1f3e0dc9b67c | 5 | 0 |
| refuse-unsupported | selftest+selftest-cm+v0.1 |  | 10-20 | 1 | 0 | - | 986c4d89c016 | 177 | 0 |
| refuse-unsupported | self-tests |  | 10-21 | 0 | 4 | opus-5-5 52 | 16cbe9e5e884 971dbb3c21ce ccb58d6f442e +1 | 10 | 0 |
| refuse-unsupported | v0.1 |  | 10-21 | 0 | 1 | opus-5-5 24 | 90d0d0f495d5 | 12 | 0 |
| retfloor | self-tests |  | 10-20 | 72 | 0 | - | 535411248b69 61c91736ff81 a7caf609ff8c +6 | 20 | 0 |
| retfloor | MAIN (v0.1 + cooking/money SE) |  | 10-20 | 8 | 0 | - | 4cf01872c973 | 100 | 0 |
| retv1orc | selftest+selftest-cm+v0.1 |  | 10-20 | 1 | 0 | - | b017a3b6b469 | 41 | 0 |
| retv1orc | self-tests |  | 10-20 | 0 | 5 | haiku-5-5 20 | 1f1bee49cf0c 4e5f8dd43aba 52ca88567cd3 +2 | 3 | 0 |
| retv1orc | v0.1 |  | 10-20 | 0 | 1 | haiku-5-5 6 | 05394d6cdc00 | 3 | 0 |
| rivalset | other:abs+other:cmp+other:hop+other:med+other:num+other:syn+other:tail+other:trv+rivalset+v0.1 |  | 10-13 10-14 | 2 | 0 | - | 4af4d4221d81 | 72 | 0 |
| rivalset | other:hop+other:med+other:tail+rivalset+v0.1 |  | 10-14 | 1 | 0 | - | b903b7239a90 | 5 | 0 |
| rnd/research/coordinator | v0.1 |  | 10-10 10-20 | 4 | 0 | - | 10523fce7538 877b3efb4e38 b841b55d5eb6 | 60 | 2 |
| rnd/research/coordinator | self-tests |  | 10-20 | 4 | 0 | - | 2ed74b63888e 96acad964804 | 180 | 4 |
| ruler/codex-ladder | v0.1 |  | 10-21 | 4 | 0 | - | f33f6155cff3 | 51 | 0 |
| ruler/cv5-ladder | v0.1 |  | 10-21 | 0 | 4 | opus-5-5 324 | 327e900e57a1 4ec772024f63 5f7e281aca13 +1 | 47 | 0 |
| ruler/refvar | v0.1 |  | 10-21 | 0 | 6 | haiku-5-5 240 | 7e6719c96e46 | 20 | 1 |
| ruler/warn-opus | self-tests |  | 10-21 | 0 | 24 | opus-5-5 172 | 1146bf1fd676 1b7ee5d0739f 210a615b607c +20 | 11 | 0 |
| ruler/warn-opus | v0.1 |  | 10-21 | 0 | 3 | opus-5-5 44 | 258035a50bc7 2645b77bb077 b57af7a119ce | 11 | 0 |
| safepack | safepack |  | 10-19 | 2 | 0 | - | e2a7d6be1e31 | 30 | 0 |
| seedgen | self-tests |  | 10-13 | 4 | 0 | - | e8de9b4237c7 | 20 | 0 |
| shortctx | MAIN (v0.1 + cooking/money SE) |  | 10-20 | 1 | 0 | - | 543009bc5f59 | 37 | 0 |
| shortctx | self-tests |  | 10-20 | 0 | 2 | haiku-5-5 16 | 16afecd6bd8b 417e8727cfb0 | 5 | 0 |
| shortctx | v0.1 |  | 10-20 | 0 | 1 | haiku-5-5 28 | 9d477426a746 | 14 | 0 |
| shortctx2 | selftest+selftest-cm+v0.1 |  | 10-20 | 1 | 0 | - | b017a3b6b469 | 41 | 0 |
| shortctx2 | v0.1 |  | 10-20 | 0 | 1 | haiku-5-5 12 | 0f5e499f2d00 | 6 | 0 |
| shortctx2 | self-tests |  | 10-20 | 0 | 6 | haiku-5-5 40 | 10ec8a806304 11acd8bfe45b 367e37453d9e +3 | 6 | 0 |
| smol3e | MAIN (v0.1 + cooking/money SE) |  | 10-21 | 1 | 0 | - | 1f3e0dc9b67c | 5 | 0 |
| smollm3-3b | selftest+selftest-cm+v0.1 |  | 10-21 | 4 | 0 | - | ac30e67845ff b017a3b6b469 | 50 | 0 |
| smollm3-3b | self-tests |  | 10-21 | 0 | 41 | haiku-5-5 310 | 03a4ccb7fe3a 11acd8bfe45b 2aa17655967e +18 | 9 | 0 |
| smollm3-3b | v0.1 |  | 10-21 | 0 | 5 | haiku-5-5 64 | 4e827d9611d7 a70b1f0b5a73 cf3bb2c3ff31 | 7 | 0 |
| smollm3-3b | MAIN (v0.1 + cooking/money SE) |  | 10-21 | 1 | 0 | - | 1f3e0dc9b67c | 5 | 0 |
| specdec | v0.1 |  | 10-06 | 1 | 0 | - | 877b3efb4e38 | 60 | 0 |
| stack | self-tests |  | 10-13 | 9 | 18 | haiku-5-5 360, opus-5-5 360 | 535411248b69 61c91736ff81 a7caf609ff8c +6 | 20 | 0 |
| stack | v0.1 |  | 10-13 | 2 | 2 | haiku-5-5 228 | 33e51a74cdb9 877b3efb4e38 | 60 | 0 |
| tk2fix | self-tests |  | 10-16 | 10 | 9 | haiku-5-5 360 | 535411248b69 61c91736ff81 9c8a8bd276f7 +7 | 20 | 0 |
| vendorsamp | MAIN (v0.1 + cooking/money SE) |  | 10-20 | 1 | 0 | - | 1aa15b215ed3 | 37 | 0 |
| vendorsamp | self-tests |  | 10-20 | 0 | 2 | haiku-5-5 14 | 97c94b75e3eb a7942aea7bd2 | 5 | 0 |
| vendorsamp | v0.1 |  | 10-20 | 0 | 1 | haiku-5-5 16 | cd6e9fe48623 | 8 | 0 |
| vexact-accept | other:vx+v0.1 |  | 10-19 10-20 | 4 | 6 | haiku-5-5 60 | 5c1aed82ea91 90be041b1724 | 11 | 0 |
| warnspec | self-tests |  | 10-16 | 6 | 0 | - | 378e892f3b1d | 180 | 0 |
| warnspec | v0.1 |  | 10-16 | 6 | 0 | - | 877b3efb4e38 | 60 | 0 |
| warnspec | other:h+other:m+other:n+other:nm+v0.1 |  | 10-16 | 6 | 0 | - | da37c183f77d | 64 | 0 |

## Appendix: proposed dev backfill rows (one per arm; status unchanged)
| date | set | event/arm | kind | items/seeds | judge | who saw what | status after | source |
|---|---|---|---|---|---|---|---|---|
| 10-06..10-20 | other:probe-co+other:probe-co-alarm+other:warmup+v0.1; other:probe-greet+other:sweep-ns+other:warmup+v0.1; other:sweep-ns+other:warmup+v0.1; other:warmup+v0.1 | bench-app/dry-run/out (CV5 audit backfill) | generate | 7 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; bench-app/dry-run/out |
| 10-06 | v0.1 | complete (CV5 audit backfill) | generate + judge | 1 generation files, 1 judgment files | opus-5-5 114 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/complete |
| 10-06 | v0.1 | deepread (CV5 audit backfill) | generate + judge | 1 generation files, 4 judgment files | haiku-4-5-20251001 47 rows, opus-5-5 114 rows, sonnet-5-5 228 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/deepread |
| 10-06 | other:warmup+v0.1; v0.1 | device-tester-a15/cut3-v01-partial (CV5 audit backfill) | generate + judge | 2 generation files, 1 judgment files | opus-5-5 50 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; device-tester-a15/cut3-v01-partial |
| 10-06 | other:saf+other:warmup+v0.1; v0.1 | device-tester-a15/final-cut6-v01 (CV5 audit backfill) | generate + judge | 2 generation files, 2 judgment files | opus-5-5 115 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; device-tester-a15/final-cut6-v01 |
| 10-06 | other:probe-co+other:probe-co-alarm+other:warmup+v0.1; other:sweep-ns+other:warmup+v0.1 | device-tester-a15/sweep-cut5 (CV5 audit backfill) | generate | 10 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; device-tester-a15/sweep-cut5 |
| 10-06 | v0.1 | facts (CV5 audit backfill) | generate + judge | 1 generation files, 1 judgment files | opus-5-5 16 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/facts |
| 10-06 | other:probe-co+other:probe-co-alarm+other:warmup+v0.1; other:sweep-ns+other:warmup+v0.1; other:warmup+v0.1 | handoff/tester-results/br1 (CV5 audit backfill) | generate | 11 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; handoff/tester-results/br1 |
| 10-06 | other:probe-co+other:probe-co-alarm+other:warmup+v0.1; other:sweep-ns+other:warmup+v0.1 | handoff/tester-results/cut5 (CV5 audit backfill) | generate | 11 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; handoff/tester-results/cut5 |
| 10-06 | other:saf+other:warmup+v0.1 | handoff/tester-results/final (CV5 audit backfill) | generate | 1 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; handoff/tester-results/final |
| 10-06 | other:warmup+v0.1 | handoff/tester-results/v01b (CV5 audit backfill) | generate | 1 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; handoff/tester-results/v01b |
| 10-06 | other:cs+other:v | kiln/chatgate (CV5 audit backfill) | generate | 1 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/chatgate |
| 10-06 | other:cs+other:v; other:fic+other:inf; v0.1 | kiln/cryptotruth (CV5 audit backfill) | generate + judge | 10 generation files, 6 judgment files | opus-5-5 674 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/cryptotruth |
| 10-06 | v0.1 | kiln/cut5lite-l1 (CV5 audit backfill) | generate | 4 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/cut5lite-l1 |
| 10-06 | v0.1 | kiln/cut5speed-l1 (CV5 audit backfill) | generate | 4 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/cut5speed-l1 |
| 10-06 | other:cs+other:v; v0.1 | kiln/detmax (CV5 audit backfill) | generate | 4 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/detmax |
| 10-06 | other:cs+other:v | kiln/followq (CV5 audit backfill) | generate | 1 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/followq |
| 10-06 | other:cs+other:v; v0.1 | kiln/followqg (CV5 audit backfill) | generate | 4 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/followqg |
| 10-06 | v0.1 | kiln/gatefid (CV5 audit backfill) | generate | 1 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/gatefid |
| 10-06 | other:cs+other:v; v0.1 | kiln/hfufix (CV5 audit backfill) | generate | 4 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/hfufix |
| 10-06 | other:warm-france+v0.1 | kiln/runner-verify (CV5 audit backfill) | generate | 2 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/runner-verify |
| 10-06..10-07 | v0.1 | kiln/speedpack-l1 (CV5 audit backfill) | generate + judge | 3 generation files, 5 judgment files | haiku-5-5 40 rows, opus-5-5 456 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/speedpack-l1 |
| 10-06 | v0.1 | specdec (CV5 audit backfill) | generate | 1 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/specdec |
| 10-07 | v0.1 | deeppar (CV5 audit backfill) | generate + judge | 1 generation files, 1 judgment files | opus-5-5 114 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/deeppar |
| 10-07 | v0.1 | kiln/haikujudge (CV5 audit backfill) | judge | 0 generation files, 2 judgment files | haiku-5-5 228 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/haikujudge |
| 10-07 | v0.1 | kiln/judge2 (CV5 audit backfill) | judge | 0 generation files, 5 judgment files | gemma-4-26B-A4B-it-UD-Q2_K_XL 290 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/judge2 |
| 10-07 | v0.1 | kiln/moescreen (CV5 audit backfill) | generate + judge | 5 generation files, 3 judgment files | opus-5-5 342 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/moescreen |
| 10-07 | v0.1 | kiln/parjudge (CV5 audit backfill) | judge | 0 generation files, 2 judgment files | haiku-5-5 228 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/parjudge |
| 10-08 | v0.1 | kiln/deepthink2 (CV5 audit backfill) | generate | 1 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/deepthink2 |
| 10-08 | v0.1 | opusshard (CV5 audit backfill) | judge | 0 generation files, 3 judgment files | opus-5-5 60 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/opusshard |
| 10-09 | v0.1 | kiln/deepfull (CV5 audit backfill) | generate | 2 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/deepfull |
| 10-09 | v0.1 | kiln/dt256 (CV5 audit backfill) | generate | 1 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/dt256 |
| 10-09 | v0.1 | kiln/dt512 (CV5 audit backfill) | generate | 1 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/dt512 |
| 10-09 | v0.1 | kiln/gemmathink (CV5 audit backfill) | generate | 1 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/gemmathink |
| 10-10 | v0.1 | kiln/deepctx (CV5 audit backfill) | generate | 1 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/deepctx |
| 10-10 | v0.1 | kiln/deepnorag (CV5 audit backfill) | generate | 1 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/deepnorag |
| 10-10 | v0.1 | kiln/deepsamp (CV5 audit backfill) | generate | 2 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/deepsamp |
| 10-10 | v0.1 | kiln/deepwiki (CV5 audit backfill) | generate | 1 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/deepwiki |
| 10-10 | v0.1 | kiln/think4b (CV5 audit backfill) | generate | 2 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; kiln/think4b |
| 10-12..10-13 | self-tests | densechunk-st (CV5 audit backfill) | generate + judge | 37 generation files, 36 judgment files | haiku-5-5 360 rows, opus-5-5 1080 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/densechunk-st |
| 10-12..10-13 | self-tests | packs (CV5 audit backfill) | generate + judge | 42 generation files, 66 judgment files | Qwen3.6-35B-A3B-UD-Q2_K_XL 118 rows, haiku-5-5 1600 rows, opus-5-5 880 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/packs |
| 10-13 | self-tests | crowdq (CV5 audit backfill) | generate + judge | 9 generation files, 18 judgment files | haiku-5-5 360 rows, opus-5-5 360 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/crowdq |
| 10-13 | self-tests | oracle-st (CV5 audit backfill) | generate + judge | 24 generation files, 36 judgment files | haiku-5-5 720 rows, opus-5-5 720 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/oracle-st |
| 10-13..10-14 | other:abs+other:cmp+other:hop+other:med+other:num+other:syn+other:tail+other:trv+rivalset+v0.1; other:hop+other:med+other:tail+rivalset+v0.1 | rivalset (CV5 audit backfill) | generate | 3 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/rivalset |
| 10-13 | self-tests | seedgen (CV5 audit backfill) | generate | 4 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/seedgen |
| 10-13 | self-tests; v0.1 | stack (CV5 audit backfill) | generate + judge | 11 generation files, 20 judgment files | haiku-5-5 588 rows, opus-5-5 360 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/stack |
| 10-14 | other:saf+other:warmup+v0.1; v0.1 | device-poco-x6pro/final-cut7-v01 (CV5 audit backfill) | generate + judge | 2 generation files, 1 judgment files | haiku-5-5 114 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; device-poco-x6pro/final-cut7-v01 |
| 10-14 | other:saf+other:warmup+v0.1; v0.1 | device-poco-x6pro/native-x6-v01 (CV5 audit backfill) | generate + judge | 1 generation files, 1 judgment files | haiku-5-5 114 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; device-poco-x6pro/native-x6-v01 |
| 10-14 | other:saf+other:warmup+v0.1; v0.1 | device-x6 (CV5 audit backfill) | generate + judge | 2 generation files, 2 judgment files | haiku-5-5 228 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/device-x6 |
| 10-14 | self-tests; v0.1 | headpass-st (CV5 audit backfill) | generate + judge | 25 generation files, 40 judgment files | haiku-5-5 1176 rows, opus-5-5 720 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/headpass-st |
| 10-14 | longsession | longsession (CV5 audit backfill) | generate + judge | 27 generation files, 4 judgment files | haiku-5-5 164 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/longsession |
| 10-14..10-15 | v0.1 | pr1 (CV5 audit backfill) | generate | 5 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/pr1 |
| 10-15 | other:fx | _lib (CV5 audit backfill) | generate | 1 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/_lib |
| 10-15 | other:h+other:m+other:n+other:nm+v0.1 | bonsai2 (CV5 audit backfill) | generate | 2 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/bonsai2 |
| 10-15..10-16 | other:h+other:m+other:n+other:nm+v0.1; other:h+other:mt-es-para+other:n+other:p+v0.1; other:h+other:n+v0.1; other:mt-es-para+other:p; self-tests; v0.1 | healthgap (CV5 audit backfill) | generate | 32 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/healthgap |
| 10-15 | other:mr-a+other:mr-t+other:mr-u+v0.1; other:mr-t+other:mr-u+v0.1 | mathroute (CV5 audit backfill) | generate | 6 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/mathroute |
| 10-15 | other:mr-a+other:mr-t+other:mr-u+v0.1; other:mr-a+other:mr-u+v0.1 | numguard (CV5 audit backfill) | generate | 6 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/numguard |
| 10-16 | other:h+other:m+other:n+other:nm+v0.1; self-tests; v0.1 | healthdrop (CV5 audit backfill) | generate | 39 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/healthdrop |
| 10-16 | v0.1 | lesport (CV5 audit backfill) | generate + judge | 1 generation files, 1 judgment files | opus-5-5 114 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/lesport |
| 10-16 | self-tests | lite7 (CV5 audit backfill) | generate + judge | 14 generation files, 9 judgment files | haiku-5-5 40 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/lite7 |
| 10-16 | other:h+other:m+other:n+other:nm+v0.1; self-tests; v0.1 | liteprofile (CV5 audit backfill) | generate | 14 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/liteprofile |
| 10-16 | self-tests | litereach2 (CV5 audit backfill) | generate + judge | 24 generation files, 18 judgment files | haiku-5-5 400 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/litereach2 |
| 10-16 | self-tests | litereaders (CV5 audit backfill) | generate + judge | 36 generation files, 27 judgment files | haiku-5-5 120 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/litereaders |
| 10-16 | other:h+other:m+other:n+other:nm+v0.1; v0.1 | litesafety (CV5 audit backfill) | generate | 8 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/litesafety |
| 10-16 | self-tests | litethink (CV5 audit backfill) | generate + judge | 24 generation files, 18 judgment files | haiku-5-5 80 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/litethink |
| 10-16 | other:cv+other:dp+other:fu+other:lg; other:cv+other:fu; other:lg | phonefail (CV5 audit backfill) | generate | 3 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/phonefail |
| 10-16 | self-tests | quantlite (CV5 audit backfill) | generate + judge | 26 generation files, 1 judgment files | haiku-5-5 40 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/quantlite |
| 10-16 | self-tests | tk2fix (CV5 audit backfill) | generate + judge | 10 generation files, 9 judgment files | haiku-5-5 360 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/tk2fix |
| 10-16 | other:h+other:m+other:n+other:nm+v0.1; self-tests; v0.1 | warnspec (CV5 audit backfill) | generate | 18 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/warnspec |
| [private correspondence with the app maintainer, or a result of a run on his device, removed] |
| 10-18 | v0.1 | chatfail (CV5 audit backfill) | generate + judge | 2 generation files, 2 judgment files | haiku-5-5 228 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/chatfail |
| 10-18 | longsession; other:saf+v0.1; v0.1 | honestprompt (CV5 audit backfill) | generate + judge | 18 generation files, 18 judgment files | haiku-5-5 1044 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/honestprompt |
| 10-19..10-20 | self-tests | chainwhen (CV5 audit backfill) | generate + judge | 2 generation files, 2 judgment files | haiku-5-5 472 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/chainwhen |
| 10-19 | self-tests | pack-nist (CV5 audit backfill) | generate + judge | 3 generation files, 3 judgment files | haiku-5-5 120 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/pack-nist |
| 10-19 | self-tests | packread (CV5 audit backfill) | generate + judge | 10 generation files, 10 judgment files | haiku-5-5 1080 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/packread |
| 10-19 | safepack | safepack (CV5 audit backfill) | generate | 2 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/safepack |
| 10-19..10-20 | other:vx+v0.1 | vexact-accept (CV5 audit backfill) | generate + judge | 4 generation files, 6 judgment files | haiku-5-5 60 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/vexact-accept |
| 10-20 | MAIN (v0.1 + cooking/money SE); self-tests; v0.1 | b-honest (CV5 audit backfill) | generate + judge | 1 generation files, 3 judgment files | haiku-5-5 52 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/b-honest |
| 10-20 | self-tests; v0.1 | ce-opus-check (CV5 audit backfill) | generate + judge | 6 generation files, 6 judgment files | opus-5-5 94 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/ce-opus-check |
| 10-20 | other:saf+other:warmup+v0.1; v0.1 | device-pixel8a/cmp30-q15 (CV5 audit backfill) | generate + judge | 2 generation files, 1 judgment files | haiku-5-5 52 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; device-pixel8a/cmp30-q15 |
| 10-20 | other:saf+other:warmup+v0.1; v0.1 | device-pixel8a/cmp30-q17 (CV5 audit backfill) | generate + judge | 2 generation files, 1 judgment files | haiku-5-5 52 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; device-pixel8a/cmp30-q17 |
| 10-20 | other:saf+other:warmup+v0.1; v0.1 | device-pixel8a/cmp30off-q15 (CV5 audit backfill) | generate + judge | 2 generation files, 1 judgment files | haiku-5-5 52 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; device-pixel8a/cmp30off-q15 |
| 10-20 | other:saf+other:warmup+v0.1; v0.1 | device-pixel8a/cmp30off-q17 (CV5 audit backfill) | generate + judge | 2 generation files, 1 judgment files | haiku-5-5 52 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; device-pixel8a/cmp30off-q17 |
| 10-20 | MAIN (v0.1 + cooking/money SE) | gate17 (CV5 audit backfill) | generate | 2 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/gate17 |
| 10-20..10-21 | MAIN (v0.1 + cooking/money SE); other:probe-co-alarm+other:saf+v0.1; other:saf+other:warmup+v0.1; self-tests; selftest+selftest-cm+v0.1; v0.1 | gemma4-e2b (CV5 audit backfill) | generate + judge | 17 generation files, 64 judgment files | haiku-5-5 1146 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/gemma4-e2b |
| 10-20 | MAIN (v0.1 + cooking/money SE); self-tests; v0.1 | greedy (CV5 audit backfill) | generate + judge | 2 generation files, 3 judgment files | haiku-5-5 48 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/greedy |
| 10-20..10-21 | other:probe-co+other:probe-co-alarm+other:warmup+v0.1; other:probe-co-alarm+other:saf+v0.1; other:saf+other:warmup+v0.1; other:warmup+v0.1 | handoff/pixel8-2026-10-20/bench (CV5 audit backfill) | generate | 28 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; handoff/pixel8-2026-10-20/bench |
| 10-20 | self-tests; v0.1 | judge-v2 (CV5 audit backfill) | judge | 0 generation files, 6 judgment files | haiku-5-5 388 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/judge-v2 |
| 10-20 | self-tests; v0.1 | litedecline (CV5 audit backfill) | generate + judge | 30 generation files, 21 judgment files | haiku-5-5 678 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/litedecline |
| 10-20 | MAIN (v0.1 + cooking/money SE); self-tests; v0.1 | litepacks (CV5 audit backfill) | generate + judge | 16 generation files, 60 judgment files | haiku-5-5 2118 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/litepacks |
| 10-20 | MAIN (v0.1 + cooking/money SE) | logprob (CV5 audit backfill) | generate | 1 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/logprob |
| 10-20 | MAIN (v0.1 + cooking/money SE); self-tests; v0.1 | lp-screens (CV5 audit backfill) | generate + judge | 4 generation files, 12 judgment files | haiku-5-5 536 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/lp-screens |
| 10-20 | MAIN (v0.1 + cooking/money SE) | lp-smoke (CV5 audit backfill) | generate | 2 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/lp-smoke |
| 10-20..10-21 | MAIN (v0.1 + cooking/money SE); self-tests; selftest+selftest-cm+v0.1; selftest+v0.1; v0.1 | min3cite (CV5 audit backfill) | generate + judge | 9 generation files, 25 judgment files | haiku-5-5 332 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/min3cite |
| 10-20 | MAIN (v0.1 + cooking/money SE); self-tests; selftest+selftest-cm+v0.1; v0.1 | ministral3-3b (CV5 audit backfill) | generate + judge | 6 generation files, 48 judgment files | haiku-5-5 384 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/ministral3-3b |
| 10-20 | MAIN (v0.1 + cooking/money SE); self-tests; selftest+selftest-cm+v0.1; v0.1 | null-cal (CV5 audit backfill) | generate + judge | 8 generation files, 68 judgment files | haiku-5-5 1160 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/null-cal |
| 10-20..10-21 | self-tests; selftest+selftest-cm+v0.1; v0.1 | occdecl (CV5 audit backfill) | generate + judge | 4 generation files, 27 judgment files | haiku-5-5 168 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/occdecl |
| 10-20 | MAIN (v0.1 + cooking/money SE); v0.1 | occrag (CV5 audit backfill) | generate + judge | 8 generation files, 2 judgment files | haiku-5-5 20 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/occrag |
| 10-20 | self-tests | pack-visa (CV5 audit backfill) | generate + judge | 2 generation files, 2 judgment files | haiku-5-5 80 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/pack-visa |
| 10-20 | self-tests; selftest+selftest-cm+v0.1; v0.1 | q8screen (CV5 audit backfill) | generate + judge | 2 generation files, 22 judgment files | haiku-5-5 174 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/q8screen |
| 10-20 | MAIN (v0.1 + cooking/money SE); self-tests; v0.1 | quotefirst (CV5 audit backfill) | generate + judge | 1 generation files, 3 judgment files | haiku-5-5 48 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/quotefirst |
| 10-20..10-21 | MAIN (v0.1 + cooking/money SE); self-tests; selftest+selftest-cm+v0.1; v0.1 | qwen35-2b (CV5 audit backfill) | generate + judge | 7 generation files, 48 judgment files | haiku-5-5 384 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/qwen35-2b |
| 10-20..10-21 | self-tests; selftest+selftest-cm+v0.1; v0.1 | refuse-unsupported (CV5 audit backfill) | generate + judge | 1 generation files, 5 judgment files | opus-5-5 76 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/refuse-unsupported |
| 10-20 | MAIN (v0.1 + cooking/money SE); self-tests | retfloor (CV5 audit backfill) | generate | 80 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/retfloor |
| 10-20 | self-tests; selftest+selftest-cm+v0.1; v0.1 | retv1orc (CV5 audit backfill) | generate + judge | 1 generation files, 6 judgment files | haiku-5-5 26 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/retv1orc |
| 10-20 | MAIN (v0.1 + cooking/money SE); self-tests; v0.1 | shortctx (CV5 audit backfill) | generate + judge | 1 generation files, 3 judgment files | haiku-5-5 44 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/shortctx |
| 10-20 | self-tests; selftest+selftest-cm+v0.1; v0.1 | shortctx2 (CV5 audit backfill) | generate + judge | 1 generation files, 7 judgment files | haiku-5-5 52 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/shortctx2 |
| 10-20 | MAIN (v0.1 + cooking/money SE); self-tests; v0.1 | vendorsamp (CV5 audit backfill) | generate + judge | 1 generation files, 3 judgment files | haiku-5-5 30 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/vendorsamp |
| 10-21 | MAIN (v0.1 + cooking/money SE); other:probe-co-alarm+other:saf+v0.1; other:saf+other:warmup+v0.1; v0.1 | aunion-pixel (CV5 audit backfill) | generate + judge | 6 generation files, 2 judgment files | haiku-5-5 38 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/aunion-pixel |
| 10-21 | v0.1 | chunkclean (CV5 audit backfill) | generate + judge | 2 generation files, 2 judgment files | haiku-5-5 102 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/chunkclean |
| 10-21 | self-tests; selftest+selftest-cm+v0.1; v0.1 | citesup (CV5 audit backfill) | generate + judge | 4 generation files, 30 judgment files | haiku-5-5 182 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/citesup |
| 10-21 | other:saf+other:warmup+v0.1; v0.1 | device-pixel8a/final-cut7-v01 (CV5 audit backfill) | generate + judge | 2 generation files, 1 judgment files | haiku-5-5 114 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; device-pixel8a/final-cut7-v01 |
| 10-21 | other:saf+other:warmup+v0.1; v0.1 | device-pixel8a/gemma73-a (CV5 audit backfill) | generate + judge | 2 generation files, 1 judgment files | haiku-5-5 114 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; device-pixel8a/gemma73-a |
| 10-21 | v0.1 | dilution-k (CV5 audit backfill) | generate + judge | 3 generation files, 2 judgment files | haiku-5-5 100 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/dilution-k |
| 10-21 | longsession | drift17 (CV5 audit backfill) | generate + judge | 2 generation files, 1 judgment files | haiku-5-5 160 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/drift17 |
| 10-21 | self-tests; v0.1 | floor-anchors (CV5 audit backfill) | generate + judge | 4 generation files, 24 judgment files | haiku-5-5 1110 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/floor-anchors |
| 10-21 | self-tests; selftest+selftest-cm+v0.1; selftest+v0.1; v0.1 | fotapol-lora (CV5 audit backfill) | generate + judge | 4 generation files, 22 judgment files | haiku-5-5 180 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/fotapol-lora |
| 10-21 | MAIN (v0.1 + cooking/money SE); self-tests; v0.1 | g41e (CV5 audit backfill) | generate + judge | 1 generation files, 2 judgment files | haiku-5-5 10 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/g41e |
| 10-21 | MAIN (v0.1 + cooking/money SE) | g41g (CV5 audit backfill) | generate | 1 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/g41g |
| 10-21 | other:epi+other:h+other:m+other:n+other:nm+v0.1 | gemma-safety (CV5 audit backfill) | generate | 2 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/gemma-safety |
| 10-21 | MAIN (v0.1 + cooking/money SE); self-tests; v0.1 | gemma4-e2b-confirm (CV5 audit backfill) | generate + judge | 3 generation files, 9 judgment files | haiku-5-5 440 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/gemma4-e2b-confirm |
| 10-21 | MAIN (v0.1 + cooking/money SE); self-tests; selftest+selftest-cm+v0.1; v0.1 | granite4-1b (CV5 audit backfill) | generate + judge | 5 generation files, 47 judgment files | haiku-5-5 514 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/granite4-1b |
| 10-21 | MAIN (v0.1 + cooking/money SE); self-tests; selftest+selftest-cm+v0.1; v0.1 | jan-v1-edge (CV5 audit backfill) | generate + judge | 7 generation files, 50 judgment files | haiku-5-5 394 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/jan-v1-edge |
| 10-21 | v0.1 | oracle-real (CV5 audit backfill) | generate + judge | 1 generation files, 2 judgment files | haiku-5-5 98 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/oracle-real |
| 10-21 | v0.1 | ruler/codex-ladder (CV5 audit backfill) | generate | 4 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; ruler/codex-ladder |
| 10-21 | v0.1 | ruler/cv5-ladder (CV5 audit backfill) | judge | 0 generation files, 4 judgment files | opus-5-5 324 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; ruler/cv5-ladder |
| 10-21 | self-tests; v0.1 | ruler/warn-opus (CV5 audit backfill) | judge | 0 generation files, 27 judgment files | opus-5-5 216 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; ruler/warn-opus |
| 10-21 | MAIN (v0.1 + cooking/money SE) | smol3e (CV5 audit backfill) | generate | 1 generation files, 0 judgment files | none | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/smol3e |
| 10-21 | MAIN (v0.1 + cooking/money SE); self-tests; selftest+selftest-cm+v0.1; v0.1 | smollm3-3b (CV5 audit backfill) | generate + judge | 5 generation files, 46 judgment files | haiku-5-5 374 rows | script/agent outputs outside blind/; ids+counts in this audit | dev (unchanged) | ruler/CV5-EXPOSURE-AUDIT-2026-10-21.md; arms/smollm3-3b |

## Reproduce
`python3 rnd/research/coordinator/ruler/tools/exposure_audit.py --json CV5-EXPOSURE-AUDIT-2026-10-21.json --table t.md --proposed p.md`
