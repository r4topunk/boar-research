# Offline Research Bench v0: device metrics block

Owner of this folder: Kiln (R&D) · Bench owner: Lantern (`rnd/bench/`) · Date: 2026-09-30 · Schema version **0.1.0**.

## TL;DR

- **[`device-metrics.schema.json`](device-metrics.schema.json)** (JSON Schema 2020-12) is one file per *system configuration*: app build + model + device + question set. It covers:
  - TTFT p50/p95 at the RAG context length;
  - TPS, prefill tok/s and total time;
  - peak RSS and peak anonymous memory;
  - sustained-session drift (throttling);
  - device / SoC / RAM / OS, build and model;
  - the APK offline proof.

  `score.py` (day 3) reads it.
- **Latency uses the MLPerf Client v2.0 definitions** ([mlcommons.org/benchmarks/client](https://mlcommons.org/benchmarks/client/)):
  - TTFT = *"the wait time in seconds before the system produces the first token in response to each prompt"*;
  - TPS = *"the average rate to produce all of the rest of the tokens in the response, excluding the first one"*.

  Because an offline research app also retrieves before it prompts, the schema keeps **three TTFTs**, each defined in §1.
- **Converters** (stdlib Python; they need no network):
  - [`from_kiln_harness.py`](from_kiln_harness.py) reads Kiln's exp-01/02 runs (Mac mini, marked **`proxy`**).
  - [`from_eval_iphone.py`](from_eval_iphone.py) reads BOAR's in-app benchmark rows (Plumb's iPhone runs, **`device`**).
  - **All 8 examples in [`examples/`](examples/) validate** (`validate.py`, full JSON Schema check).
- **Proxy configuration:** [`proxy-capture-config.json`](proxy-capture-config.json) records how the Mac-mini proxies were set up, with sha256 for every pack, place file, capture and model. The proxies are scored as configured: no vital5, and places only for world + Berlin, so food-002/006 are declined for lack of coverage. It also lists the 4 missing proxy answers (Ling and Maple on trv-002/004).
- **Third-party template:** [`template.device-metrics.json`](template.device-metrics.json), all nulls; it validates.
- **First real finding from the block:** in the two 52-question iPhone sessions, decode speed drops to **0.58× and 0.65×** from the first 5 to the last 5 answers (app tok/s ~20 → ~12–13 over 8–9 min). The 38-question session stays at 0.98×. That is **throttling suspected** (threshold < 0.8). The rows carry no thermal state, so this is UNKNOWN until a run records it (§4).
- **Third parties (a competitor team, a competitor team)** can fill it without our API, using `adb` plus their own exports (§4). a competitor team already measures TTFT the same way as `ttft_e2e_ms`. **a competitor team's `ttftS` includes model load, so it is not MLPerf TTFT** and must set `includes_model_load: true`.

## 1. Definitions (what each field means)

| Field | Definition | Why |
|---|---|---|
| `latency.ttft_model_ms` | **MLPerf TTFT at engine level:** prompt submitted to the engine → first generated token of *any* kind (reasoning included). Excludes model load and retrieval | Comparable with MLPerf Client and llama-bench-style numbers |
| `latency.ttft_answer_ms` | Prompt submitted → first token of the *visible answer* | Reasoning models (Maple: 2.7 s to the first token, 4.8 s to the first answer word) |
| `latency.ttft_e2e_ms` | Question sent in the app → first visible answer text (retrieval + routing + prefill) | What the user waits. This is what a competitor team measures |
| `latency.tps` | MLPerf TPS: (tokens − 1) / (last-token time − first-token time), per answer | Excludes the first token by definition |
| `latency.tps_engine_reported` | The engine's or app's own decode rate (llama.cpp `predicted_per_second`, BOAR `tokPerSec`) | Traceability, and the fallback when the last-token time is not recorded |
| `latency.prefill_tps` | Prompt tokens processed / prompt time | Prefill dominates TTFT on phones |
| `workload.context_tokens` | Prompt tokens per answer | **TTFT is only comparable at similar context length.** MLPerf reports per prompt category (~128 to ~7,631 input tokens); RAG answers here sit around 400–630 |
| `memory.peak_anon_bytes` | Anonymous memory: macOS peak footprint / Android private dirty (PSS as an upper bound) / iOS `phys_footprint` | What the low-memory killer and jetsam count. `peak_rss_bytes` also counts clean mmap'd weights |
| `sustained.tps_ratio_last_first` | Median TPS of the last 5 LLM answers / first 5, in session order | < 0.8 means throttling suspected. Record `thermal_status_*` to confirm |
| `offline_proof.status` | Verdict of `scripts/audit-apk.py` (boar-app PR #42) on the exact APK, plus kernel per-UID traffic (`scripts/netstats-uid.sh`) | The "offline" claim, checkable by anyone |

Rules:
- **Unmeasured → `null` with a reason in `measurement.notes`, never 0.**
- **Proxy numbers are never ranked against device numbers.**
- Answers served without the LLM (calculator, places list, health excerpt) are excluded from every latency statistic (`workload.n_llm_answers`).

## 2. Examples (all validate)

| File | Kind | Model | n LLM | ctx p50 | TTFT model p50 | TTFT e2e p50 | TPS p50 | prefill p50 | peak anon | TPS last/first |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `proxy-macmini-qwen2.5-1.5b.json` | proxy | Qwen2.5-1.5B | 56 | 612 | 2.7 s | — | 58.2 | 226 | 1.15 GiB | 1.17 |
| `proxy-macmini-qwen3-4b.json` | proxy | Qwen3-4B | 56 | 612 | 7.7 s | — | 22.2 | 81 | 3.03 GiB | 1.09 |
| `proxy-macmini-qwen3-4b-b11010.json` | proxy | Qwen3-4B (b11010) | 56 | 612 | 7.5 s | — | 22.5 | 82 | 3.03 GiB | 1.06 |
| `proxy-macmini-ling-3.0-tiny.json` | proxy | Ling-3.0-tiny | 56 | 629 | 4.1 s | — | 59.3 | 157 | 4.58 GiB | 0.95 |
| `proxy-macmini-maple-preview.json` | proxy | Maple-Preview (reasoning) | 56 | ~610 | 2.7 s (answer: 4.8 s) | — | 79.0 | 232 | 0.50 GiB | 1.39 |
| `device-iphone13-qwen2.5-1.5b-run1-factual.json` | device | Qwen2.5-1.5B | 31/38 | 416 | 4.7 s | 5.6 s | null¹ | ≤ upper bound² | null³ | 0.98 |
| `device-iphone13-qwen2.5-1.5b-run2-device.json` | device | Qwen2.5-1.5B | 40/52 | 400 | 5.2 s | 6.3 s | null¹ | ² | null³ | **0.58** |
| `device-iphone13-qwen2.5-1.5b-run3-device-vital5.json` | device | Qwen2.5-1.5B | 44/52 | 415 | 5.6 s | 6.9 s | null¹ | ² | null³ | **0.65** |

Notes on the iPhone rows:
- ¹ The rows do not record the last-token time, and `receipt.totalMs` includes post-generation work (citation gate), so MLPerf TPS is left null. My first attempt from `totalMs` gave 3.8 tok/s against the app's 12.5, which is wrong. `tps_engine_reported` (the app's tok/s, p50 13.8–15.6) is filled in instead, and the sustained ratios use it.
- ² `ctxTokens / prefillMs` is an upper bound, because llama.rn reuses the KV prefix.
- **TTFT derivation (fixed 2026-09-30 after Lantern flagged `ttft_model_ms.min = -2.3 ms`):**
  - The app's `receipt.ttftMs` is the first visible text of *any* tier. On 29 rows that was the instant snippet (`instant:preview`), shown when the prefill starts.
  - The converter now uses the stages: `ttft_model_ms = generating − prefill` and `ttft_e2e_ms = generating` (first **model** token). The app's value is kept per query as `first_visible_ms`.
  - p50 moved from 3.1–4.0 s to **4.7–5.6 s** (model) and from 4.0–5.3 s to **5.6–6.9 s** (e2e).
  - **So the "TTFT ≤ 5 s" in `review/research-pipeline/06` measured the first visible snippet, not the model's answer.**
- ³ The in-app benchmark does not record memory.
- The TTFT last/first ratio (~0.1–0.2) is **not** a thermal signal: the first answers of a session pay cold start and warm-up.
- The proxies' "last/first" > 1 is host-load noise on a shared Mac mini, not a speedup.

Reproduce:

```bash
cd rnd/bench/device
python3 from_kiln_harness.py --model qwen3-4b --runs ../../kiln/exp-01-inram-moe-reader/runs/qwen3-4b.jsonl \
  --mem-meta ../../kiln/exp-01-inram-moe-reader/runs-mem/qwen3-4b.jsonl.meta.json --out examples/proxy-macmini-qwen3-4b.json
python3 from_eval_iphone.py --rows ../../plumb/data/qwen2.5-1.5b-instruct-q4km__iphone-14de107-device-vital5.jsonl \
  --build 14de107 --question-set vitalik-lantern-device-52 --os "iOS 26.6.2" --out examples/device-iphone13-qwen2.5-1.5b-run3-device-vital5.json
python3 validate.py examples/*.json        # full check needs: pip install jsonschema
```

## 3. What BOAR's own runs still do not record (fix in the in-app benchmark, owner: eval session)

| Missing | Why it matters | Cheapest fix |
|---|---|---|
| Last-token timestamp | MLPerf TPS | Add `lastTokenMs` to the receipt |
| Peak memory | Memory block | Android: poll `dumpsys meminfo team.sopa.aoair` from the host during the run. iOS: `os_proc_available_memory` + `task_info` `phys_footprint` into the receipt |
| Thermal state | Confirms the 0.58–0.65 decode drop | Android `dumpsys thermalservice` / `dumpsys battery` (temperature, tenths of °C) at start and end. iOS `ProcessInfo.thermalState` per answer |
| OS version, threads, n_ctx | Reproducibility | Echo them into the run header |

## 4. How a third party (a competitor team, a competitor team) fills this without our API

They need their own app, a USB cable and `adb`; there is no BOAR code on the phone. Start from [`template.device-metrics.json`](template.device-metrics.json), leave what they cannot measure as `null`, and run `validate.py`.

| Block | How, without our API | a competitor team (local clone 706ccbb) | a competitor team (local clone 4988848) |
|---|---|---|---|
| `device` | `adb shell getprop ro.product.model ro.soc.model ro.build.version.release ro.build.fingerprint`; `adb shell grep MemTotal /proc/meminfo` | same | same. Its own `docs/device-testing.md` already asks for these |
| `system.apk_sha256` | `sha256sum app.apk` | release APK | release APK |
| `latency` | **App export first, then logcat, then screen recording** | Per-token CSV via "Share metrics" (`MetricsCsv.kt`, `shareCsv`), plus `Telemetry.prefillTps` and `ttftS`. **`ttftS` = model load + prefill** (`Telemetry.kt:51`), so set `includes_model_load: true`, or subtract the load time. `ttft_model_ms` = prefill time; TPS from the per-token `wall_ms` (MLPerf-compatible: skip token 1) | `ResearchMetrics.timeToFirstTokenMillis` counts from question start (`ResearchOrchestrator.kt:127-143`), which is exactly **`ttft_e2e_ms`**; also `retrievalMillis`, `totalMillis`, `generatedTokenCount`. It is shown on screen ("First word …"), and its `device_acceptance.sh` diagnostics JSON is the export path |
| `latency` fallback | Apps built on llama.cpp can log `llama_perf_context_print` (prompt eval / eval times). Read them with `adb logcat -d`. **Last resort:** a 60 fps screen recording of each answer, with TTFT = the frame of the first visible word (±17 ms), marked `method: "screen-recording"` | — | — |
| `memory` | Poll every 0.5 s during the session: `adb shell dumpsys meminfo <pkg>` → `TOTAL PSS` (peak_pss_bytes) and `Private Dirty` (peak_anon_bytes). LMK kills: `adb logcat -b events -d \| grep am_kill` | same | same |
| `sustained` | Run ≥ 20 questions back to back in one session. At the start and the end, run `adb shell dumpsys thermalservice` (Thermal Status) and `adb shell dumpsys battery` (temperature, level) | same | same |
| `offline_proof` | `scripts/audit-apk.py <apk>` from boar-app PR #42 (python3 + aapt2, works on any APK) and `scripts/netstats-uid.sh <pkg>` over adb | PR #42 reports it ran on a competitor team 1.0.0 → `NETWORK-CAPABLE`, and says why | a competitor team 1.1.10 was also audited in PR #42 |
| `workload.context_tokens` | From the app's prompt log if it has one. Otherwise `null` with a note, and latency is then comparable only within the app | CSV has prompt tokens | UI shows prefill "x/y tokens read" (`LlamaInferenceGateway.kt:35`) |

**Minimum acceptable third-party submission:**
- `device`;
- `system.model`;
- `latency.ttft_e2e_ms` (or `ttft_model_ms`), `latency.tps` or `tps_engine_reported`, with n ≥ 20 answers;
- `memory.peak_pss_bytes`;
- `sustained` start and end thermal status;
- `offline_proof`.

Everything else may be `null`.

## Decisions / Options / Tasks

**Decisions (Kiln, reversible)**
- MLPerf Client v2.0 definitions, plus two BOAR-specific TTFTs (answer, e2e). Proxy vs device is an explicit field.
- Unmeasured means `null` with a note; there is no imputation.

**Options**
- O1. Add a `energy` block (battery % per 10 answers). The schema has `battery_pct_drop` only, because no current run records it.
- O2. Per-context-length buckets (MLPerf-style categories), once the bench has long-context items.

**Tasks**
- [x] Schema, 2 converters, validator, 8 validated examples.
- [ ] Eval session: add `lastTokenMs`, memory and thermal state to the in-app benchmark receipt (§3).
- [ ] Lantern: wire `score.py` to read `latency.ttft_*`, `tps|tps_engine_reported`, `memory.peak_anon_bytes`, `sustained.tps_ratio_last_first` and `offline_proof.status`.

## UNKNOWN

- The iPhone thermal state during runs 2/3. The decode drop could also come from question mix (answer length did not grow: median tokens by thirds 40/51/42 and 57/45/37).
- Whether a competitor team's CSV has a per-answer prompt token count (not checked field by field).
- MLPerf Client's aggregation across prompt categories (the page does not state geometric vs arithmetic mean; 8K prompts are reported separately).

**Metric:** 8 of 8 converted runs validate, covering 2 kinds (proxy, device) and 5 models.
**Next step:** Lantern's `score.py` reads `examples/*.json` on day 3–4.
