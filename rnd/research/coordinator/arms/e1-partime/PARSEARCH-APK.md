# PARSEARCH-APK: BOAR Bench build with Promise.all pack search (2026-10-21)

TL;DR: APK exists, retrieval is identical to the serial engine on the 72 A-union questions (0 diffs). E1-PAR run 3 (arm B) is runnable.

## Patch
- Function: `searchWikiPacks` in src/rag/packs.ts (bench-app/engine tree 0ca54d87 = cut7-cmp30off-batchret).
- Change: the serial `for await` over `knowledgePacks()` becomes `Promise.all(packs.map(...))`; each pack keeps its own try/catch
  and returns null on failure/missing; `.filter(non-null)` keeps catalog order, so the caller's merge and tie-breaks see the same list.
- `openPack` is safe to run concurrently (per-pack `opening` map, per-pack connection).
- Files (tools/): `promise-all.patch` (delta on the batchret tree, sha 3d91aa73...), `cut7-cmp30off-batchret-parsearch.vs-0cfd4a77.patch`
  (batchret patch + delta, sha 707cebf2..., used by `scripts/engine.sh 0cfd4a77 --patch ... --arm cut7-cmp30off-batchret-parsearch`).
  boar-app/ untouched; the patch is applied only in bench-app/engine (generated, gitignored).
- Engine tree hash 8ad2c4b0fae9c8a4... (engine.lock.json NOT changed: it still names the batchret tree for the other APKs).

## APK
- `bench-app/build/boar-bench-0cfd4a77-cut7-cmp30off-batchret-parsearch-nonet-8ad2c4b0fae9.apk` (89.7 MB, no INTERNET permission)
- sha256 `fc1c855a2d4dd21c79e1c0c3f72ff615e7c4417336163d3af9119ea194c10340` (also in the .sha256 file)
- Built like the gemma2 APK: incremental `gradlew :app:assembleRelease -PreactNativeArchitectures=arm64-v8a -PrnllamaVariants=rnllama,rnllama_v8_2_dotprod,rnllama_v8_2_dotprod_i8mm`
  with JDK17 and BENCH_NONET=1 on the existing nonet android/ (full build-android.sh skipped: 12 GB free < 15 GB floor). JS bundle is 768 B larger than gemma2's.
  Same native libs / llama.rn as gemma2 (no version change). Models are chosen per request, so Qwen3-1.7B (catalog id qwen3-1.7b-q4km) is the default of the e1par requests.

## Parity (desktop, 0 LLM)
- replay-retrieval.sh, gate=rules, 6 A-union packs, 72 questions of aunion73-a (58 retrieve, same as the phone), unpatched vs patched tree.
- Result: `query`, `k`, `task`, ordered `raw` titles/sections/sources and `sources` identical on 72/72; 41 items have pack-sourced hits. 0 diffs (kill rule not triggered).
- Engine tests src/rag: 181 passed, 64 skipped, 7 files fail in BOTH trees (scratch tree lacks scripts/build-*.mjs); no new failure. Not verified: phone timing (that is the step).

## Run E1-PAR run 3 (arm B)
1. `adb install -r` the APK (BOAR Bench package keeps data; same package id as the other bench APKs; packs/model already on the phone from arms A/C).
2. Cool phone, `python3 $G/thermal_gate.py e1par-b 310`, then `python3 boar_bench.py run e1par-b` (request handoff/pixel8-2026-10-20/bench/requests/e1par-b.request.json).
3. Kill rules unchanged (DEVICE-DAY step E1-PAR): retrievedTitles differ from A -> B void. Reinstall the previous APK for A2 (drift control).
