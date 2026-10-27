# Deep tier on 12 GB Android: Qwen3.6-35B-A3B streamed by BigMoeOnEdge as an opt-in "Go deeper" (scoping)

TL;DR
- **What:** an opt-in deep answer from **Qwen3.6-35B-A3B UD-Q2_K_XL** (12.29 GB; the competitor a competitor team's model).
  - It runs in a **separate process**: BigMoeOnEdge's `bmoe-cli`, shipped as `libbmoe-cli.so` and spawned with `ProcessBuilder`. That is the upstream Android pattern; no JNI.
  - Experts stream from flash (O_DIRECT + its own expert cache).
  - The 4B is **unloaded first** (model swap), then reloaded lazily.
- **Why:** the biggest measured ratio lever. Δ **+0.060** (CI +0.021…+0.101) vs the 4B on v0.1, desktop, deep contract 400 ctx / 200 tok / k = 6 / no-think. Linux memory passes (cgroup peak 6.59 GiB, anon 4.0–4.3 GiB). It is reported separately unless the measured profile answers deep.
- **Cost:** **≈ 5 build days + 1 device day, +2–3 days risk buffer → 7–9 days.** It fits before the Oct 22 freeze only if it starts by ~Oct 10.
- **Blockers:**
  - **there is no 12 GB Android in hand**, and there is no device verdict without one;
  - **UNKNOWN: whether the bounty's measured profile is deep-by-default.** That decides whether the +0.06 counts, at ~55–80 s per answer.
- **Recommendation: GO for the desktop part (D1–D4) now**, in BOAR Bench (no work inside the app maintainer's app). Buy or borrow a 12 GB Pixel (also the demo device, SHIP-SPEED.md §3) before D5.

Lane: Forge · front #4 (BOUNTY-BOARD) · Status: scoping · Sources: `anvil/exp/outofkit/README.md` §c, `boar-eval/reports/night-2026-10-01/deep35.md` + `p0-deep-memory.md`, `anvil/cards/deep-tier-streamed-moe.md` + `deep-tier-bounded-prefill-t2.md`, the BigMoeOnEdge checkout on the mini (`<runner>/spikes/bmoe`, README + `examples/android`).

## 1. Integration path (BOAR Bench first, the PR to the app maintainer later)

| Piece | Design | Notes |
|---|---|---|
| **Engine binary** | `bmoe-cli` built for arm64 with the NDK, pinned at **v0.28.0 `374f562`** (Kiln's P0 build). Shipped in `jniLibs/arm64-v8a/libbmoe-cli.so`, so Android installs it into `nativeLibraryDir`. That is the one executable location allowed under W^X since API 29. Needs `useLegacyPackaging` / `extractNativeLibs=true` | Separate process → **no symbol clash** between bmoe's llama.cpp fork (`Helldez/llama.cpp` submodule) and llama.rn's b11010. A deep-tier crash or OOM does not kill the app |
| **Native module** `boar-deep` (Expo, Kotlin) | `start(model, args)` → ProcessBuilder; `prompt(json)` over stdin; tokens + telemetry lines from stdout as JS events; `stop()` = destroy; exit code / stderr tail on failure | Same pattern as bmoe's demo app (a foreground service keeps it alive with the screen off; Bench doesn't need that). ~250 lines Kotlin |
| **Engine adapter** | A `StreamedEngine` implementing the generate interface `answer.ts` uses for the deep tier (`generate({messages, nPredict, onToken, onTimings})`) on top of `boar-deep` | The deep routing exists (`resolveDeepModel`, deep settings, tier "deep", `deepen()`). Only the backend changes |
| **Model swap** | Deep request → `llamaEngine.unload()` (frees the 4B's ~3 GiB anonymous memory with repack) → spawn bmoe. Then stay in "deep mode" for follow-ups; after 60 s idle or a fast-tier question, kill bmoe and reload the 4B lazily | The 4B + bmoe don't co-fit on 12 GB (3 + 4.3 GiB anon + file pages + Android). Embedding (37 MB) and detector (106 MB, mmap) stay |
| **No repack / page cache** | bmoe holds dense weights itself (`--dense-weights anon`, 1.63 GiB) and reads experts with O_DIRECT into its own cache (`--cache-mb 1500`). llama.rn's repack doesn't apply. The model file must sit in app-internal storage (not `/sdcard` FUSE) | P0 knobs: `--moe-stream --overlap --dense-weights anon --cache-mb 1500 --ubatch 512 -t 4 --io-threads 4 --chatml --no-think -n 200 -c 4096` |
| **Fit rule** | Catalog entry `streamed: true`, `minDeviceRamBytes ≈ 11.5 GB`. `memoryFit` returns a `streamed` verdict instead of rejecting a 12.3 GB file | Small. Hidden on < 12 GB phones |
| **Prompt parity** | The deep35 desktop arm used llama-server with the GGUF's **jinja** template; bmoe's CLI was probed with `--chatml`. Either feed bmoe the template-rendered prompt (what our llama-server shim does via `/apply-template`), or prove `--chatml --no-think` is token-identical for these prompts | Otherwise the device runs a different prompt than the one that scored +0.06 |
| **BOAR Bench deep slot** | request `models: ["qwen3.6-35b-a3b-ud-q2kxl"]` + `answerSettings.alwaysComplete` (deep route), `bench.deep{cacheMb, threads, ioThreads}`. The kit push streams the 12.3 GB file; telemetry tracks the child process (PSS by pid) as well as the app | Desktop dry run: a `boar-deep` shim that spawns the macOS bmoe build |

## 2. Build and reproducibility cost
- **Pins:** bmoe tag + its llama.cpp-fork submodule sha + NDK r27 (`27.1.12297006` is installed on the MacBook) + the model sha (`96b9c0af…`).
- **Build script:** upstream ships `scripts/build-android.ps1` (PowerShell), so we write a bash equivalent (cmake + NDK toolchain, `-DGGML_*` CPU flags for arm64 dotprod/i8mm). It runs on the mini with Kiln's Linux build as the reference. ~10–20 min per build; the binary is ~10–20 MB (UNKNOWN).
- **APK:** +1 `.so` (the CLI) + `boar-deep` module. llama.rn is unchanged.
- **License:** Apache-2.0: carry NOTICE and the license in the repo and app.
- **For a stranger's build:** one more pinned submodule + NDK cmake. That's the same toolchain RN already needs. No Rust, no extra SDK.

## 3. Day count (desktop first; the device day needs the phone)

| Day | Work | Done when |
|---|---|---|
| D1 | Pin bmoe v0.28.0 (+ fork sha). Bash Android build on the mini; macOS build for the dry run | Android `libbmoe-cli.so` + macOS `bmoe-cli` built from the pins; sha in a build report |
| D2 | `boar-deep` Expo module (Kotlin ProcessBuilder, stdout events, cancel, errors) + JS `StreamedEngine` | Unit tests on the JS side; prebuild autolinks it; release bundle OK |
| D3 | Engine arm `deep-streamed`: deep tier → `StreamedEngine`, model swap + idle policy, `streamed` fit verdict, catalog entry, receipt fields (`deep:streamed`, bmoe version, cache MB) | vitest green; desktop answerEval identity unchanged for fast-tier items |
| D4 | **Desktop parity** in BOAR Bench: the dry run with a macOS bmoe shim on the 62 deep-route v0.1 prompts vs deep35's llama-server prompts. (a) prompt tokens identical; (b) greedy first 64 tokens identical on 10 prompts (UNKNOWN whether the fork matches b11010 numerically); else (c) a judged L1 on the EN 24 slice ≥ deep35's desktop result − MDE | parity verdict written |
| D5 | Device session prep: kit (12.3 GB push), bench requests, child-process telemetry, ADR §7 sheet | run sheet frozen |
| **Device** | ADR §7 on a 12 GB phone: TTFT p50 ≤ 15 s, total ≤ 60 s, ≥ 4 tok/s sustained, **0 LMK in 10 answers**, peak PSS ≤ 8 GB; thermal log | verdict |

## 4. Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| No 12 GB phone before the freeze | **high today** | buy a Pixel 9/10 (12 GB; also the demo phone); D1–D4 don't need it |
| LMK kills the child (4+ GiB anon) when the app isn't foreground | medium | foreground service (bmoe's own app does this); the bench keeps the screen on |
| Latency ~55–80 s/answer (swap 3–10 s + prefill 13–17 s + decode 33–54 s), thermal throttling after ~50 s | high | opt-in only, streamed text, progress line. Never the default unless r4to decides the claim profile |
| bmoe's llama.cpp fork ≠ b11010 → different logits from the desktop deep35 run | medium | D4 parity (prompt identity + greedy check, else judged L1) |
| Unsafe-rule hits (deep35 s43: 4 vs 3, contested as negations) | low | Compass's checker v0.8.x already has the negation fixes; re-score |
| Disk / download: 12.3 GB + 2.5 GB + packs ≤ 50 GB | low | kit push for the bench; download UX in the PR phase |
| Scope creep vs the freeze | medium | D1–D4 time-boxed; kill at D4 if parity fails |

## 5. Decisions needed (not Forge's)
1. **Claim profile:** is the deep tier part of the measured configuration (deep-by-default / `alwaysComplete`), or only a separately reported "deep mode" (r4to's rule of 2026-10-02)? If only separate, the +0.06 helps the demo story, not the scored ratio.
2. **Device:** buy/borrow a 12 GB Pixel. Required for the deep verdict and the demo anyway.

UNKNOWN:
- bmoe Android binary size;
- whether `--chatml --no-think` equals the jinja prompt for Qwen3.6;
- fork numerics vs b11010;
- swap time on a phone;
- child-process LMK behaviour on Android 16;
- the sustained thermal envelope.
