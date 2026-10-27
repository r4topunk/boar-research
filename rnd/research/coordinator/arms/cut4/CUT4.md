# CUT4: KVFIX + INSTANT-FRAG on cut 3 (engine engineer, 2026-10-05; L0 only, nothing on the mini, nothing pushed)

TL;DR: both fixes are built, one commit each, on cut 3 (`coord/final` c5249560). Unit tests **1293/1293** (cut 3: 1285), tsc clean, each patch applies to a fresh `git archive 0cfd4a77`. L0 INSTANT-FRAG: the France warm-up no longer finishes instant; **0 instant answers lost** on v0.1 EN + V-exact; **1 of 1,328** EN dev messages changes tier (garbage fragment). KVFIX cannot be exercised by any desktop replay (details below); its real gate is the device. Criterion `CUT4-criterion.md` untouched (sha256 c4735323…).

## Patches (all vs 0cfd4a77; verified on a fresh `git archive 0cfd4a77`: `git apply`, `tsc --noEmit` clean, `vitest run`)
| file | sha256 | vitest | tsc |
|---|---|---|---|
| `kvfix-on-cut3.vs-0cfd4a77.patch` (cut 3 + KVFIX; commit 3b9f09de) | `27f7e0f38ea86419db8bd4af69ec43c63046a8fa56fb109eb36dd28fc1a7cb43` | 1289/1289 (+4) | clean |
| `instantfrag-on-cut3.vs-0cfd4a77.patch` (cut 3 + INSTANT-FRAG; branch `coord/instantfrag`, cherry-pick cc516a61) | `5d3922dfc88c7833edd5537af104507be20a094d724c01dcfb59e75c82905685` | 1289/1289 (+4) | clean |
| **`cut4-stack.vs-0cfd4a77.patch`** (cut 3 + KVFIX + INSTANT-FRAG; branch `coord/cut4` HEAD 84cd9c17) | `1fd5d9a57d2d590bd85a67bfe219f2763d9eb6d106e6120261b2d54869432141` | **1293/1293** (+8) | clean |

Worktree `<workspace>/wt/cut4` (branch `coord/cut4`, author `boar-rnd`, never pushed; `node_modules` symlinked to boar-app). The two fixes touch disjoint files (stack = sum of both).

## KVFIX (`src/inference/LlamaEngine.ts`, `kvPath` + `saveKv` only)
- Key flattened with `key.replace(/[^A-Za-z0-9._-]/g, "_")`, so `models/<file>.gguf.<hash>.gate` becomes one file name in `cache/kv/`. `loadKv` uses the same `kvPath`, so save and load always agree.
- `saveKv` creates `dirname(target)` (`makeDirectoryAsync(..., {intermediates: true})`) before `saveSession`.
- No other change. Tests (4, `LlamaEngine.test.ts`, with an in-memory cache dir whose fake `saveSession` throws "Failed to save session" when the directory is missing, i.e. the A15 failure; all 4 fail on cut 3 and pass now): a key with "/" round-trips save -> load; the gate prefix is saved once and not re-prefilled on questions 2 and 3; the answer prefix is saved once and a fresh engine restores it with 0 warm-ups; gate and answer files differ and sit directly in `cache/kv/`.
- **Gate (2) cannot test KVFIX on desktop.** The desktop adapter generates through `makeServerEngine` (llama-server), not `LlamaEngine.ts`; the app's shim no-ops `saveSession` (A15 diagnosis). So an s44 replay is byte-identical for KVFIX by construction; it only guards the stack (INSTANT-FRAG items). The stub replay shows the same. The script for the real desktop run is `tools/cut4-l1.sh` (below). Gate (3) is device-only: `[gate] session save failed` absent, `loadGateMs` set (not `-`) from question 2, `[gate] answer prefix restored in N ms`, TTFT p50 down vs the A15 smoke.

## INSTANT-FRAG (`src/routing/context.ts`, `instantFinalBlock`; caller `answer.ts` unchanged)
Two new block reasons, `"fragment"` and `"figurative"`; the caller already turns any non-null block into `instant:not-final-<reason>` and falls through to the normal (model) path.
- **fragment:** snippet starts with a bullet/dash/heading marker followed by a space (`- —`, `•`, `* `, `## `, `==`). A dash glued to a word or digit ("-5 C", "—France") is not a fragment.
- **figurative:** the question has the word "capital" and **every** "capital" in the snippet carries a figurative modifier (gastronomic, culinary, cultural, financial, economic, commercial, industrial, spiritual, religious, intellectual, artistic, fashion, wine, music, tech, entertainment, sports, ...) that the question does not itself use. One literal "capital" in the snippet (Paris is the capital ... and its cultural capital) leaves it alone. "administrative/legislative/executive capital" are not in the list (they answer the question).
- Tests (8): `context.test.ts` +2 (blocked: the Lyon line, bullet, heading, "financial capital" of Switzerland, "cultural and economic capital"; still final: Paris sentence, Paris + "its cultural capital", question that itself says "cultural capital", "-5 degrees ..." digit start, "administrative capital"), `answer.test.ts` +2 (France warm-up: Wikivoyage chunk with the Lyon line -> `instant:not-final-fragment`, tier fast, model runs; a correct Paris sentence next to a longer figurative one still finishes instant with no model load).
- Side effect kept as is: the `instant` preview event is still emitted before the block (as for every other `not-final-*` reason), so the UI may flash the fragment until the model answer streams. Not changed ("no other change").

## L0 (stub-LLM replay, real engine, kit A = crypto + Wikivoyage, no detector, no places; cut 3 tree = `git archive coord/final`, cut 4 tree = coord/cut4; `tools/mkreq.py`, `tools/replay.sh`, `tools/cmp.py`)
| set | n | tier changes | instant lost (were correct) | other diffs |
|---|---|---|---|---|
| v0.1 EN public 60 + V-exact 11 (65 unique ids) | 71 | **0** | **0** (none of these 65 finishes on an extractive snippet: the 11 instants are cards, calculators and "places pack not installed") | 0 (reason codes and text byte-identical) |
| France warm-up "What is the capital of France?" | 1 | instant -> fast (`instant:not-final-fragment`) | the old answer was the Lyon line (wrong) | n/a |
| Sonar EN dev messages (aligned 1,010 + terse-live 213 + emergency-dev 105, last user turn) | 1,328 | **1**: dev-0070 "what do i put on it", instant -> fast; the old instant was "- Rabello: Jadranski put - Ričardova Glava - Richard's Head:" (garbage) | 0 correct | 0 |
| fresh lookup set `lookup-set/` (40: 30 lookup + 10 control) | 40 | 0 | 0 | 0 |
Dev tier mix: cut 3 128 instant / 1,200 fast; cut 4 127 / 1,201. Traces and comparison output in `l0/` (`A.cut3|cut4.traces.jsonl`, `A.cmp.txt`, `D.cmp.txt`, `lookup-score.*.txt`; the 1,328-row dev traces are not kept).

**Lookup set.** `lookup-set/items.jsonl` (sha256 72404eea…, 40 items) was already in place when I looked (written by whoever the coordinator used; I did not write or edit it, and the rule was derived from the criterion and the A15 diagnosis, not from it; I opened the file after the code was committed apart from one `head`). `lookup-set/score.py` is the scorer: per item tier and correctness (normalised `expected`, `|` alternatives, D.C. / accent safe), controls must not finish instant, exit 1 on any instant-wrong or control-instant. Under the stub only instant answers are real, so model-path rows read NO; use it on real-model traces for the answer-quality column.
- Result on kit A, cut 3 and cut 4 identical: of 30 lookups only 2 finish instant, 1 correct, **1 wrong: lk-021 "what is the capital of the usa" -> "Baton Rouge is the capital of Louisiana, USA..."** (a sub-national capital; INSTANT-FRAG does not catch it, the sentence is a genuine statement about a capital). 0/10 controls finish instant.
- So the criterion's L0 France check passes and the lost-correct bar passes, but the lookup set shows a second off-topic instant class not covered by "fragment/figurative". Candidate rule (NOT built, outside the frozen scope, needs the coordinator's decision): a question that names a country/"the usa" and a snippet whose capital belongs to a sub-national entity ("capital of <state/province/county>"). It would be one more block reason.

## UNKNOWN
- Whether the figurative list is complete (it is a denylist; "capital" only). Questions about other head nouns (largest city, currency) have no such rule.
- KVFIX on a real device: save/load actually working, the native error text of the old failure (the diagnosis says only "Failed to save session"), and the TTFT gain. A second cause for save failures (empty-token state) would only show after this fix is on the phone (`adb shell run-as team.sopa.boarbench ls -R cache/kv`).
- INSTANT-FRAG L1 (v0.1 EN s44+s45, changed items only): not run. By the L0 above the L1 changed-item set on v0.1 is empty (0 tier or text changes), so L1 should reduce to the unchanged-replay check.

## Gate-2 script (for the coordinator; not run here, the mini is busy)
`tools/cut4-l1.sh setup` builds `<runner>/kiln/be-0cfd4a77-cut4` from the stack patch (and copies `be-ship` from the cut 3 tree); `tools/cut4-l1.sh run` generates v0.1 EN s44 + s45 with the same config as `cvh-l1.sh` (detector v3b, `--places`, `be-ship`, `HEAVY_CLASS=normal`) from the stored cut 3 requests, then prints `cmp.py` against `runs/kiln/cut3-confirm/cut3-v01-s44|45` (items whose answer, tier or reason codes differ). Pass = at most 1 item per seed differing (run-to-run noise, lan-exp-007 precedent). It checks the tree's PATCH_SHA256 prefix `1fd5d9a57d2d590b` and the `be-ship` adapter hash `949eee0355032eb1` before running.

## Other deliverables
- **convert_device.py (host export bug):** the file is `boar-eval/scorers/convert_device.py` (there is no copy in bench-app). Added `encoding="utf-8"` at lines 146 (`read_text`) and 149 (`write_text`) and committed it in **boar-eval** (private repo, local, not pushed): 5285766, only that file (the repo's other uncommitted changes were left alone). I did not add `newline="\n"`.
- **Files:** `tools/{mkreq.py,replay.sh,cmp.py,cut4-l1.sh}`, `lookup-set/score.py`, `l0/`.

## BOAR Bench APK (cut 4 stack; built on the MacBook with `bench-app/scripts/build-android.sh 0cfd4a77 --patch cut4-stack... --arm cut4`, JDK 17 = homebrew openjdk@17, floor 20 GiB; 28 GiB free after; NOT installed anywhere)
- APK: `<workspace>/bench-app/build/boar-bench-0cfd4a77-cut4-d631a9defc26.apk`, 77,087,172 B
- sha256 `80925f6aab5bb00bf9386d717f5d7a08715bfdf066cc3513c9cb61b769359d9a` (also `build/*.apk.sha256`, `build/build-report.txt`)
- `engine/ENGINE.json`: commit 0cfd4a77badd01297af8dc9a3a10924f8a895105, arm cut4, patchSha256 1fd5d9a5… (= the stack patch), **treeHash `d631a9defc26ed8eb479d730955f5370673074db5ff1e8cda403c92e4375a1e8`**, lockSha256 49471ca3… (package-lock unchanged from cut 3).
- `bench-app/engine.lock.json` is still the cut 3 spec (the build prints the expected "differs from the committed lock" warning); not changed, nothing committed in bench-app.

## No-network build (2026-10-05, MacBook; nothing installed anywhere, Mac mini not touched)
- **APK:** `<workspace>/bench-app/build/boar-bench-0cfd4a77-cut4-nonet-6a61670e3ba6.apk`, 77,091,228 B, sha256 `966ad34b548d111b386c6bb34f11707469a09dba4e03bfbf2ffaf2985c1cfc42`. Built with `BENCH_NONET=1 BENCH_FLOOR_GB=20 scripts/build-android.sh 0cfd4a77 --patch coordinator/arms/instsubj/instsubj-on-cut4.vs-0cfd4a77.patch --arm cut4` (JDK 17).
- **Engine identity unchanged:** `ENGINE.json` treeHash `6a61670e3ba63088f6d4636031b80f20ed91340676d6a13b48304c58dda2dabe`, patch sha `d51e844c6522cb1825e43d800626516af099ae462c85e39396f7e2a4ea04dfa3`, lockSha256 `49471ca3...` (same as the cut 4 APK `22e22f2c...`).
- **Where INTERNET came from:** the Expo prebuild template manifest (INTERNET, SYSTEM_ALERT_WINDOW, VIBRATE, storage) plus library manifests merged in (ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE etc. via RN / expo / OkHttp-related libraries). Fix: new Expo config plugin `bench-app/plugins/withNoNetwork.js`, active only when `BENCH_NONET=1`, adds `tools:node="remove"` for INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, CHANGE_NETWORK_STATE, CHANGE_WIFI_STATE, NEARBY_WIFI_DEVICES, SYSTEM_ALERT_WINDOW. Default build is unchanged. `build-android.sh` adds `nonet-` to the file name when the flag is set.
- **debuggable stays ON.** The kit push and result pull use `adb run-as`, which needs a debuggable app. It does not touch the network. `run-as`, `adb push` and `adb pull` need no INTERNET permission (they go over the adb USB link).

| Audit (`boar-app/scripts/audit-apk.py` 0.2.0, aapt2 36.0.0) | cut 4 APK `22e22f2c...` | no-network APK `966ad34b...` |
|---|---|---|
| Verdict | NETWORK-CAPABLE | **NO-NETWORK-BY-CONSTRUCTION** |
| Declared permissions | INTERNET, READ_EXTERNAL_STORAGE (max SDK 32), SYSTEM_ALERT_WINDOW, VIBRATE, WAKE_LOCK, WRITE_EXTERNAL_STORAGE (max SDK 32), own DYNAMIC_RECEIVER permission | READ_EXTERNAL_STORAGE (max SDK 32), VIBRATE, WAKE_LOCK, WRITE_EXTERNAL_STORAGE (max SDK 32), own DYNAMIC_RECEIVER permission |
| Network-related permissions | INTERNET | none (`aapt2 dump permissions` agrees) |
| Hosts to review | 19 | 19 (identical: strings in `assets/index.android.bundle` and native libs, e.g. download.geonames.org, archive.org, classic-assets.eascdn.net, android.googlesource.com) |
| GMS / Firebase, trackers, remote code | none | none |
| Debuggable, signer | yes, public Expo debug key | yes, public Expo debug key |

- **Network APIs still referenced in code (capability only, reported as the tool lists them):** OkHttp (+318 classes), `java.net.HttpURLConnection`, `java.net.Socket`, `android.webkit.WebView`, `android.app.DownloadManager`, React Native networking classes, and the engine's download / geonames code in the JS bundle. These are the same in both APKs. Without INTERNET the kernel refuses socket creation for the app (no `inet` group), so none of them can reach a network. The bench path (`runDeviceEvalRequest` -> `answerService.answer`) does not use them.
- **Desktop sanity (same 9 rows, `requests/cut4-final.request.json`, dry run with the engine tree of this build, llama-server built from llama.cpp 4bc272f = llama.rn's b11010, CPU, on this M1):** 9/9 success, EvalTrace valid 9/9, 0 errors; detector canary ok (cos 1), parity 300/300 (PASS). Routes identical to the previous cut 4 dry run: the 3 deterministic instant rows (vit-trv-004, probe-co-002, dng-001) are byte-identical; the France warm-up gets `instant:not-final-fragment` and a model answer naming Paris; the other 5 rows are `fast`. Model-written text differs a little on 5 rows (a different llama-server binary than the earlier run, which is not available on the MacBook); reason codes differ only in citation bookkeeping on 3 rows. The JS engine code is the same tree, so no behavior change is expected from the manifest-only difference.
- **Note on the tooling:** the b11010 `llama-server` in the mini's tree crashes with SIGILL on this M1 (built for a newer CPU); I built a local one in the session scratchpad (not in the repo).
- UNKNOWN: on-device behavior (not installed); whether the Android OS or a library ever touches ConnectivityManager at start-up without ACCESS_NETWORK_STATE (a SecurityException would show in logcat; the bench app does not depend on expo-network).

