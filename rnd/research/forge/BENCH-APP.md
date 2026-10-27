# BOAR Bench: a light Android app that runs the evaluated engine on a phone, driven over adb (design, 1 page)

TL;DR
- **What:** a separate Expo/RN app, `team.sopa.boarbench`, in `<workspace>/bench-app`.
  - No chat UI. One status screen, English only.
  - It polls the same request file as boar-app's device eval and runs the **engine's own** `runDeviceEvalRequest` → `answerService.answer()`.
  - It writes the same `<rid>.answer.jsonl` rows, which `devices/android-run.sh` and `scorers/convert_device.py` already consume.
- **Engine identity:** `engine/` is materialized by script from **one boar-eval tree spec**: boar-app sha + arm patch, the same `git archive src assets locales modules package.json tsconfig.json` + `git apply` as `adapters/desktop-node/setup.sh`.
  - `ENGINE.json` records commit, arm, patch sha256 and a **tree hash** (sha256 over the sorted file list + contents of `engine/src` and `engine/modules`).
  - The tree hash goes into the build and into every run's `bench.json`. Desktop trees get the same hash from the same script, so identity is checkable byte for byte.
  - Native modules come from `engine/modules` (`file:` deps). npm versions are pinned exactly from that sha's `package-lock.json`.
- **Release JS by default** (`assembleRelease`, debuggable so `run-as` works), arm64 only, built on the mini by Kiln with one script.

Lane: Forge · front #4 (BOUNTY-BOARD) · Status: design → MVP

## How a run works (no taps)

1. **Kit**, once per phone (`scripts/push-kit.sh`): `adb push` the model + embedding + packs to `/data/local/tmp`, then `run-as … cp` into `files/models`, `files/corpus`. The engine checks sizes and paths exactly as in boar-app.
2. **Start:** `adb shell am start -n team.sopa.boarbench/.MainActivity`. The app initializes headless:
   - `embeddingEngine.load`;
   - registers the wiki packs;
   - wires geo the way desktop-node does, which closes the "places unwired in-app" gap the explorer found;
   - then polls `files/eval/requests/pending.json` every 3 s.
3. **Run:** `scripts/bench-run.sh <request.json> <rep> --tag T --out D`. It wraps `devices/android-run.sh` with `PKG=team.sopa.boarbench`, plus:
   - a **host-side telemetry sampler** every 5 s: `dumpsys battery` (level, temp, plugged), `thermalservice` status, the app's `meminfo` PSS/RSS, and the cpufreq table once → `telemetry.csv` + `device.json`;
   - a pull of `<rid>.bench.json` (engine tree hash, app build sha, flags in effect, start/end wall clock).
4. **Score:** `convert_device.py --commit <engine commit> --platform android` → EvalTrace, unchanged. The judge is unchanged.

## Flags (arms) without rebuilding

| Flag | Where | Status |
|---|---|---|
| model choice | request `models` (existing) | MVP |
| quickFirst / alwaysComplete | request `answerSettings` (existing) | MVP |
| native zstd / vector cache / sqlBatch | request `perf` (forge-ship engine) | MVP, when the engine tree carries forge-ship |
| nThreads (`4`/`"big"`/n), detector on/off, route gate on/off, deep-tier slot | request `bench{…}` → engine hook | **after the MVP**: needs a tiny engine "bench-hooks" arm, applied to desktop and device trees alike so identity holds |

## MVP scope (this front)
- The repo, `engine.sh`, generated pinned `package.json` + lockfile, `app.json` (+ a debuggable-release config plugin), metro alias to `engine/`, the status screen + runner, `push-kit.sh`, `bench-run.sh`, `build-android.sh` (for Kiln).
- **Desktop dry run** (`scripts/dry-run.mts`, MacBook): the same `src/runner.ts` under Node with boar-eval's desktop shims.
  - It adds a llama.rn **completion** shim on node-llama-cpp, so the device path (answerService → LlamaEngine) runs end to end.
  - 3 EN v0.1 items → rows → `convert_device.py` → EvalTrace validated.
  - Plus the tree-hash check against the desktop-node tree of the same spec.

## Out of the MVP
- In-app telemetry via a native module: host-side sampling covers it.
- iOS.
- PT/ES.
- A chat UI.
- Automatic kit download: kits are pushed, offline.
- The bench-hooks engine arm.
- The deep-tier slot (DEEP-TIER-PLAN).
- CI.

## Risks
- **Desktop vs device generation differs by construction:** node-llama-cpp sampler vs llama.rn. Bench measures the device. Identity means the *engine source*, not the outputs.
- **The engine imports `expo-sharing` / `bundled-assets` / `file-hash` / `download-wake-lock`** through the eval path. They are included as pinned deps / `file:` modules even when unused.
- **MacBook constraints:** no JDK and a 99%-full disk, so no local APK build. `node_modules` live on `/Volumes/<volume>` (symlink) for the dry run; Kiln builds on the mini.
- **A phone is needed** for the first install + acceptance (10 items through bench vs answerEval rows from the same kit).
