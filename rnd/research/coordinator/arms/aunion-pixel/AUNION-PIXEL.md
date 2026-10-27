# AUNION-PIXEL: persona A-union packs on the Pixel 8a with Qwen3-1.7B (2026-10-21 03:3x-03:51)

Criterion frozen before the run: AUNION-PIXEL-criterion.md (sha bc5bc517..., commit a852f6bd). 0 judge calls, 0 paid. Pixel 8a, airplane mode, Wi-Fi/BT off, BOAR Bench in front, AC power, thermal gate before each run (status 0; battery 30.0 C at both gates). APK and engine are the same as gemma10-b / q17b10-a / q17b73-a (tree 0ca54d87 found in bench.json; the boar_bench.py "tree hash not found" warning is its stale cut-6 list).

Kit: bench-app/kits/persona-a-union.kit.txt, 7 files sha-verified on the device (crypto and wikivoyage already present with the same shas; visa, medlineplus, firstaid, factbook in files/corpus, world-places.sqlite in files/poi). The kit stays installed on the phone: later 1.7B/4B runs on this phone now search 6 packs plus the gazetteer, not the claim kit. Push note: scripts/push-kit.sh re-reads the sha right after the stream and reported a mismatch on each new file the first time; a re-read a few seconds later matched, so this is a flush race in the script, not corruption (all 7 shas match now).

How the engine uses the packs (bench-app/engine/src/rag/packs.ts, retrieve.ts): every *.sqlite in files/corpus is a pack (no catalog or manifest needed; checked only for format + embedding sha). Each question searches all installed format-2 packs one after another with k = topK, merges by fusion and cuts to topK. There is no per-pack quota and no pack selection per request, so the LITEPACKS K-sets have no phone equivalent: on the phone it is all installed packs, the same topK. Codes 10/11 fall back to the enwiki label (SOURCES[code] ?? enwiki); their keyword hits are retrieved.

| run | packs | rows | answer p50 / p90 | total | TTFT p50 | LLM calls | promptN p50 / max | prefill / decode tok/s | retrieval p50 / p90 / max | PSS peak | battery | thermal max | LMK |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| q17b10-a (baseline) | claim kit (2) | 10/10 | 8.3 / 10.0 s | 67 s | 4.9 s | 7 | 274 / 487 | 81.8 / 13.9 | 1.47 / 1.90 / 3.15 s | 3.25 GB | 31.6-32.7 C | 0 | 0 |
| aunion10-a | A-union (6 + gazetteer) | 10/10 | 9.4 / 12.2 s | 83 s | 6.6 s | 7 | 218 / 487 | 86.1 / 16.1 | 3.90 / 5.01 / 6.54 s | 3.32 GB | 29.6-30.0 C | 0 | 0 |
| q17b73-a (baseline) | claim kit (2) | 73/73 | 4.2 / 12.1 s | 400 s | 2.9 s | 34 | 276 / 561 | 80.2 / 12.4 | 1.63 / 3.14 / 5.04 s | 3.39 GB | 26.2-34.1 C | 0 | 0 |
| aunion73-a | A-union (6 + gazetteer) | 73/73 | 7.6 / 15.0 s | 544 s | 5.3 s | 34 | 250 / 561 | 69.5 / 11.3 | 3.99 / 5.91 / 10.71 s | 3.41 GB | 30.1-33.6 C | 0 | 0 |

Verdict by the frozen rule (smoke vs q17b10-a): answer p50 +1.1 s (<= +3), TTFT +1.7 s (<= +2), PSS 3.32 GB (<= 4.0), 0 LMK -> **PASS**. On the 73 (same thresholds vs q17b73-a, reported) the deltas sit in the MARGINAL band: answer p50 +3.4 s (p90 +2.9 s), TTFT +2.4 s, PSS 3.41 GB, 0 LMK; no kill clause fires (PSS < 4.4 GB, answer p50 < +5 s). Total wall for the 73: +36 %.

Where the time goes: memory is flat (+0.02 to +0.07 GB PSS); the cost is retrieval, +2.4 s p50 on both sets (1.5-1.6 s -> 3.9-4.0 s), max 10.7 s. SQL time by pack over the 73: wikivoyage 18.0 s, crypto 16.5, firstaid 12.6, factbook 12.1, medlineplus 11.0, visa 10.7: each small pack costs ~0.15 s per question regardless of size, because the packs are searched one after another. Model speed is unchanged within noise (prompt tokens do not grow: the topK cut holds the context).

Pack hits (retrievedTitles mapped to pack titles; a title present in several packs counts for each, so the baseline shows 3 firstaid collisions): 73-run wikivoyage 26 questions, crypto 10, firstaid 7, factbook 2, visa 0, medlineplus 0; smoke factbook 1, firstaid 1. **Flag: medlineplus never appears in retrievedTitles in either run** (and visa neither) -> native PackSource enum gap note stays open for the app maintainer; on this set the two health/visa packs are inert, which is a set-coverage reading, not proof they are unreachable.

Reading: A-union fits the 8 GB product in memory with a wide margin and no kill; it costs about +2.4 s per researched answer, all in sequential pack search. Cheapest lever if needed: search the packs in parallel (Promise.all in searchWikiPacks) or merge the four small packs into one file. Not judged here (answers unscored).

Files: aunion10-a/, aunion73-a/ (rows.jsonl, bench.json, telemetry.csv, device.json, kit.txt, status, meminfo, aunion-summary.json; no logcat), thermal.jsonl, requests aunion{10,73}-a.request.json, summarize_aunion.py.

## gemmaa73-a: Gemma 4 E2B on the 73 with A-union installed (03:53-04:10)
Addendum frozen first: GEMMA-AUNION-addendum.md (commit ed25e122). Thermal gate status 0, battery 32.8 C. Same APK (gemma2; 0 thinking markers in 73 rows), tree 0ca54d87 in bench.json. LLM calls counted by summarize_aunion.py (llm-completion spans) for both runs, so 42 here vs the 55 quoted above for gemma73-a is a counting difference, not a run difference.

| run | packs | rows | answer p50 / p90 | total | TTFT p50 | LLM calls | promptN p50 / max | prefill / decode tok/s | retrieval p50 / p90 / max | PSS peak | battery | thermal max | LMK |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gemma73-a (baseline) | claim kit (2) | 73/73 | 11.8 / 23.5 s | 779 s | 5.5 s | 42 | 236 / 550 | 34.1 / 7.0 | 1.96 / 3.68 / 6.41 s | 4.52 GB | 33.0-36.4 C | 1 | 0 |
| gemmaa73-a | A-union (6 + gazetteer) | 73/73 | 13.3 / 23.3 s | 873 s | 8.4 s | 42 | 219 / 550 | 35.6 / 7.2 | 4.41 / 6.99 / 10.52 s | 4.38 GB | 32.2-34.3 C | 0 | 0 |

Verdict (addendum rule): PSS peak 4.38 GB < 5.0 GB and 0 LMK kills -> **PASS**. PSS never crossed 4.8 GB (peak at load, +26 s); it is 0.14 GB below the claim-kit run, i.e. within sample noise, so the packs add no measurable memory to Gemma either. Speed: answer p50 +1.5 s, p90 flat, TTFT +2.9 s, total +12 %; retrieval +2.4 s p50, the same sequential pack-search cost as with the 1.7B; model prefill/decode unchanged (the baseline ran warmer and reached thermal 1, so if anything the A-union speed deltas are slightly understated). Pack hits identical in shape to the 1.7B run (same retrieval): wikivoyage 26, crypto 10, firstaid 7, factbook 2, visa 0, medlineplus 0.

## q4ba73-a: Qwen3-4B (the RC's 8 GB default) on the 73 with A-union installed (04:11-04:35)
Addendum frozen first: Q4B-AUNION-addendum.md (commit 0e20b925). Thermal gate status 0, battery 32.6 C (right after the Gemma run). APK gemma2 build, tree 0ca54d87 in bench.json. The app was never killed (watcher checked the process every 15 s); 73/73 in one pass.

| run | engine | packs | rows | answer p50 / p90 (all rows) | generating rows p50 | TTFT p50 all / generating | promptN p50 / max | prefill / decode tok/s | retrieval p50 | PSS peak / after-load p50 / after-first | battery | thermal max | LMK |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| final-cut7-v01 (10-20 baseline) | cut 7 (7c96e59e) | claim kit (2) | 73/73 | 25.4 / 51.7 s | 37.0 s | 14.0 / 20.8 s | 241 (evaluated) | 18.0 / 4.2 | n/a (no timeline in cut 7) | 4.92 / 4.05 / 4.94 GB | 33.4-38.0 C | 1 | 0 in the kept run (1 kill in attempt 1, ~4.4 GB) |
| q4ba73-a | cut7-cmp30off-batchret (0ca54d87) | A-union (6 + gazetteer) | 73/73 | 19.4 / 38.6 s | 27.3 s | 9.2 / 13.6 s | 230 / 563 | 26.7 / 5.2 | 4.25 s (p90 6.16, max 11.1) | 4.76 / 3.79 / 4.48 GB | 31.2-32.6 C | 0 | 0 |

Verdict (addendum rule): 0 LMK kills and PSS peak 4.76 GB < 5.2 GB -> **PASS**. Memory with the A-union is not higher than the claim-kit baseline (peak -0.16 GB, after-load -0.26 GB); the 6 packs + gazetteer add no measurable PSS to the 4B either. Caveats: one run, PSS sampled every 5 s; the 10-20 kill came from load-time peaks (~4.4-4.9 GB) and this run's load peak 4.76 GB is in that range, so the margin to an LMK kill on 8 GB is about the same as on 10-20, not wider; the risk is the 4B itself, not the packs. Speed is not a fair A/B here: the baseline ran on the cut 7 APK hot (38 C, thermal 1) while this run stayed cool (status 0) on the batchret engine; the 4B was faster in this run (answer p50 19.4 vs 25.4 s, prefill 26.7 vs 18.0, decode 5.2 vs 4.2 tok/s) despite +2.4-ish s of pack search (retrieval p50 4.25 s vs 1.6-2.0 s on the 1.7B/Gemma claim-kit runs). Pack hits identical to the 1.7B and Gemma runs: wikivoyage 26, crypto 10, firstaid 7, factbook 2, visa 0, medlineplus 0.

## PK-5 MERGED-PACK: step 1 identity FAILED the 95 pct gate -> stopped before the phone (04:3x-04:5x)
Criterion PK5-criterion.md (commit 59a909f0) frozen before the build. 0 LLM, 0 judge. The phone was not touched (still the A-union state: 6 packs + gazetteer).
- Build (mini, tools/merge-packs.mjs, 13 s): boar-aunion-merged.sqlite, 417,857,536 B, sha 7e86674b59b5cfa687208cffb2eba505a67ec0165d8966e273dc7703c7ee6eb7 (40,649 articles, 649,964 chunks, 648,597 indexed = the sum of the six). Copies: mini <runner>/kiln/pk5/, MacBook shared-data/packs/persona-a-union-merged/. Re-index fidelity: a one-pack merge reproduces the source fts5vocab instance table exactly (factbook, crypto, visa).
- Replay (MacBook, replay-retrieval.sh, tree bench-app/engine = 0ca54d87, --gate rules --compress, 97 items = MAIN 97, which contains the v0.1 57): six-pack rerun is deterministic (97/97 identical). Six vs merged: **kept sources identical on 81/97 = 83.5 pct (gate >= 95 pct: FAIL)**; raw lists identical 56/97. The 16 differing items (15 of them in the v0.1 57) are listed in pk5/compare.txt.
- Direction of the differences (not a quality verdict): distinct kept titles lost 8, gained 11; 2 items go from no kept source to some (lan-hlt-002 gains MedlinePlus "Exercise for Older Adults" + "Myocardial infarction", lan-exp-003 gains factbook "Kenya"), 0 go to none; dng-002 gains "Hypothermia"; vit-cry-006 drops "Quadratic sieve" (an off-topic keep); vit-sci-002 swaps "Pacific War" for "Japan"; dng-005 swaps "Stay healthy" for a Ready.gov flood page. Replay gold recall@5 on the 39 gold items 0.231 (six) -> 0.269 (merged). This is the global-idf + single-candidate-list effect the hypothesis named as the main risk; it reorders rather than loses on this set, and it is the first configuration in which medlineplus reaches a kept context.
- Speed (MacBook only): retrieve() p50 226 ms (six) -> 80 ms (merged), -65 pct, on the CPU that took 1.5 s -> 3.9 s on the phone. Phone saving unmeasured.
Reading: the merge is not an identity transform, so under the frozen rule it does not go to the phone. Whether the changed contexts are equal or better needs a judged parity screen (or the hypothesis's own 90 pct kept-title parity + RAG-FUNNEL S4+S5 rule); that is the coordinator's call. Resume steps for the phone step: PLAN.md.

### PK-5 judged parity screen (addendum 1, a0e7b351 + r1 655ddc5e): FAIL -> stopped, phone untouched (04:47-04:52)
Both arms fresh on the mini in the phone's retrieval configuration (settings quickFirst only, no head pass / dense append; S = 6 A-union phone files, M = merged file), 1.7B, seed 42, the 16 changed items; Haiku 5.5-low N=4 both orders, byte-identical answers reuse existing judgments. Calls 38 / cap 70 (S 8: 12 reused; M 30: 1 reused). Why fresh S and not the existing KA cell: KA ran HEADPASS-X2b, which skips packs by id, so merged vs KA would mix in a head-pass change (addendum 1).

| arm | U (16) | CE-unwarned | CE | warned | declines |
|---|---|---|---|---|---|
| S (6 packs) | 0.399 | 2 | 5 | 8 | 0 |
| M (merged) | 0.365 | 1 | 2 | 6 | 0 |
| (existing KA cell, LITEPACKS settings, reported only) | 0.398 | 3 | | | |

Rule: U(M) - U(S) = **-0.034 < -0.02 -> FAIL** (CEu -1 passes). Per item: 7 down, 6 up, 3 flat; the big losses are lan-exp-005 (-1.17, the merged keep dropped Wikivoyage "Sahara" and the answer turned into a warned memory answer), dng-002 (-1.17, merged added Wikipedia "Hypothermia" ahead of the ATP hypothermia chapter) and vit-cry-008 (-1.00); gains on vit-cry-003/006 (+0.50, the merged keep replaced an off-topic EIP / "Quadratic sieve"). n = 16, one seed: the pooled delta is about one item's swing, so this is a stop by the frozen rule, not evidence that merging hurts in general. The phone step did not run; the phone stays in the A-union state; the merged file stays on the mini (kiln/pk5/packs-merged) and the MacBook.
Implication for the app maintainer note: the +2.4 s serial-search cost is better attacked without changing ranking (search the packs in parallel, Promise.all in searchWikiPacks; identical results by construction) than by merging (one global idf + one candidate list changes what is kept).
