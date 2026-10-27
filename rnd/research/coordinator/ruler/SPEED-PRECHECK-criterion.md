# SPEED-PRECHECK criterion (RJ5-SPEEDPRECHECK step 1; frozen 2026-10-21 before computing)

Scope: 0 LLM, 0 judge, 0 generation, 0 paid, no phone access. Inputs = existing Pixel 8a (8 GB, Tensor G3) BOAR Bench traces on disk. Output = the ruler's speed row (RULER-SPEC-v1 §7.2, BENCH-RULER §1 B31:28), labelled PROJECTED FROM BENCH-APP TRACES, never the verdict run (the verdict run is the RC APK, PLAN 0.2 / RJ5 step 2).

## Unit and classes
- Unit = one row of rows.jsonl. warmup-000 is dropped from every statistic (not a v0.1 item). v0.1 has no multi-turn items, so per-turn = per-row.
- Declined row: declined == true (refusal, z > 0). Excluded from the answered set; its wallMs is reported as refusal latency.
- Deterministic row: tokensGenerated == 0 and not declined (facts, calculator, places, extractive, grounding-guard answers).
- LLM row: tokensGenerated > 0 and not declined.
- deterministic-v01.ids (ruler/ids, 31 ids incl. warm-up) defines the "without deterministic items" set by id (skip list), independent of the per-run class.

## Metrics per row
- TTFT = firstTokenMs (LLM rows); = wallMs for deterministic and declined-without-tokens rows.
- T30 (time to the 30th generated token, or to the deterministic answer). The traces have no per-token timestamps (timeline holds firstTokenAt/lastTokenAt only), so T30 is DERIVED and flagged:
  - tokensGenerated >= 30: T30 = firstTokenMs + 29 x 1000 / tokPerSec (the row's decode rate; if tokPerSec <= 0, the run's median completion decode rate).
  - 0 < tokensGenerated < 30: T30 = wallMs (the whole answer is shorter than 30 tokens).
  - deterministic: T30 = wallMs.
  - Warning lines are app text, not generated tokens; the derivation counts model tokens only.
  - Sanity check printed: median |firstTokenMs + (tokens - 1) x 1000 / tokPerSec - totalLatencyMs| over LLM rows.
- Complete = wallMs.
- Decode tok/s = median of predictedN / (predictedMs / 1000) over bench.json completions with predictedN >= 1 (all completions, incl. no-callback ones). Prefill tok/s = median promptPerSecond, same filter.
- Thermal at start = first telemetry.csv row (thermal_status, battery_temp_dC / 10). PSS peak = max app_pss_kb in telemetry.csv.
- Percentiles: numpy linear interpolation (default method). Seconds, 1 decimal.

## Sets per run
- S1 answered (not declined), all classes = the VERDICT set (spec: answered items only, deterministic answers are answers).
- S2 answered, ids not in deterministic-v01.ids (model-path questions).
- S3 all rows (declines at their wallMs).
- S4 declined rows only (refusal latency).
Sensitivity: share of S1 complete <= 60 s (speed-qualified U basis).

## Thresholds (RULER-SPEC-v1 §7.2, verbatim, our choice)
USABLE iff p50 T30 <= 30 s AND p90 T30 <= 60 s AND p50 complete <= 60 s, over S1.

## Tiers and runs (Pixel 8a only)
| tier | primary (verdict) run | secondary runs (reported, not used for the verdict) |
|---|---|---|
| 1.7B + A-union (headline config: arm A-union, default tier) | arms/aunion-pixel/aunion73-a | aunion10-a |
| 1.7B claim kit | arms/gemma4-e2b/phone/q17b73-a | q17b10-a; handoff batchret-1a/2b/3a/4b (litelat-9); cmp30-q17, cmp30off-q17 (31) |
| Gemma 4 E2B | arms/gemma4-e2b/phone/gemma73-a | gemma10-b |
| 4B (Qwen3-4B-Instruct-2507) | handoff final-cut7-v01 | final-a-cut7, live-4b-final2 (9 each) |
Excluded: gemmaa73-a (running now, incomplete), gemma10-a/-thinking-on (non-default thinking), live-17b-final2 (diagnostic). Engine tree per run is printed; the 4B primary is cut 7 (7c96e59e, before BATCHRET), so a sensitivity row subtracts the BATCHRET paired median TTFT gain (3.494 s) from T30 and complete of 4B LLM rows; the verdict uses the unadjusted numbers.

## Verdict rules
- Per tier: USABLE / NOT USABLE on the primary run's S1, labelled PROJECTED.
- RJ5 step-1 prediction holds iff 1.7B + A-union and 1.7B claim kit are USABLE AND the 4B fails at least one threshold. If the 4B passes all three on the traces, the report says the "latency constraint" rationale for the 1.7B default is not supported by the trace projection (final call stays with the RC run, per RJ5 kill criterion).
- Missing rows named in the report: 1B no-RAG arm (B31:9 anchor), native APK (maintainer RC) rows, reference arm end-to-end time.
