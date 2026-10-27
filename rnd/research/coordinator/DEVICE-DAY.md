# Device day: BOAR Bench, cut 3, first 12 GB phone session

TL;DR: install the cut 3 APK, push one 3.0 GB kit, run a 10-item acceptance vs desktop answerEval, record stage latencies and PSS. No tuning, no blind sets. Sources: `rnd/research/forge/BENCH-APP.md`, `rnd/research/forge/PHONE-SESSION.md` (S0 / meminfo-poll / mark.sh), `bench-app/README.md`.

## Artifacts (built 2026-10-04, MacBook, no device touched)
| What | Value |
|---|---|
| APK | `bench-app/build/boar-bench-0cfd4a77-cut3-53338dffc493.apk`, 77,086,168 B (74 MB), sha256 `a02b55e6afa42b1e4d3bde98690832185ad4a4018110eeb2e615300262cdad84` |
| Package | `team.sopa.boarbench`, release JS (Hermes), debuggable (verified with aapt2), arm64-v8a only, 3 llama.rn variants (base, dotprod, dotprod+i8mm) |
| Engine | base `0cfd4a77`, arm `cut3`, patch sha `a67c70dbd194...0efc2a`, treeHash `53338dffc4936daee06864893ee0ef65c1234b1e23e740e93f43369b2d6ce671` |
| Identity check | a desktop-node tree of the same spec (git archive + patch, setup.sh recipe, built locally) hashes to the same value |
| Kit file | `bench-app/kits/cut3-en-12gb.kit.txt` (the old `qwen3-4b-en.kit.txt` lacks the detector files: do not use it) |
| Desktop dry run | 8/8 rows, EvalTrace valid 8/8; detector parity Compass dev 300: 300/300 agree, canary ok (cos 1) |

UNKNOWN: the app has not run on a phone. `-PrnllamaVariants` names built fine; the i8mm lib is present.

## 0. Before the phone (5 min)
- [ ] `shasum -a 256 bench-app/build/*.apk` equals the value above; `cat bench-app/engine.lock.json` treeHash equals the table.
- [ ] `adb devices` shows the phone; USB debugging on; phone free space >= 6 GB (kit 3.0 GB + APK + margin); battery >= 50%, USB plugged (same condition for every run).
- [ ] `adb shell getprop ro.product.model; adb shell grep MemTotal /proc/meminfo` into the session notes (the 12 GB claim must be checked, not assumed).
- [ ] Set `D=<out dir>`; `bash rnd/research/forge/arms/session/mark.sh $D S-start` (battery, temp, time), as in PHONE-SESSION S0.

## 1. Install
```fish
cd <workspace>/bench-app
adb install -r build/boar-bench-0cfd4a77-cut3-53338dffc493.apk
adb shell dumpsys package team.sopa.boarbench | grep -E "versionName|DEBUGGABLE"
```
Expected: versionName 0.1.0, DEBUGGABLE flag set (run-as needs it).

## 2. Kit push (offline, sha-checked per file)
`scripts/push-kit.sh kits/cut3-en-12gb.kit.txt` (about 10-15 min over USB)

| File on device (`files/`) | Size (B) | Why |
|---|---|---|
| `models/qwen3-4b-instruct-2507-q4km.gguf` | 2,497,281,120 | 4B reader (12 GB tier default) |
| `models/embedding.gguf` (bge-small q8) | 36,806,944 | retrieval embeddings |
| `models/emergency-detector.gguf` (v3b, sha a86fe8b9...) | 106,210,784 | learned detector, frozen |
| `models/emergency-detector.head.json` (sha 766434de...) | 1,696,707 | detector head |
| `models/emergency-detector.canary.json` | 8,959 | load-time canary |
| `corpus/boar-wikivoyage-en.sqlite` | 351,092,736 | EN travel pack |
| `corpus/boar-crypto.sqlite` | 36,093,952 | crypto pack |
| Total | about 3.03 GB | |

- [ ] Every line prints a check mark (`✓` or `= already`); the final `ls -l` lists all 7 files.
- Not in the kit by design: big Wikipedia packs (closed lever), deep tier 35B (paused), other models, PT/ES.
- UNKNOWN: POI/places packs (`corpus/poi`): the ship kit (kit A) used `--places kit-vexact` on desktop. Check what kit A holds and whether a `poi/` file belongs here before the acceptance run; the dry run used none.

## 3. Cold start and canary check
```fish
adb shell am force-stop team.sopa.boarbench; adb logcat -c
adb shell am start -n team.sopa.boarbench/.MainActivity
adb logcat -d -s ReactNativeJS:V | grep -i -E "engine .*ready|embedding|detector|canary|error" | head
```
- [ ] Status screen shows the engine tree `53338dffc493` (first 12 chars of the hash) and polling.
- [ ] Detector loads and the canary passes (desktop: ready in ~0.8 s, cos 1.0). A canary failure is a stop: report it, do not continue.
- [ ] Record the cold start wall time (am start to first "ready" log line).

## 4. 10-item acceptance run vs desktop answerEval
Request: `requests/cut3-final.request.json` (the 8 EN sanity items: vit-hum-004, vit-trv-004, probe-co-001, probe-co-002, probe-co-alarm, dng-001, vit-cry-001, lan-exp-005). Add 2 more items for 10: take them from the v0.1 EN set (dev set only, never `blind/`), one retrieval-heavy (travel) and one chat/small-talk item, and build the request with the same `answerSettings`. Put the cold/warm-up item first (BENCH README: the gate needs the model resident).
```fish
scripts/bench-run.sh requests/cut3-final.request.json 1 --tag cut3-acc --out $D
```
Compare each row with the desktop reference (same engine tree, same request ids), field by field, not by text equality:
| Check | Pass |
|---|---|
| 10/10 `outcome: success`, 0 errors | required |
| `route` and `tier` per item | equal to desktop (expected: vit-trv-004, probe-co-002, dng-001 `instant`; the CO items and detector hits take the card path) |
| sources / retrieved titles | same set as desktop (retrieval is deterministic) |
| card items (CO, snakebite) | text byte-identical to desktop |
| free-form answers (vit-hum-004, vit-cry-001, lan-exp-005) | different wording expected (sampler/threads differ: llama.rn vs node-llama-cpp); read for content: no empty answer, no crash, no wrong-language |
| engine identity | `<rid>.bench.json` treeHash = `53338dff...` |

Desktop reference: dry run rows `bench-app/dry-run/appdir/eval/dry-cut3-final.answer.jsonl` (8 items, llama-server) and the mini traces `boar-eval/runs/kiln/cut3-confirm/` (cut3-v01-s44 / s45: the full cut 3 desktop run, 4B). Score with `convert_device.py` as the script does; do not run the judge on device rows on this day (work budget).

## 5. Latency stages to record (per item, from rows + telemetry)
- From each row's `receipt`: `ttftMs`, `total` time, `retrievalMs`, and `retrievalStages` (`sqlMs`, `sqlCalls`, `zstdMs`, `utf8Ms`, `corpusSqlMs`); the gate line (`[gate] ... gateMs`) and detector ms from logcat. Table: `python3 rnd/research/forge/arms/stages_report.py $D/<rid>` (add `--ref` for a second run).
- Wall clock: cold start (section 3), first-question cold path (model load + gate load), then warm items. Report p50 and max for warm items separately from the cold first item.
- Decode and prefill speed: tokens/s from the rows where present; the desktop reference is ~21 tok/s on the mini (M4), so a ratio is only indicative.
- Context for the numbers: `device.json` (SoC, cores, max freqs), `telemetry.csv` (battery, thermal status). If thermal status rises above 0, say so next to the latency figures.

## 6. Memory check (4B path)
- The host sampler already logs the app's total PSS every 5 s into `telemetry.csv`. For the peak and a per-process breakdown run in parallel (as in PHONE-SESSION):
  ```fish
  bash rnd/research/forge/arms/session/meminfo-poll.sh $D/cut3-acc.mem.csv 480 &
  ```
- [ ] Take `adb shell dumpsys meminfo team.sopa.boarbench` once after the model is loaded (idle) and once at the end of the run; record TOTAL PSS, Native Heap, Code (mmap of the GGUF) and `Graphics` if any.
- [ ] Check `adb logcat -d | grep -i -E "lowmemorykiller|lmkd|am_kill"` is empty for the package (0 LMK kills).
- Compare with: Probe A on the mini (no-repack: anon ~0.9 GB, max RSS 3.41 GB; with repack: anon 3.25 GB, RSS 5.1-5.4 GB), and the Probe B frozen bar (peak total RSS <= 3.5 GiB, 0 LMK kills). NOTE: the cut 3 engine does NOT carry the Probe B `no_extra_bufts` line (grep found none in `engine/src`), so this build runs the default repack path. A PSS above 3.5 GiB is expected and is not a failure of the engine; record it as the repack baseline. Probe B (the 1-line patch) stays a separate decision, and would need the same patch on desktop and device trees to keep identity.
- UNKNOWN: whether the 12 GB phone's `memoryFit` verdict for the 4B is `ok` or `repack-peak`: grep the logcat for the memory-fit line and note it.

## 7. What to compare against (summary)
| Question | Reference |
|---|---|
| Does the phone run the same engine as the desktop result? | treeHash `53338dff...` in `bench.json` = `engine.lock.json` |
| Same routes, sources, card texts? | dry run rows (8) and `runs/kiln/cut3-confirm/` desktop traces |
| Quality | not judged on device day; desktop v0.1 EN cut 3 numbers are in `coordinator/cut3-confirm.md` |
| Speed and memory | PHONE-SESSION figures for the 8 GB moto g75 (D/R builds) and Probe A/B for memory |
| Detector | canary pass + desktop parity 300/300 |

## 8. Wrap-up
- [ ] `bash rnd/research/forge/arms/session/mark.sh $D S-end`; copy `$D` into `boar-eval/runs/` under a `device-day-cut3` name; append a 5-line result to `rnd/research/QUEUE.md`.
- [ ] Leave the app installed with its kit; delete nothing on the phone without the owner's OK.
- Stop conditions: canary fail, any LMK kill, treeHash mismatch, free space < 2 GB on the phone, battery temp > 42 C (pause and log).

## 9. Cut 4 retest (final cut 4 APK, built 2026-10-05, MacBook, nothing installed)
TL;DR: cut 4 = cut 3 + KVFIX + INSTANT-FRAG + INSTANT-SUBJ. Install it over cut 3 (`adb install -r`), push the same kit (`kits/cut3-en-12gb.kit.txt`, unchanged), repeat the cut 3 smoke and check the six items below. No tuning, no blind sets.

| What | Value |
|---|---|
| APK | `bench-app/build/boar-bench-0cfd4a77-cut4-6a61670e3ba6.apk`, 77,091,288 B, sha256 `22e22f2cdb02bcc93946e9f497ccac2ef20522db3571088e298bee52b8405787` |
| Engine | base `0cfd4a77`, arm `cut4`, patch `coordinator/arms/instsubj/instsubj-on-cut4.vs-0cfd4a77.patch` sha `d51e844c6522cb1825e43d800626516af099ae462c85e39396f7e2a4ea04dfa3`, treeHash `6a61670e3ba63088f6d4636031b80f20ed91340676d6a13b48304c58dda2dabe` (status screen shows `6a61670e3ba6`) |
| Identity | an independent `git archive` + `git apply` tree hashes to the same value |
| Superseded | `boar-bench-0cfd4a77-cut4-d631a9defc26.apk` (cut 3 + KVFIX + INSTANT-FRAG only): do not install |
| Desktop sanity | 9 rows (France warm-up + the 8 EN items), 9/9 success, EvalTrace valid 9/9; detector canary ok (cos 1), parity 300/300 |

What the tester checks on the phone (logcat `ReactNativeJS`, rows, `adb shell run-as team.sopa.boarbench ls -R cache/kv`):
- [ ] **`[gate] session save failed` is absent** from the whole run (it appeared on the A15 cut 3 smoke). `cache/kv/` holds flat files (one for the gate prefix, one for the answer prefix). If it still fails, copy the native error text into the notes (KVFIX UNKNOWN: a second cause, e.g. empty-token state).
- [ ] **`loadGateMs` is set (not `-`) from question 2 onward** in the `[gate] ... loadGateMs=... gateMs=...` lines. Question 1 may still show `-` (nothing to load yet).
- [ ] **`[gate] answer prefix restored in N ms` appears** (after the first answer prefix was saved; also expect it after a force-stop and restart). Record N.
- [ ] **TTFT p50 vs the A15 cut 3 smoke (72-100 s)**: compute p50 and max of `ttftMs` over the warm items (not the cold first item) with `stages_report.py`; report the ratio. UNKNOWN: the expected gain; the KVFIX unit tests only prove the save/load path.
- [ ] **France warm-up answer**: send "What is the capital of France?" first (cold). It must not finish `instant` (tier `fast`, model path) and must not be the Lyon "gastronomic capital" line. Desktop reference: a model answer naming Paris. Also try "what is the capital of the usa" once as an observation (INSTANT-SUBJ should keep it from answering with a state capital); write down what came back.
- [ ] **The export is UTF-8 clean**: pull `<rid>.answer.jsonl`, then `file` and `python3 -c "open(f, encoding='utf-8').read()"` must pass; no mojibake in accented titles ("Gríma", "Wikivoyage" titles). Convert with `boar-eval/scorers/convert_device.py` (utf-8 fix, commit 5285766 in boar-eval).

Everything else (kit push, cold start, 10-item acceptance, memory, wrap-up) is sections 0-8, with these substitutions: APK name and sha above, treeHash `6a61670e...`, request `requests/cut4-final.request.json` (France warm-up first, then the same 8 items; add the 2 extra dev items as in section 4), tag `cut4-acc`, out dir name `device-day-cut4`. Expected routes: vit-trv-004, probe-co-002, dng-001 `instant`; the warm-up and the other items `fast`.

### 9a. Use the no-network APK, in airplane mode (supersedes the APK row above for the retest)
The retest should use `bench-app/build/boar-bench-0cfd4a77-cut4-nonet-6a61670e3ba6.apk` (sha256 `966ad34b548d111b386c6bb34f11707469a09dba4e03bfbf2ffaf2985c1cfc42`, 77,091,228 B). Same engine (base `0cfd4a77`, arm `cut4`, patch sha `d51e844c...`, treeHash `6a61670e...`); the only difference is the manifest: INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, CHANGE_*_STATE, NEARBY_WIFI_DEVICES and SYSTEM_ALERT_WINDOW are removed. It is still debuggable (adb `run-as` needs it), so `adb install -r`, kit push and result pull work as before.
- Turn **airplane mode on** before the first launch and keep it on for the whole run (Wi-Fi and Bluetooth off too).
- Record in the run notes, as two explicit lines: **"airplane mode on"** and **"network permission absent"** (check: `adb shell dumpsys package team.sopa.boarbench | grep -i "permission"` shows no `android.permission.INTERNET`).
- The 19 hosts the static audit lists are strings in the JS bundle and native libraries; without the permission they cannot open a socket.


## 10. Cut 5 retest (supersedes §9 APKs)
TL;DR: cut 5 = cut 4 + CUT5-LITE (route-gate skip for lookup/research/compare, no-source prefix cache, detector release, small fixes). Install cut 5 first, run the §9 checklist plus (a) and (b); then install cut5-speed over it and rerun the same 8 items for the retrieval A/B (c). Both APKs are no-network (BENCH_NONET=1, same rules as §9a: airplane mode on, write "airplane mode on" and "network permission absent" in the notes). Built 2026-10-06 on the MacBook, nothing installed. Same kit `kits/cut3-en-12gb.kit.txt` (unchanged), same request shape as §9 (`bench-app/requests/cut5-final.request.json`, tag `cut5-acc`; for B `cut5speed-final.request.json`, tag `cut5speed-acc`; out dirs `device-day-cut5`, `device-day-cut5speed`).

| | A: cut 5 | B: cut5-speed |
|---|---|---|
| APK (`bench-app/build/`) | `boar-bench-0cfd4a77-cut5-nonet-de5f5bae429a.apk`, 77,175,948 B (rebuilt 2026-10-06 after an overwrite; same treeHash) | `boar-bench-0cfd4a77-cut5speed-nonet-5a1f6a0a3002.apk`, 77,239,378 B |
| sha256 | `04d051dc3fb0d0ea45d088c33345356e71ef0f8654e913bcdce2a69442ccd961` (first build dc2d931f… is gone; never distributed) | `be9e9ce6e4ecc3d6a263efc0c63b3fe2d9bec1a56675cc12c2a7087b3337b598` |
| treeHash (status screen shows 12 chars) | `de5f5bae429a7b759e2b2d6103fc2228c0dcb66e52faa67b46057834b12e3cdc` | `5a1f6a0a300224f5f5fc5cb379efb1d0a34a72d819c4fae5ff886ab167d5b7b1` |
| Patch (`coordinator/arms/...`) sha256 | `cut5lite/cut5lite-on-cut4.vs-0cfd4a77.patch` `3b7a0dfa42bddee21c349a55f3d7ea3a5a1b98b58355c78b2768de75108d3e53` | `cut5speed/cut5speed-on-cut4.vs-0cfd4a77.patch` `cfbaf7071a0128b92c369ea7bd2bd6a8d63f56754c12203cb7beede85ebe1cf9` |
| Native | as cut 4 | adds `lib/arm64-v8a/libboarzstd.so` (73,592 B, compiled into the APK); kill switch `EXPO_PUBLIC_BOAR_PERF=none` is build-time only (not set) |

- Identity: for both, an independent `git archive 0cfd4a77` + `git apply` (+ reverse-apply check) tree hashes to the value above. Build reports: `bench-app/build/build-report-cut5.txt`, `build-report-cut5speed.txt`. Both manifests carry no INTERNET permission.
- Build note B: `npm ci` first failed because `package-lock.json` lacked `boar-zstd` (the engine adds a local module). Fixed the normal way (`gen-package.mjs`, `npm install --package-lock-only`; diff = only the boar-zstd link, committed in bench-app d886a1d). Consequence: the committed package.json now matches B; rebuilding A needs `node scripts/gen-package.mjs` first.
- Desktop sanity (9 rows = France warm-up + 8 EN items, `dry-run/cut5-final.log`, `cut5speed-final.log`; llama-server 4bc272f): A and B both 9/9 success, EvalTrace valid 9/9, 0 errors; detector canary ok (cos 1), parity 300/300 PASS (A; B shares the detector code). Routes: vit-trv-004, probe-co-002, dng-001 `instant`; the rest `fast`. `route-gate:skip-rules` on warm-up (lookup), vit-hum-004, vit-cry-001, lan-exp-005 (research); probe-co-001 and probe-co-alarm (chat) still show `route-gate:search` + score. Desktop `receipt.retrievalMs` p50 is 256 ms for both (the shim has no native zstd: `zstdModule:false`, so B shows no gain here). Not testable on desktop: `[engine] no-source prefix restored` (the shim no-ops sessions), the real zstd module.

Checks on the phone (§9 list stays; `[gate] session save failed` absent, `loadGateMs` from Q2, `[gate] answer prefix restored in N ms`, TTFT p50 vs the cut 3 smoke, France warm-up, UTF-8 export), plus:
- [ ] (a) **`route-gate:skip-rules`** in the rows' `reasonCodes` (and `[gate]`/answer logcat) for lookup/research/compare items: expect warm-up, vit-hum-004, vit-cry-001, lan-exp-005. The CO items (chat-like) must still show `route-gate:search` / `route-gate:score-*`, i.e. the gate still runs. Record `gateMs` and TTFT for skipped vs gated items.
- [ ] (b) **`[engine] no-source prefix restored in N ms`** (exact string in the patch, `console.warn`) in `adb logcat -d -s ReactNativeJS:V | grep "no-source prefix"` on no-source answers after the first; the first no-source answer should log the save, not a restore. Record N; also grep `no-source prefix failed` (must be absent).
- [ ] (c) **Retrieval A/B:** install B over A (`adb install -r`; the kit and files/ survive), rerun the same 8 items with the same warm-up. Per item take `receipt.retrievalMs` (and, on B only, `receipt.retrievalStages`: `zstdMs`, `sqlMs`, `corpusCacheHit`, `perf`, `zstdModule`). Report **retrievalMs p50 for A and B**, B/A ratio, items with B < A; use `rnd/research/forge/arms/stages_report.py` on B. On B confirm `zstdModule:true` and `zstdFallbacks:0` (else the native module did not load: report the logcat line, do not tune). Instant-tier items have no retrieval row: skip them. UNKNOWN: A rows carry no `retrievalStages` (only `retrievalMs`); on-device gain.
- Stop conditions as §8. Do not mix A and B rows in one out dir.


## 11. Device-rate sweep (A15), built 2026-10-06 on the MacBook, nothing installed
TL;DR: one install, 8 requests, each with a bench-only `engineOverrides` block (threads, KV type, flash attention) that reloads the model; engine answer logic is untouched (same cut 5 tree). Use it to pick `nThreads`/KV for the A15 (G99: 2x A76 + 6x A55) and to replace the unmeasured "device rate x1.25" in `device/A15-LATENCY-BUDGET.md`.
- **APK**: `bench-app/build/boar-bench-0cfd4a77-cut5-nonet-sweep-de5f5bae429a.apk`, 77,134,712 B, sha256 `cb76f3a0ba324eeec1a2bd53a04bca2b543b3b9677dea62a5b8ac058f1e3c74d` (report `build/build-report-cut5-sweep.txt`). Engine = cut 5: base `0cfd4a77`, patch `cut5lite-on-cut4...patch` sha `3b7a0dfa...`, treeHash `de5f5bae429a7b759e2b2d6103fc2228c0dcb66e52faa67b46057834b12e3cdc` (an independent `git archive` + `git apply` hashes the same). No INTERNET permission (no-net build); bench repo b4183ca adds the knob (`src/engineOverrides.ts`, `src/llamaRnShim.ts`: a llama.rn wrapper that Metro resolves only for `LlamaEngine.ts`; the embedding and detector contexts keep the real initLlama). This APK is not the §10 cut 5 APK (different bytes, same engine); use one or the other, say which in the notes.
- **Fields** (llama.rn 0.13.0-rc.4 ContextParams): `nThreads`, `cacheTypeK/V` (f16 f32 q8_0 q4_0 q4_1 iq4_nl q5_0 q5_1), `flashAttn` (auto|on|off), `useMlock`, `nBatch`, `nUBatch`, `cpuMask`, `cpuStrict`, `reload`, `label`. A bad value fails the request in its status file (no silent default). Any change vs the previous request, or `reload:true` (set in all 8), unloads the model and empties `cache/kv`, so every config starts cold the same way.
- **Requests** (`bench-app/requests/`, run in this order; 5 items each: France warm-up (cold, not scored), vit-cry-001 + lan-exp-005 with sources, sweep-ns-001 + sweep-ns-002 chat without sources): `a15sweep-01-t4-f16-base`, `02-t8-f16`, `03-t2-f16`, `04-t6-f16`, `05-t4-q8` (KV q8_0 K and V), `06-t4-fa-on`, `07-t4-fa-off`, `08-t4-f16-repeat` (baseline again; the drift vs 01 is the thermal/noise floor). Deviation: the cut 5 request has no no-source model item (its chat items are cards), so the 2 no-source items are new chat questions checked on desktop (`retrievalUsed` false, 34-59 tokens). Regenerate with `node scripts/gen-sweep.mjs`.
- **Steps**: `adb install -r` over the existing bench install (kit and `files/` survive; fresh phone: §2 first); airplane mode on, note "airplane mode on" and "network permission absent"; battery >= 60%, thermal status 0, note battery temp. Then, per request in order: `scripts/bench-run.sh requests/a15sweep-NN-<name>.request.json 1 --tag sweep --out $D` (fish; `$D` as in §3). Cool-down between requests: wait until thermal status 0 and battery temp <= start + 1 C (min 4 min), write the temp in the notes. Do not touch the phone during a run. To test the best thread count with q8_0, copy request 05, change `nThreads` and `requestId`, run it last (UNKNOWN: whether a 4-thread default is also best for q8_0).
- **Record per config** (`$D/a15sw-NN-...-sweep-r1/`): `bench.json` `completions[]` (llama.cpp timings per call: `promptPerSecond` = prefill tok/s, `predictedPerSecond` = decode tok/s; take the calls with `promptN` >= 300 and `predictedN` >= 30, i.e. the answers, not the gate), `llamaInits[].applied` (the params really used; a second init with `flash_attn_type: off` = the engine's CPU fallback fired), rows' `ttftMs` and `totalLatencyMs` per item, `modelLoadMs` of the warm-up, `telemetry.csv` (max `thermal_status`, battery temp, `app_pss_kb` = RSS proxy; also `adb shell dumpsys meminfo team.sopa.boarbench | grep TOTAL` after the run). Flash attention actually used: `adb logcat -d | grep -i "flash"`.
- **Reading it**: per config take the median of ttft and total over the 4 scored items and the decode and prefill medians; the winner is the config with the lowest median total whose thermal status stayed 0 and whose repeat (08) agrees with 01 within ~10% (else rerun the order with longer cool-downs). Quality: for f16 configs (02, 03, 04, 06, 07 vs 01) the answer text must match 01 item by item (same sampler, same weights; flash attention or thread count may shift a token on a near-tie, report any diff and do not call it a quality change). q8_0 (05) changes text by design: its non-inferiority was judged on desktop (`arms/kvq8/KVQ8-L1.md`); here only compare speed and RSS. If 05 fails to load with flash attention off or reports an init error, record the error text (a quantized V cache needs flash attention); do not tune further. Feed the winner and the measured prefill/decode rates into `A15-LATENCY-BUDGET.md`.
- **Warning (§10 row A)**: building this APK overwrote `build/boar-bench-0cfd4a77-cut5-nonet-de5f5bae429a.apk` (sha `dc2d931f...`) by a name collision. The file now under that name is a rebuild from bench d886a1d + `gen-package` (same engine tree `de5f5bae...`, no-net, 77,175,948 B, sha256 `04d051dc3fb0d0ea45d088c33345356e71ef0f8654e913bcdce2a69442ccd961`; builds are not byte-reproducible). The `dc2d931f...` value in §10 matches no file any more; if you use that APK, record the new sha. The sweep APK has its own `-sweep-` name.


## 12. Cut 6 (cut 5 + DETMAX), built 2026-10-06 on the MacBook, nothing installed
TL;DR: cut 6 supersedes the cut 5 APKs of §10 A and §11 for steps 1 and 2 (smoke + sweep); cut5-speed (§10 B) stays as the retrieval A/B. Same procedure as §10/§11, same 8 sweep requests (unchanged), same kit.
- **APK**: `bench-app/build/boar-bench-0cfd4a77-cut6-nonet-sweep-b0f53fe0d30a.apk`, 77,135,128 B, sha256 `cca28caf613a6b28eb5a7784e64931e45ceb98434c88ad96fde635c423b763f3`; report `build/build-report-cut6-sweep.txt`. No INTERNET permission, includes the §11 engineOverrides knob (default config = plain cut 6). Engine: base `0cfd4a77`, arm `cut6`, patch `coordinator/arms/detfu/detmax-on-cut4.vs-0cfd4a77.patch` sha `824e0b35fcdfe46b25bdb824516b5ccec387247d14a461f7bbfd9fb332fb953b`, treeHash `b0f53fe0d30abb8395e95971e3be4dfc4b406d394bf346dedb525a2678479daa` (status screen `b0f53fe0d30a`; independent `git archive` + `git apply` hashes the same).
- **Desktop sanity** (`bench-app/dry-run/cut6-final.log`, request `requests/cut6-final.request.json` = cut5-final with requestId `dry-cut6`): 9/9 success, EvalTrace valid 9/9, 0 errors; tiers as cut 5 (vit-trv-004, probe-co-002, dng-001 `instant`, rest `fast`); detector canary ok (cos 1), parity 300/300 PASS (`detector-parity-cut6.log`).
- **Handoff**: `handoff/boar-bench-cut6-update.zip` (sha256 `db7bb6baf5484e71097da6121d1404a6662fc2e72ba7c2206801114aa9a84400`): cut 6 sweep APK + cut5-speed APK, `run cut6-final`, the 8 sweep requests, updated `boar_bench.py`, `SHA256SUMS` (`verify` passes).
- [ ] **New check**: a greeting-prefixed emergency question (e.g. "hi there! my friend just got bitten by a snake, what do I do?") still routes emergency: `instant` tier with the first-aid card, detector fire in `reasonCodes`, not a chat/greeting answer. Record the row.
