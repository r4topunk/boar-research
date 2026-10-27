# LITE2: is Ternary-Bonsai-2-2B (PTQ1_0, 0.43 GB, PrismML fork) better than Qwen3-1.7B Q4_K_M (1.1 GB, stock llama.cpp b11010) as the lite-tier fast model behind cut 7? (frozen 2026-10-15 22:5x by the LITE2 agent; measurement arm, r4to/coordinator request 2026-10-15)

Frozen before any judged run and before any 1.7B generation beyond the 5-item smoke. Precheck token numbers come from that smoke (l-smoke, blind/bench-v02/runs-lite2/). Adapter patch tools/adapter-lite2.patch 6f53bc17cdbf7586… (boar-eval a6e3cf3 + MODELS/ADAPTER_CATALOG entries `qwen3-1.7b-q4km`; adapter.ts e37b5a8932fa1c88…, mini side dir be-repo-lite2/). Runner lite2-remote-run.sh d8f260941a9b2e1f… (arms L and T2). Slice files: random20-v02.ids a3e43672…, selftest20.ids abc23353… (tools/make_st20.py e3dfede7…). Requests: l-kit-v02-s42-slice 6de4667f… (normalised = t2-kit-v02-s42-slice), l-st20-s42 cda4a81a…, t2-st20-s42 1942cd5d…; bench-st20 questions c87210b4… / refs 77c8b740…; control c4b-st20-s42 traces 8855d521… / Haiku rows dff24d98….

## Tags
Tags: none
Ruleset: 30

## Question
Lite-tier roadmap (post-10-20 integration either way): if the stock-llama.cpp Qwen3-1.7B Q4_K_M matches the ternary 2B on quality, the PrismML runtime lock-in is not worth it. Measured: paired Δ(2B − 1.7B) on two 20-item slices, plus each model vs the 4B control; latency, decode tok/s, file size, RSS.

## Fixed inputs
- Arm **L** (1.7B): cut 7 tree (`<runner>/kiln/be-0cfd4a77-cut7`, side dir be-repo-lite2/), `--backend server --server-bin <runner>/spikes/llama-b11010/build-cpu/bin/llama-server`, modelId `qwen3-1.7b-q4km` (file lite/Qwen3-1.7B-Q4_K_M.gguf, 1,107,409,472 B, sha b139949c…1897, HF unsloth/Qwen3-1.7B-GGUF @ d7f544ee; the official Qwen/Qwen3-1.7B-GGUF ships Q8_0 only), BOAR_SERVER_EXTRA_ARGS="--reasoning off" (accepted by b11010: seen in the smoke server log) + the engine's enable_thinking:false, threads 4, ctx 4096, seed 42, persona succinct, engine sampler.
- Arm **T2** (2B ternary): as BONSAI2-2B (fork prism-b10777-e3de715, "--device none --no-op-offload --reasoning off", file bonsai2/Ternary-Bonsai-2-2B-PTQ1_0.gguf sha 36061ad4…29fa), run through the same side dir/runner as L.
- Slice **kit** = random20-v02 (v0.2, noplaces, claim kit, quickFirst true / alwaysComplete false): L-kit = l-kit-v02-s42-slice (new); T2-kit = t2-kit-v02-s42-slice traces + Haiku rows from BONSAI2-2B (REUSED, not regenerated); 4B = dv-C-v02-s42 Haiku rows (reused).
- Slice **st20** = selftest20.ids (180 public self-test items of SELFTEST-SCORES, 9 packs; seed 42, 2 per pack + 2 more = 20): requests = the SELFTEST-SCORES with-pack requests (claim kit + the item's pack) with modelId swapped; L-st20 and T2-st20 generated here on the mini (BOAR_EVAL_PACK_DIRS = wave3:wave2:wave1:packs:crypto; noplaces); 4B control = the SELFTEST-SCORES with-pack traces + Haiku rows (MacBook kiln-local, 2026-10-13) filtered to the 20 ids (runs/c4b-st20-s42.*). Judge bench = bench-st20/ (questions/refs lines copied verbatim).
- Scoped script-only exception (coordinator 2026-10-15, BONSAI2 terms): scripts read blind/bench-v02 inputs; the agent prints counts/ids/hashes/aggregates only. Self-test items are public: their text may be read and quoted.

## Power
expected_delta: −0.05…+0.03 raw (2B − 1.7B; prior: 2B vs 4B −0.168 with the kit (BONSAI2-2B), 4B ternary vs 4B −0.045 (S1); the 1.7B is ≈ one size step below the 4B (model-size wall +0.06 per step, 10-06), so the 1.7B is expected near the 2B)
n: 20 per slice (2 slices)
seeds: 1
mde: ≈ 0.05 raw at a 20-id slice (Haiku)
slice: random20-v02.ids (a3e43672…) + selftest20.ids (abc23353…)
l1_futility: n/a (measurement with a frozen cheaper-parity clause; no Opus stage)
reopen: n/a (BONSAI2 closed R77/R78 for the fast-tier swap; this is the lite-tier comparison r4to asked for)
split: none

## Ceiling (RULE 29; 0 calls, before the freeze)
ceiling: n/a (measurement)
bar_ceiling: n/a (product/lite-tier; never preempts bar work)
launch: measurement requested by r4to 2026-10-15 (mini idle)
transfer: product-only

## Budget (RULE 29)
wall_cap: 2 h (mini: 60 generations at ≈ 3–6 s + downloads + judge)
calls_cap: Haiku 120 / Opus 0
smoke: 5 items (l-smoke = b2b-smoke-T2's 5 requests with modelId swapped: 3 v0.1 + 2 slice) -> s/item, empty share, reasoning tokens
kill_if: projected_wall > 3 h, OR any empty answer on a generation, OR reasoning tokens > 0 on any generation of either model, OR `<think>` in an answer
checkpoint: each slice's L1
subset_step0: n/a

## Precheck (to fill before the freeze)
token_projection: 483.4 (L smoke l-smoke, mean timing.promptTokens over its 5 items: 275, 631, 722, 375, 414; Qwen3 tokenizer) / token_budget: 503.37 (= 1.05 x 479.4, C's mean on the same 5 items, as S1/BONSAI2-2B)
disk_peak_gib: 1.2 (one model on disk at a time: the 1.7B 1.1 GB, deleted before the 2B 0.43 GB is fetched; free 26.4 GiB before, floor 25)
off_baseline: dv-C-v02-s42 (kit), c4b-st20-s42 (st20)
call_pattern: Haiku N=4 both orders: L-kit vs gold (40), T2-st20 vs gold (40), L-st20 vs gold (40); preflight probe disabled (PREFLIGHT_PROBE_IDS=0) to stay at 120
lane: mini-long
opus_clause: none
wall_cap_h: 2
parallelism: 1
run_type: 4b-patch

## Stages and rules
1. Smoke (done before the freeze, L): tools/gate.py (GATE_MODEL=qwen3-1.7b-q4km): 0 errors, non-empty, reasoning 0, no `<think>`, runtime.model = config.modelId; `arm.sh smoke --n-full 60` writes the verdict for this sha.
2. Generate (one llama-server at a time, runner sentinels): l-kit-v02-s42-slice, l-st20-s42 (1.7B), then delete the 1.7B, fetch the 2B, t2-st20-s42. Gate each run (tools/gate.py) and precheck vs its control (--min 0).
3. L1 Haiku 5.5-low N=4 both orders, each vs gold: L-kit (40), T2-st20 (40), L-st20 (40). The 4B rows and the T2-kit rows are reused.
4. Paired Δ (deepvpara/tools/paired.mjs, items resampled jointly, 2000 boots) per slice: **2B − 1.7B** (T2 vs L judgment files) and each model − 4B. Report ratio, floor-adj, W/T/L vs gold, head-to-head, p50 total latency, median decode tok/s.
5. **Clause (frozen): the ternary 2B is CHEAPER-PARITY vs the 1.7B if paired Δ ratio (2B − 1.7B) ≥ −0.02 with CI low ≥ −0.05 on BOTH slices (kit random20-v02, selftest20); LOSS if either slice fails.** (Read: LOSS = the 1.7B is at least as good, so the ternary lock-in buys only size/speed; the verdict says which side wins and by how much.)
- One generation per run. No rerun, except after an infrastructure error before the first token.
