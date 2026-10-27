# LITELAT: engine-side settings that cut Qwen3-1.7B TTFT and total time on a Pixel 8a (frozen 2026-10-20 12:3x, main)

## Tags
Tags: probe (device latency; no judge, no LLM calls, 0 paid)
Ruleset: 30

## Question
Where do the seconds go before and during a Qwen3-1.7B answer on a real 8 GB phone (Pixel 8a, GrapheneOS, Tensor G3), and which engine-side settings that exist as bench overrides (no engine source change) cut time-to-first-token (TTFT) and total time without changing answer quality?

## Fixed inputs
- Build: BOAR Bench live-view + LITELAT observer taps, APK build/boar-bench-0cfd4a77-cut7-nonet-litelat-7c96e59e001b.apk (sha256 f97f74a5ffb707bb81461cf4854d58e8e62ddabec0003b799f69d99347b94e00), engine tree 7c96e59e (cut 7), same package/key, files/ kept. Taps time calls only (sqliteTap, embedShim, packsTap, answerDepsTap, seedTap, llamaRnShim spans); engine source unchanged.
- Kit on the phone: claim kit (corpus boar-crypto + boar-wikivoyage-en, embedding.gguf, emergency detector), model qwen3-1.7b-q4km (thinking off via bench catalog).
- Question set litelat-9 (public dev, 9 items, fixed order): vit-hum-004, vit-cry-001, lan-exp-005, lan-exp-002, vit-cry-006, lan-hlt-003, lan-rsn-006 (bench v0.1 dev; reach the model) + probe-co-alarm (final-2-cut7 probe) and saf-004 (v0.1 dev) (retrieval-wait cards, no model). Requests: arms/litelat/requests/litelat-*.request.json.
- Runner: handoff/pixel8-2026-10-20/bench/boar_bench.py run <request> (force-stop, cold app start, 9 questions); airplane mode on, Wi-Fi off, app in front (r4to watches live).
- Thermal gate before every run: arms/litelat/thermal_gate.py (thermal status 0 and battery <= 34.0 C; logged in thermal.jsonl).
- Analysis: arms/litelat/analyze.py (stage spans per question; medians over the 7 model items and the 2 card items).

## Runs (max 8, each 9 questions)
| run | requestId | engineOverrides (LlamaEngine generation context only unless noted) |
|---|---|---|
| R0 | litelat-00-base | none (engine defaults: n_threads 4, flash_attn auto, KV f16, mmap, no mlock); already run before this freeze (breakdown only) |
| C1 | litelat-01-fa-off | flashAttn "off" |
| C2 | litelat-02-kvq8 | cacheTypeK "q8_0", cacheTypeV "q8_0" (flash_attn default) |
| C3 | litelat-03-t5 | nThreads 5 (Android set_best_cores: X3 + 4 A715) |
| C4 | litelat-04-t6 | nThreads 6 |
| C5 | litelat-05-mlock | useMlock true |
| C6 | litelat-06-combo | only if >= 2 of C1..C5 reach LEAD or ADOPT and are compatible: their union; else not run |
| R1 | litelat-07-base-repeat | none (same as R0; noise band), always last |
Not run as overrides (no override exists without engine source changes; estimated from R0 spans in the report instead): embedding threads (embed = 13 ms median in R0, nothing to gain), safety card before retrieval, smaller kept context, model preload at app start, retrieval caching. nBatch/nUBatch not run: every answer prompt (< 500 tokens) fits one 512 ubatch.

## Metrics
Per run, over the 7 model items: TTFT p50 (row ttftMs), total p50 (row totalLatencyMs), prefill tok/s p50 (promptN / prompt_ms of the answer completion), decode tok/s p50 (row tokPerSec), first-item model load (llm-init ms). Over the 2 card items: TTFT p50 (control: LLM overrides should not move it).
Noise band per metric: |R1 - R0| / R0 (relative), floor 5 %.

## Adoption rule (each candidate vs R0, same session)
ADOPT (recommend as engine default) iff all:
 (a) TTFT p50 (7 model items) <= -20 % vs R0 and the change exceeds the noise band;
 (b) total p50 not worse than R0 by more than the noise band;
 (c) quality: answers byte-identical to R0, or, where texts differ (device sampling is not deterministic: A15 sweep 01 vs 08), no new decline, error, timeout or truncated/garbled answer on visual check, plus the note "desktop judged check needed before shipping".
LEAD (not adopted; recorded for an engine change or a combo): prefill tok/s p50 >= +15 % or decode tok/s p50 >= +10 % vs R0, beyond the noise band, with total p50 not worse by more than the noise band and (c) holding.
NO: otherwise. LOSS: TTFT p50 or total p50 worse than R0 beyond the noise band.
A candidate whose init fails (llamaInits error or CPU fallback) is NO (recorded).

## Expectation (before running)
R0 shows retrieval ~5.2 s and prefill ~3.3 s of a ~9.2 s TTFT p50; overrides only touch prefill/decode, so ADOPT (TTFT -20 %) needs prefill -55 %: unlikely. Expected outcome: at most LEADs; the TTFT lever is retrieval (engine change), reported with R0 numbers.
