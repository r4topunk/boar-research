# BATCHRET-PHONE (2026-10-20, main): on the Pixel 8a, batched pack lookups cut retrieval 5.0 → 1.4 s and the 1.7B's TTFT 9.1 → 5.5 s (-3.5 s paired), with identical retrieval on 9/9 questions in all 4 runs

Measured, not projected. Phone: Pixel 8a (GrapheneOS, 8 GB), airplane mode on, Wi-Fi off, BOAR Bench in front, AC power. Model qwen3-1.7b-q4km (thinking off), claim kit. Set litelat-9 (the LITELAT set: 7 v0.1 dev items that reach the model + 2 retrieval-wait safety cards). Same-session A/B, order A B A B (17:44–17:52), cold start per run, thermal status 0 before each run. 4 runs x 9 questions. 0 LLM judge calls, 0 paid.

- **A** = the build that was installed: bench-app live-view 43abbeb, arm `cut7-cmp30off` (tree c407db32), APK `boar-bench-0cfd4a77-cut7-cmp30off-nonet-c407db3224e2.apk`, sha256 c1864d32….
- **B** = A + arms/batchret/batchret.patch (sha 57367f4a…) on the engine copy: arm `cut7-cmp30off-batchret`, tree 0ca54d87…, patch `phone/cut7-cmp30off-batchret.vs-0cfd4a77.patch` (sha256 b1666764…, = cmp30off patch + batchret patch, applied by scripts/engine.sh). APK `bench-app/build/boar-bench-0cfd4a77-cut7-cmp30off-batchret-nonet-0ca54d870ba8.apk`, **sha256 d29cd152961259b4d224515d734eea67567e8d23a3c03f192f3f50e43fe1cfa8**.
  - Same package (team.sopa.boarbench), same signing cert (SHA-256 fac61745…), same permission list as A (no INTERNET). Installed with `adb install -r` (files/ kept). Every bench.json carries the expected tree (A runs c407db32, B runs 0ca54d87).
  - Engine tests on the B tree (boar-app 0cfd4a77 full tree with the engine overlaid, node_modules from wt/batchret): **1358/1358 pass** (cmp30off 1350 + 8 BATCHRET tests); `tsc --noEmit` clean.
  - Build: incremental `gradlew :app:assembleRelease` on the MacBook (Homebrew openjdk@17, existing nonet android/, no npm ci, no prebuild), the same way as the cmp30off build. Disk stayed above 6 GB free.

## TL;DR
| fast-tier model answers (7 items) | A p50 (runs 1a / 3a) | B p50 (runs 2b / 4b) | pooled A → B | paired Δ per item, median (min…max) | projection |
|---|---|---|---|---|---|
| retrieve() wall | 5 115 / 4 962 | 1 332 / 1 645 | 5 039 → 1 451 ms | **-3 681 ms** (-6 054…-852) | — |
| pack SQL calls | 435 / 435 | 27 / 27 | 435 → 27 | -409 (-715…-232) | 435 → about 27 |
| pack SQL summed ms | 3 452 / 3 393 | 495 / 537 | 3 408 → 497 | -2 888 (-5 070…-1 491) | -3.0 to -3.5 s |
| TTFT | 9 480 / 8 760 | 4 978 / 6 090 | 9 120 → 5 549 ms (-39 %) | **-3 494 ms** (-5 606…-245) | -2.7 to -3.4 s |
| total | 12 455 / 12 328 | 8 203 / 10 262 | 12 392 → 9 395 ms (-24 %) | **-3 118 ms** (-5 236…+35) | -2.7 to -3.4 s |
| prefill (llama.cpp prompt_ms) | 3 191 / 3 294 | 3 343 / 3 701 | 3 232 → 3 452 ms | +458 (-35…+933) | 0 |
| decode tok/s | 15.6 / 14.9 | 14.7 / 12.2 | 15.3 → 14.2 | -1.8 | 0 |

| safety cards (2 items) | A p50 (1a / 3a) | B p50 (2b / 4b) | pooled A → B | paired Δ median (min…max) | projection |
|---|---|---|---|---|---|
| retrieve() wall | 8 169 / 7 931 | 1 977 / 3 367 | 8 055 → 2 849 ms | -5 378 (-7 686…-3 070) | — |
| pack SQL calls | 665 / 665 | 34 / 34 | 665 → 34 | -632 | 665 → about 42 |
| card TTFT (= total) | 8 418 / 8 101 | 2 119 / 3 630 | 8 272 → 3 097 ms (-63 %) | **-5 385 ms** (-7 699…-3 072) | 8.9 → 3.5–4.4 s |

**Did the projection hold?** Yes, at or slightly above its top end. Retrieval fell by 3.6–3.7 s and TTFT by 3.5 s (paired median) against a projected 2.7–3.4 s. The safety-card wait fell to 2.1–3.6 s against a projected 3.5–4.4 s. The calls went 435 → 27 exactly as projected. The gain beat the projection because the JS remainder of the pack search also shrank: wikipacks wall minus pack SQL time was about 1.6 s in A and about 0.9 s in B (fewer awaits and row-object round trips). The projection had assumed it would not change.

## Identity (A vs B, per question, all 4 runs)
| check | result |
|---|---|
| retrievedTitles (the row's sources list, in order) | **9/9 identical across all 4 runs** |
| retrieve event n / k | 9/9 identical |
| reason code `context:X->Y` (context size before → after compression) | 9/9 identical |
| prompt tokens of the answer completion (promptN) | 7/7 model items identical (A and B 274 p50) |
| declines | 6/9 identical; vit-cry-001, lan-exp-002 and lan-hlt-003 flip between runs, **within A as well as across arms** (1a vs 3a also differ). This is LITELAT's known device sampling noise and not a retrieval difference, because the context is identical. |

Identical titles, context sizes and prompt token counts on every question mean the model saw the same retrieved context in A and B, which is the on-device match to the desktop 390/390 byte-identity result (BATCHRET.md).

## Spread and caveats
- Within-arm spread: A's two runs agree within 0.16 s on retrieval p50 and 0.7 s on TTFT p50. B's run 4b is slower than 2b (retrieval +0.3 s, TTFT +1.1 s). Three of 4b's questions (vit-cry-006, lan-hlt-003, saf-004) had a 1.3–1.5 s stall in the native **query embedding** (normally 10–40 ms, every other question in every run). This is not touched by the patch: retrieval minus embedding is 1.29–1.67 s for 4b's model items, the same band as 2b. Pooled retrieval minus embedding for the model items: A 5.01 s → B 1.39 s (-3.62 s).
- The phone warmed across the session (battery 27.3 → 28.4 → 30.5 → 32.8 C at the gates of 1a, 2b, 3a, 4b; status 0 throughout, no cooling waits). The B runs sat later in each pair, which fits their slower prefill (+0.2 s pooled) and decode (-1.1 tok/s). The patch does not touch the model, so this is thermal order, and it makes the measured TTFT and total gains slightly conservative.
- n is small: 7 model items and 2 cards per run, 2 runs per arm. The effect (-3.5 s on a 9.1 s TTFT, every model item faster on retrieval and on TTFT when its two B runs are paired with its two A runs) is far outside LITELAT's 5 % TTFT noise band.
- A's numbers reproduce the LITELAT baseline (retrieval 5.3 → 5.0 s, TTFT 9.4 → 9.1 s, pack SQL 435 calls per model question and 665 per card).
- The measured gain is the bench app's TypeScript engine on expo-sqlite. The native Kotlin engine's SQLite calls are synchronous JNI calls with a much smaller per-call cost, so the port's gain there is not this number (see handoff/batchret-2026-10-20/PORT-NOTE.md).

## Files
- phone/run_ab.sh (driver: install -r, thermal gate, boar_bench.py run), phone/run_ab.log (+ run_ab.attempt0-uppercase-id.log: a first attempt with uppercase request ids that the app rejected as invalid; no question ran), phone/thermal_gate.py, phone/thermal.jsonl.
- phone/requests/batchret-{1a,2b,3a,4b}.request.json (litelat-9, identical apart from requestId).
- phone/compare_ab.py (uses ../litelat/analyze.py) → phone/compare_ab.json (per run, pooled, paired, identity, per question).
- phone/runs/batchret-*.rows.jsonl + .bench.json.gz. Full results: handoff/pixel8-2026-10-20/bench/results/batchret-*.
- phone/cut7-cmp30off-batchret.vs-0cfd4a77.patch (+ .sha256).

State left: the B APK is installed and the app is in front on the live log.
