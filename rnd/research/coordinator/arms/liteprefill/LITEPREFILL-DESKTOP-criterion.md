# LITEPREFILL-DESKTOP: prefill and decode rate ratio Qwen3-1.7B vs Qwen3-4B on a phone-like CPU budget (frozen 2026-10-16 17:2x, coordinator)

## Tags
Tags: probe
Ruleset: 30

## Question
LITE-PREFILL (BACKLOG row 15) is blocked by the device. Desktop proxy, 0 calls: on the MacBook CPU-only build of llama.cpp b11010, 4 threads, same prompts, what is the ratio of prompt-processing tok/s and decode tok/s of Qwen3-1.7B Q4_K_M to Qwen3-4B-Instruct-2507 Q4_K_M? Used for: replacing the assumed ">= 1.5x" prefill rate of the lite tier in the X2b TTFT projection (4B phone prefill 47.6 tok/s -> +413 tokens = +8.7 s; lite = 8.7 / ratio). Measurement only; not a score lever.

## Fixed inputs
- Binary: llama-server b11010 CPU build on the MacBook (no Metal; -t 4 -c 4096 --no-warmup off; -np 1).
- Models: shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf, shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf (sha256 b139949c…, catalog entry qwen3-1.7b-q4km).
- Prompts: 5 synthetic English prompts of ~450 and ~850 tokens cut from BOUNTY_31.md (public text), identical for both models; n_predict 64, temperature 0; server timings (prompt_n, prompt_ms, predicted_n, predicted_ms) are the measurement.
- Idle rule: the run starts only when the 1-min load average < 4.0 (poll up to 45 min; else record 'not run (load)').

## Power
expected_delta: n/a (ratio measurement; prior >= 1.5x from parameter count 1.7/4.0 = 2.35x ideal)
n: 5 prompts x 2 lengths x 2 models
seeds: 1
mde: n/a
slice: n/a
l1_futility: n/a (probe)
reopen: n/a
split: none

## Ceiling (RULE 29; 0 calls, before the freeze)
ceiling: n/a (latency measurement)
bar_ceiling: n/a
launch: probe (<= 30 min wall, 0 calls)
transfer: desktop CPU ratio -> phone: indicative only; the X6 run decides

## Budget (RULE 29)
wall_cap: 1 h on the MacBook (including the load wait)
calls_cap: Haiku 0 / Opus 0; 0 paid
smoke: first prompt per model (load ok, timings present)
kill_if: load >= 4.0 for 45 min; a server fails /health within 120 s; disk free < 5 GiB
checkpoint: first prompt of the 1.7B
subset_step0: n/a

## Precheck
token_projection: n/a / token_budget: n/a
disk_peak_gib: 0.01
off_baseline: n/a
call_pattern: 0 calls
lane: mac-cpu
opus_clause: none
wall_cap_h: 1
parallelism: 1
run_type: latency

## Stages and rules
1. Wait for load < 4.0; record load, free disk, other engines (the :8094 detector may stay up).
2. Per model: start the server on :8181, /health, run the 10 prompts sequentially, read timings, stop the server.
3. Report: table model x length -> median pp tok/s, median tg tok/s; ratios 1.7B/4B; projected X2b TTFT on the POCO = 413 / (47.6 x pp_ratio) s; verdict = the measured ratio (no pass/fail; 'not run (load)' if the idle rule never held).
