# GEMMA4-PHONE: Gemma 4 E2B on the Pixel 8a (2026-10-21 02:0x, r4to watching, same-session A/B)

Measured, not projected. Pixel 8a (GrapheneOS, 7.15 GiB), airplane mode, Wi-Fi off, BOAR Bench in front, USB power, thermal status 0 at each gate (battery 28.7 C -> 31.1 C -> 31.6 C -> 32.7 C). Set gemma-10 = litelat-9 (7 v0.1 dev items that reach the model + 2 safety cards) + lan-ref-001 (Wikidata table). Order: Gemma then 1.7B, cold start each. 0 judge calls, 0 paid.

Build: bench-app incremental gradle (Homebrew openjdk@17, existing nonet android/), engine tree unchanged (0ca54d87 = cut7-cmp30off-batchret); catalog entry gemma-4-e2b-it-q4km (unsloth Q4_K_M, sha 740185b2, 3.11 GB) in src/benchModels.ts.
- APK gemma (sha 187c6842): entry without the thinking shim -> the model THOUGHT on the phone (`<|channel>thought Thinking Process: ...`), 3 answers at 42 s each (n_predict cap), TTFT 12-14 s. llama.rn/llama.cpp applies the Gemma 4 template with enable_thinking on by default; the mini runs used llama-server --reasoning off. Rows kept in gemma10-a-thinking-on/.
- APK gemma2 (sha 284abdde): thinkingOff: true (enable_thinking:false, same shim as Qwen3-1.7B) -> 0 thinking markers in 10/10.

| run | model | TTFT p50 | answer p50 | total 10 q | prefill tok/s | decode tok/s | PSS peak | llm init |
|---|---|---|---|---|---|---|---|---|
| gemma10-b | Gemma 4 E2B Q4_K_M | 7.2 s | 12.6 s | 98 s | 46.4 | 10.5 | 4.63 GB | 2.8 s |
| q17b10-a | Qwen3-1.7B Q4_K_M | 4.9 s | 8.3 s | 67 s | 81.8 | 13.9 | 3.25 GB | 1.6 s |
| (10-20 batchret-2b/4b) | Qwen3-1.7B | 4.9-5.6 s | 7.7-9.2 s | | 70-84 | 12-15 | | |
| (10-20 T1) | Qwen3-4B | 14-21 s | 29-46 s | | | 3.6-6 | 4.92 GB, 1 LMK kill | |

Per item (7 model items): Gemma TTFT 4.3-12.5 s vs 1.7B 3.2-7.8 s; answers 7-17 s vs 4.5-12 s. Prompt n p50 274 both (same engine, same retrieval). Deterministic items (CO card, burn card, Wikidata) identical text and time.
Answers (read, not judged): the 1.7B refused 4/7 ("The passages found don't support this answer."), Gemma refused 1/7 and answered Montenegro, quadratic funding and mosquito items with [n] citations; the 2 items both answered (Sahara, Hundred Years' War) are equivalent. Consistent with the desktop CONFIRM reading (gain = fewer refusals).

Reading: Gemma 4 E2B is 1.4-1.6x the 1.7B in time on this phone and 3x faster than the 4B; no LMK kill in this 2-minute run, but PSS 4.63 GB sits above the 4.4 GB at which the 4B was killed once (10-20); the per-layer-embedding pages are the unknown. Longer run (73 items) and the Q3_K_M fallback (N2) are the next phone steps; the model is NOT in the app maintainer's catalog yet (NATIVE-SUPPORT.md: one catalog.json entry).
Files: gemma10-b/, q17b10-a/, gemma10-a-thinking-on/ (rows, bench.json, telemetry.csv, device.json), requests; APKs bench-app/build/boar-bench-0cfd4a77-cut7-cmp30off-batchret-nonet-gemma{,2}-0ca54d870ba8.apk; bench-app commit pending (src/benchModels.ts + kits/gemma-4-e2b.kit.txt + requests).

## gemma73-a: the 73-question set (final-3-bench = 1 warm-up + 72 v0.1 dev items), 02:07-02:20
| run | model | rows | answer p50 / p90 | total | TTFT p50 | LLM calls | prefill / decode tok/s | PSS peak / end | battery | thermal status max |
|---|---|---|---|---|---|---|---|---|---|---|
| gemma73-a | Gemma 4 E2B Q4_K_M | 73/73, 0 errors | 11.8 s / 24.3 s | 13.0 min | 5.5 s | 55 | 34.1 / 7.0 | 4.52 / 3.64 GB | 33.0 -> 36.4 C | 1 |
| final-cut7-v01 (10-20) | Qwen3-4B Q4_K_M | 73/73 (after a reboot; 1 LMK kill before) | 25.5 s | | | | / 4.2 | 4.92 GB | | |
Thinking markers 0/73; refusal-like answers 3/73 (text match); no LMK kill over 13 minutes at PSS 4.5 GB. Decode fell from 10.5 (10-question run, status 0) to 7.0 tok/s median over the long run with thermal status 1 from mid-run: the phone throttles the E2B sooner than the 1.7B (the 1.7B 73-run on this phone is not in this folder; the 10-question same-session A/B above is the paired speed number). Gemma is ~2.2x faster than the 4B on the same 73 on the same phone.
Quality on the phone: not judged here; the 57 device-parity ids are judged in GEMMA4-PHONE-JUDGE.md (frozen reading rule, Haiku N=4) against the 4B phone run and the desktop Gemma stage-2 traces.

## q17b73-a: the same 73 with Qwen3-1.7B, same session (04:1x, thermal status 0 at the gate, battery 26.2 C)
| run | model | rows | answer p50 / p90 | total | TTFT p50 | LLM calls | prefill / decode tok/s | PSS peak | battery | thermal max |
|---|---|---|---|---|---|---|---|---|---|---|
| q17b73-a | Qwen3-1.7B Q4_K_M | 73/73, 0 errors | 4.2 s / 12.2 s | 6.7 min | 2.9 s | 38 | 80.2 / 12.4 | 3.39 GB | 26.2 -> 34.1 C | 0 |
| gemma73-a | Gemma 4 E2B Q4_K_M | 73/73, 0 errors | 11.8 s / 24.3 s | 13.0 min | 5.5 s | 55 | 34.1 / 7.0 | 4.52 GB | 33.0 -> 36.4 C | 1 |
Paired sustained numbers on the same phone and set: Gemma is 2.8x the 1.7B in answer p50 and 1.9x in total time; the 1.7B made 38 LLM calls to Gemma's 55 (its compact declines and deterministic paths skip generation more often, so part of its speed is answering fewer items with the model); the 1.7B never left thermal status 0. Decode 12.4 vs 7.0 tok/s sustained; PSS 3.39 vs 4.52 GB. The 1.7B ran second and cooler (start 26 C vs 33 C); order favours the 1.7B slightly.
