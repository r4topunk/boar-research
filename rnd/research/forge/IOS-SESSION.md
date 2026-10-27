# iOS session run sheet: iPhone 13, base vs JS perf flags (24 items, ABAB, ≤ 20 min on the device)

> **PARKED (r4to, 2026-10-03 ~11:00):** today's iPhone time went to Anvil's repack probe only. No iOS build or install was done. Kept for a future device window.
>
> **Prerequisites, before that window:**
> 1. r4to's OK to build on the mini;
> 2. a working signed-build route. The mini's `<runner>/ios-gui` wrappers were deleted in the 2026-10-02 22:02 GC. `arms/ios/forge-ios-build.command` replaces them and has not been tried yet. The MacBook can't build it: Xcode 26.1 vs 27.0 on the mini, and no signing identity or profile;
> 3. re-check that `wt/forge-ios` (`cc3ca10f`) still matches the installed iOS tree;
> 4. one install + icon launch by r4to.
>
> Device fact from Anvil's probe (2026-10-03): the 1.5B loads CPU_Mapped only (no repack) on the iPhone 13, footprint ~346–377 MB after load.

TL;DR
- **Scope (r4to, 2026-10-03):**
  - 24 items, 2 arms: **A** = flags off, **B** = `vectorCache` + `sqlBatch` on.
  - Blocks run in the order A1 B1 A2 B2: block 1 = items 1–12, block 2 = items 13–24.
  - The in-retrieve stage timers attribute the difference per stage, so no per-flag legs.
  - Native zstd skipped today.
- **Blocker (decision for r4to): the stage timers and flags need one new iOS build.**
  - There is no Metro dev client on the iPhone. Every iPhone build so far is a Release `.app` with the JS embedded (`boar-eval/devices/DEVICE-KIT.md` §2.4: one build per arm).
  - The installed build (`evalbench-0074737`) has neither the timers nor the flags.
  - Metro on a physical iPhone would also need Wi-Fi to the Mac, which breaks the airplane rule.
  - So the legs need **one JS-only Release build** on the mini (≈ 5–10 min, off the device) plus **one install + one icon launch by r4to**.
  - My attempt to start that build on the mini was blocked by the permission guard (shared machine). **It needs your OK.** The ready-to-run script is `arms/ios/forge-ios-build.command`.
- **The MacBook can't build it today:**
  - it has Xcode 26.1 (the mini builds with 27.0);
  - it has 0 signing identities and 0 provisioning profiles.
  - The mini has both: identity `Apple Development` and 2 profiles.
  - The mini's GUI build tooling (`<runner>/ios-gui`) was deleted in the approved 2026-10-02 22:02 disk GC (`rnd/kiln/DISK-LOG.md`). The script replaces it for this one build.
- **Device time ≈ 15 min:**

  | Step | Time |
  |---|---|
  | install | 1 min |
  | r4to: icon launch, then airplane | 2 min |
  | warm-up | 1 min |
  | 4 blocks × ~2.5 min (iPhone P1: ~8 s per item) | 10 min |

## 0. Ready now (checked on the MacBook)

| What | Where | Check |
|---|---|---|
| Build tree: `00747371` (the installed iOS tree = main `0cfd4a77` + PR #62 ui-ios + bench) + `forge-arms.patch` (sha `914086dc…`) | `wt/forge-ios`, local commit `cc3ca10f` (not pushed) | Patch applies cleanly. Vitest **2567/2567** on the patched tree. tsc: only 2 errors, in untouched `src/bench/modelBench.ts` (`ram-monitor` resolved through my symlinked node_modules; not from the patch). iOS chat polls with `DEVICE_EVAL_ON` (`src/ui-ios/ChatScreen.tsx:447`). |
| Native zstd (for a later day, not built today) | `modules/boar-zstd` (in the tree; **removed by the build script**) | The C decoder cross-compiles for `arm64-apple-ios15.1` with `-O3`, cleanly. The Swift API calls match expo-modules-core 57.0.18 (`NativeArrayBuffer.wrap(dataWithoutCopy:cleanup:)`, `TypedArray.rawPointer`). Never compiled as a pod: risk is Swift seeing the C header through the pod module. |
| Build script (mini, GUI session) | `arms/ios/forge-ios-build.command` | Runs in an **APFS clone** of `<runner>-ios-build` at `<runner>/forge/ios-build`, so Anvil's and Kiln's build dir is untouched. It reuses the `00747371` prebuild (`IOS_SKIP_DEPS=1`: the native side is identical once `boar-zstd` is removed). Signed Release, `EXPO_PUBLIC_DEVICE_EVAL=1`, the same entitlement strip as evalbench. |
| Runner with `perf` | `arms/ios/eval-iphone-perf.mjs` | A copy of Plumb's `eval-iphone.mjs` @ `00747371` plus `--perf <json>`, sent as the request's `perf`. `node --check` passes. The arm build's request parser accepts `perf` (`deviceEvalRequest.pure.ts`). |
| Items | `arms/ios/ios-b1.jsonl` (12), `ios-b2.jsonl` (12), `ios-warmup.jsonl` (1); `make_ios_items.py` | The 52 items that retrieved in **both** iPhone P1 reps, every 52/24-th, in questions72 order. Set sha `fdf48287…`, b1 `b3b9e113…`, b2 `7d370b82…`. Mix: 4 danger, 4 reasoning, 4 explanation, 3 crypto, 2 comparison, 2 health, 2 honesty, 3 travel/synthesis. Warm-up `vit-hum-004`, unmeasured. |
| Paired report | `arms/ios/paired_report.py` | Smoke test on yesterday's P1 r1 vs r2 (no arm). The script works. It showed **rep 2 faster by 8% on 65/68 items with nothing changed**, which is why A and B interleave. Answer text matched only 31/72 between identical runs, while sources matched 72/72, so the guard is sources only. |

## 1. After Anvil's handoff (device steps; r4to present for step 2)

Shell (fish):
```fish
set FI <workspace>/rnd/research/forge/arms/ios
set D <workspace>/boar-eval/runs/devices/2026-10-03/ios-forge
set U <DEVICE_UDID>
set APP <workspace>/builds/ios/device/forge-ios-cc3ca10f/std/BOAR.app   # copied back from <runner>/forge/ios-out
mkdir -p $D
```

1. **Install** (keeps the container: models and packs stay; never uninstall):
   - `codesign --verify --deep --strict $APP`
   - `xcrun devicectl device install app --device $U $APP`
2. **r4to:**
   - open BOAR once **from the icon with mobile data on** (DEVICE-KIT rule after any install);
   - wait for the chat;
   - then turn airplane mode on (Wi-Fi off), keep the phone unlocked, BOAR in the foreground, USB plugged (devicectl transport, the same "charging" condition for A and B).
3. **Warm-up** (launches the app with `GGML_METAL_DEVICES=0`, loads the 1.5B, opens the packs; flags off; not measured):
   ```fish
   node $FI/eval-iphone-perf.mjs --bundle team.sopa.boar --udid $U --questions $FI/ios-warmup.jsonl --models qwen2.5-1.5b-instruct-q4km --quick-first on --always-complete off --dataset forge-ios24 --perf '{"nativeZstd":false,"vectorCache":false,"sqlBatch":false}' --request-id fg-ios-warm --out $D/fg-ios-warm
   ```
   - Must print no `⚠ this build ignores: perf`. If it does, the wrong build is installed: stop.
4. **Four blocks, back to back, no relaunch:**
   ```fish
   set OFF '{"nativeZstd":false,"vectorCache":false,"sqlBatch":false}'
   set ON  '{"nativeZstd":false,"vectorCache":true,"sqlBatch":true}'
   set C --bundle team.sopa.boar --udid $U --models qwen2.5-1.5b-instruct-q4km --quick-first on --always-complete off --dataset forge-ios24 --no-launch
   node $FI/eval-iphone-perf.mjs $C --questions $FI/ios-b1.jsonl --perf $OFF --request-id fg-ios-a1 --out $D/fg-ios-a1
   node $FI/eval-iphone-perf.mjs $C --questions $FI/ios-b1.jsonl --perf $ON  --request-id fg-ios-b1 --out $D/fg-ios-b1
   node $FI/eval-iphone-perf.mjs $C --questions $FI/ios-b2.jsonl --perf $OFF --request-id fg-ios-a2 --out $D/fg-ios-a2
   node $FI/eval-iphone-perf.mjs $C --questions $FI/ios-b2.jsonl --perf $ON  --request-id fg-ios-b2 --out $D/fg-ios-b2
   ```
   - Expected per block: `✓ 12 rows`, status done 12/12.
   - If iOS kills the app, re-run the same line: the same request id resumes.
   - Thermal: `xcrun devicectl device info details --device $U` is not needed. The rows carry timestamps, and block order is the drift control.
5. **Done on the device.** The forge build stays installed: all flags default OFF, which is the same retrieval path as `00747371` (desktop identity 72/72 flags off, Kiln step 0). Reinstalling `evalbench-0074737` instead costs one more install + icon launch, so that's r4to's call.

## 2. Reading (frozen before any iOS data)

```fish
python3 $FI/paired_report.py --a $D/fg-ios-a1 $D/fg-ios-a2 --b $D/fg-ios-b1 $D/fg-ios-b2
python3 <workspace>/rnd/research/forge/arms/stages_report.py $D/fg-ios-a1 $D/fg-ios-a2 $D/fg-ios-b1 $D/fg-ios-b2
```

- **Validity guards** (any failure → report "not readable", no verdict):
  1. 4 × 12 rows, 0 errors;
  2. `perf` in the rows = OFF in A1/A2 and ON in B1/B2;
  3. `retrievedTitles` identical A vs B on ≥ 23/24 (the flags change no sources on the desktop: 72/72);
  4. B rows show the mechanism: `sqlCalls` p50 down (desktop packs 455.5 → 183) and `corpusSqlMs` ≈ 0 after each B block's first item.
- **Primary:** paired per-item `retrievalMs`, B/A median ratio and the count of items with B < A, over 24 pairs.
  - The flags **help on iOS** if the median ratio ≤ **0.90** and B < A on ≥ 16/24.
  - They **hurt** if the ratio ≥ 1.05.
  - Otherwise **no measurable effect** at n = 24.
- **Attribution** (reported, not gated): per-stage paired medians for `sqlMs`/`sqlCalls` (sqlBatch), `corpusSqlMs` + `corpusScoreMs` (vectorCache), `zstdMs` + `utf8Ms` (untouched: they should not move).
  - `zstdMs` A p50 gives the iPhone's fzstd cost. That is the native-zstd kill-rule input for a later day: < 300 ms p50 → native zstd not worth it on iOS.
  - The `calibration:` line gives the M1-Hermes → A15 ratio.
- First item of each block listed apart: B1 pays the vector-cache fill.
- **Expected** (my prediction, stated before data):
  - iPhone retrieval p50 ≈ 1.1–1.3 s (P1);
  - fzstd ≈ 0.5–0.65 s of it (M1 Hermes 499 ms × A15 ≈ M1 single-core);
  - B saves ≈ 0.1–0.3 s p50 (fewer bridge calls + no 10.6 MB row materialization): **ratio ≈ 0.75–0.9**.

## 3. Native zstd on iOS: cost and whether it's worth it today

- **Cost:**
  - + the pod in the same build: full prebuild + pod install, ≈ 10–15 min on the mini instead of ≈ 5;
  - risk of a Swift/C module compile failure (never built for iOS), one retry ≈ 15 min;
  - device time ≈ 0 extra if it rides the same build (`nativeZstd` is a request flag).
- **Gain** (estimate): fzstd ≈ 0.5–0.65 s p50 on the A15 → native ≈ 10 ms, so **≈ −0.5 s p50 retrieval** per question, ≈ 40–50% of iPhone retrieval.
- **Verdict: not today** (r4to's call, agreed): the prebuild + first-compile risk doesn't fit a ≤ 20 min device slot, and today's A run measures the iPhone `zstdMs` that decides it.
  - Next time: the same script with `boar-zstd` kept and `IOS_SKIP_DEPS` unset. The leg is then free on the device.

UNKNOWN:
- whether `ios-build-on-host.sh device` codesigns from the GUI Terminal without the deleted `ios-gui` wrapper's extra env (it worked with the same script and identity on 2026-10-02);
- iOS row-materialization cost of the 5,300-row scan (that's what B measures);
- whether `--no-launch` blocks inherit `GGML_METAL_DEVICES=0` (they do if the warm-up launched the app, as above).
