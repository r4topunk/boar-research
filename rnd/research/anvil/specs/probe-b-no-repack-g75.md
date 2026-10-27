# Probe B run sheet: Qwen3-4B with `no_extra_bufts` on the moto g75 (run-ready, frozen 2026-10-02)

For Plumb, the next g75 session. Card: `../cards/android-lowram-no-repack.md`. Probe A (Kiln, mini, `<runner>/kiln/probeA/`) confirmed the mechanism on desktop:
- with repack: anonymous memory 3.25 GB, RSS 5.1–5.4 GB;
- without repack: anonymous memory **0.88–0.91 GB**, RSS **3.41 GB**;
- decode the same (~21 tok/s); macOS prefill faster without repack (an Accelerate artifact; Android UNKNOWN).

## 1. The JS change (one line plus a log line; no native rebuild)

`src/inference/LlamaEngine.ts` at upstream/main 0cfd4a77, in `load()`, the `initWithCpuFallback(…)` params object (lines ~268–277):

```ts
        {
          model: modelPath,
          use_mmap: true,
          use_mlock: false, // avoid pinning full weights in RAM; rely on mmap streaming
          n_ctx: nCtx,
          n_threads: nThreads,
          n_gpu_layers: 0, // CPU-only for broad device compatibility; adjust per-device
+         // PROBE B (Anvil android-lowram-no-repack): keep weights file-backed; no CPU_REPACK anonymous copy.
+         ...(Platform.OS === "android" ? { no_extra_bufts: true } : {}),
        },
```

- Plus, right after the load succeeds (next to `this.modelInfo = …`):
  ```ts
  console.warn(`[engine] PROBE-B no_extra_bufts=${Platform.OS === "android"} nCtx=${nCtx} model=${modelFilename}`);
  ```
- **Why it is enough:**
  - `initWithCpuFallback` forwards the params object unchanged (generic `P & BackendInitParams`; `initFallback.ts`);
  - llama.rn's JSI layer reads the key: `cparams.no_extra_bufts = getPropertyAsBool(params, "no_extra_bufts", …)` (`node_modules/llama.rn/cpp/jsi/JSIParams.cpp:356`, rc.4);
  - the CPU fallback branch spreads the same `params`, so it inherits the flag.
- **Not part of Probe B:** nCtx stays as the engine picks it (4096 on 7.2 GiB). The probe isolates the repack effect. An nCtx 2048 variant is a separate, optional run.

## 2. Applying it through Metro (debug dev client, no rebuild)

1. In the worktree Metro serves for the g75 session (Plumb's 0cfd4a77 dev tree), apply the two edits above. `git stash` or `git diff` it afterwards, so the tree returns to 0cfd4a77 exactly.
2. Metro picks up the change. Then **force-stop and cold-start** the app so the engine re-initialises:
   `adb shell am force-stop team.sopa.aoair` → launch from the icon, or with `adb shell monkey -p team.sopa.aoair 1`.
3. **Verify the patch is live before any measurement:**
   - the Metro or console log shows `[engine] PROBE-B no_extra_bufts=true`;
   - abort if it is absent (stale bundle).
4. The model file is already on the phone (the 4B was installed for the killed runs). No download.

## 3. Measurements (unplugged, airplane mode, as in P3a)

- **Memory during load and after:**
  - start before launching the app, every 1 s for 120 s: `adb shell dumpsys meminfo team.sopa.aoair | grep -E "TOTAL (PSS|RSS)|Native Heap"`;
  - keep `adb logcat -b events | grep -E "am_kill|killinfo|am_proc_died"` running for the whole session.
- **Two cold launches** (force-stop between them), each loading the 4B. Then **10 answers** with the P3a request (`and-*-p3speed` items), using the existing device-eval transport.
- **Pull the rows; convert them with `scorers/convert_device.py`;** then read them with `anvil/tools/e2_latency_check.py <traces> --device g75`.

## 4. Frozen criterion (stated before any run)

1. **0 LMK kills of `team.sopa.aoair`** across both cold launches and the 10 answers (events buffer).
2. **Peak TOTAL RSS ≤ 3.5 GiB** for the BOAR process during load and answering (`dumpsys meminfo`), against 4.74–5.03 GiB in the killed runs.
3. **Answers are produced:** 10/10 rows with `outcome: success`. Route and shown sources are identical to the desktop `and-qwen` trace for the same items, with the same kit and RAM profile (7.2 GiB).
4. **Speed is reported, not gated:**
   - prefill tok/s, decode tok/s, first visible text and total, read against the frozen g75 prediction (first visible 15–21 s, total 33–45 s, prefill 12–18, decode 2.5–3.8 tok/s; `android-4b-latency-budget` §2b).
   - Whether the 4B or the 1.5B is the 8 GB default is r4to's call with these numbers. The 1.5B measured on the g75: total p50 9.6 s, 12.2 tok/s, 29 declines of 72.

- **Pass = 1 + 2 + 3.**
- **Fail on 1 or 2:** the next step is the same probe with nCtx 2048, then the 1.5B as the 8 GB default.

UNKNOWN: whether lmkd on Android 16 kills a foreground app for file-backed RSS under pressure (criterion 1 answers it); and the no-repack prefill speed on the A78 (criterion 4 reports it).
