# LESPORT S0: is OpenBMB llama.cpp-omni's expert streaming (LES) usable for our Qwen3.6-35B-A3B deep tier? (frozen 2026-10-16 17:1x, coordinator)

## Tags
Tags: probe
Ruleset: 30

## Question
Step 0 of LESPORT (BACKLOG row 10). (a) Does the OpenBMB fork (github.com/OpenBMB/llama.cpp-omni, branch ios-omni or its default) build on the mini and load a stock qwen3_5_moe / qwen3_6 GGUF (our Qwen3.6-35B-A3B UD-Q2_K_XL) with expert streaming enabled, or is the scheduler tied to MiniCPM-V 4.7's own graph / a trained predictor? (b) If it loads: greedy 128-token outputs on the 10 DEEPPAR prompts vs the stock b11010 CPU build (text identical count), decode tok/s, prefill s, peak RSS with the expert cache capped (target <= 4 GiB) vs uncapped, vs the bmoe v0.28.0 K0 numbers in arms/deepspeed/DEEPSPEED.md (8.69 tok/s, 10.25 GiB footprint). Used for: the device plan of the deep tier (supersede LAZYEXP/IQKPORT or close LESPORT). Mechanism seen / not seen only; no score claim.

## Fixed inputs
- Model: <runner>/shared-models/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf on the mini (sha256 verified before the run, logged in S0.md).
- Control: <runner>/spikes/llama-b11010/build-cpu/bin (llama-cli / llama-bench, CPU, -t 4), same prompts, greedy, -n 128, -c 4096.
- Prompts: the 10 DEEPPAR rendered prompts (arms/deeppar/raw/, as used by arms/deepspeed/tools/run_deepspeed.py); no blind material.
- Fork: clone into <runner>/spikes/llama-omni (new empty dir), commit sha logged; build with cmake, CPU only; no model download; nothing uploaded.

## Power
expected_delta: n/a (mechanism probe, 0 judge calls; no score)
n: 10 prompts
seeds: 1 (greedy)
mde: n/a
slice: n/a
l1_futility: n/a (probe)
reopen: n/a
split: none

## Ceiling (RULE 29; 0 calls, before the freeze)
ceiling: n/a (latency/memory lever, not a bar lever; the published claim is 35B-A3B at ~3 GiB RSS and 13+ tok/s on an iPhone 17 Pro Max)
bar_ceiling: n/a
launch: probe (<= 2 mini-h, 0 judge calls)
transfer: n/a

## Budget (RULE 29)
wall_cap: 2 h on the mini (build <= 30 min, runs <= 60 min)
calls_cap: Haiku 0 / Opus 0; 0 paid
smoke: first prompt on both binaries (load ok, 128 tokens, s/item); projected wall = s/item x 10 x 2 binaries x 2 cache settings
kill_if: fork does not build in 30 min; model does not load (record the error = 'not seen'); disk free < 25 GiB; swap used > 8 GB; any other engine running on the mini
checkpoint: after the first prompt on the fork (load + first 128 tokens)
subset_step0: n/a

## Precheck
token_projection: n/a / token_budget: n/a
disk_peak_gib: 2 (clone + build; model already on disk)
off_baseline: n/a (identity measured against the b11010 CPU build run in this arm)
call_pattern: 0 calls
lane: mini-long
opus_clause: none
wall_cap_h: 2
parallelism: 1
run_type: latency

## Stages and rules
1. Build the fork (CPU). FAIL-INFRA if it does not build in 30 min: record 'not seen (build)'.
2. Load check with expert streaming on our GGUF. 'not seen (arch)' if the loader rejects qwen3_5_moe / qwen3_6 or streaming needs a converted/split model format we do not have (record the exact tool/flag it wants and whether a conversion of a stock GGUF is offered; if a converter exists and runs in <= 20 min and <= 15 GiB, run it and continue).
3. If it loads: 10 prompts x {fork capped cache (<= 4 GiB), fork uncapped, b11010 control}; greedy; record text identity vs control, decode tok/s, prefill s, peak RSS (/usr/bin/time -l), free disk and swap before/after.
4. Verdict (mechanism): SEEN = loads and generates on >= 9/10 prompts with the expert cache capped, RSS <= 6 GiB, text identical to control >= 8/10; SEEN-DEGRADED = loads but text differs on > 2/10 or RSS > 6 GiB (report); NOT SEEN otherwise. Follow-up (device port) only on SEEN, after 10-20.
