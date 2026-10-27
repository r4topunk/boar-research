# BONSAI2-S1: does Ternary-Bonsai-2-4B (PTQ1_0) answer as well as the Qwen3-4B Q4_K_M on the fast path, closed-book and with the claim kit? (DRAFT, not frozen; 2026-10-15 21:4x, coordinator)

DRAFT until the S1 agent fills the two Precheck token numbers from the T-kit smoke and writes the `.sha256` (rule text fixed by the coordinator 2026-10-15 22:0x; adapter patch done: tools/adapter-bonsai2.patch a65e4c69…).

## Tags
Tags: none
Ruleset: 30

## Question
The arm swaps the fast-tier model: Qwen3-4B-Instruct-2507 Q4_K_M (2.50 GB, llama-server b11010) becomes Ternary-Bonsai-2-4B PTQ1_0 (0.95 GB, base Qwen3.5-4B, PrismML fork prism-b10777-e3de715). Engine, persona, retrieval and sampler stay the same. We measure it in two configurations: closed-book (`config.kit = []`) and with the claim kit. The answer decides whether the 2.6× smaller file and 0.5× RSS (S0 § BONSAI2-B: decode 0.79×, so it passes the speed clause) are worth a maintainer question about building the native app's JNI llama.cpp from the fork. Nothing here ships by 10-20.

## Fixed inputs
- Arm **T** (ternary): cut 7 tree (`kiln-local/be-0cfd4a77-cut7`, the MP4B/C tree), `--backend server --server-bin <runner>/spikes/llama-prism/bin/llama-server`, modelId `bonsai2-4b-ptq1_0` (file `bonsai2/Ternary-Bonsai-2-4B-PTQ1_0.gguf`, sha 56711263…4d60), threads 4, ctx 4096, persona succinct, noplaces, seed 42. Sampler = the engine's (temp 0.7 / top_k 40 / top_p 0.95 / min_p 0.05, as the control). The card's presence 1.5 is NOT applied, so the swap stays single-variable. Thinking is OFF for T through the fork server's `--reasoning off` flag (BOAR_SERVER_EXTRA_ARGS="--device none --no-op-offload --reasoning off"; S1 sanity 2026-10-15: the engine's fast tier sends a 256-token thinking budget (depth.ts:259), harmless on the instruct 4B but Bonsai2's Qwen3.5 template thinks by default: 265 reasoning tokens per item without the flag, 0 with it; the native port would need the same switch). Any reasoning tokens > 0 on T = kill_if.
  - **T-cb**: requests = the 20 random20-v02 ids with `config.kit = []`.
  - **T-kit**: requests = C's s42 requests on the 20 ids with only `modelId` changed.
- Control **C-kit**: the existing `dv-C-v02-s42` rows (`runs-deepvpara`, 4B Q4_K_M claim config; Haiku rows reused, as MP4B did).
- Control **C-cb**: NEW generation: the 4B Q4_K_M, same tree and backend (b11010 build-cpu), the same 20 ids with `config.kit = []`. Generating it needs 0 judge calls. No closed-book v0.2 4B rows are known to exist.
- Slice: `arms/random20-v02.ids` (sha a3e43672… in arms/random20-sets.sha256). The v0.2 questions, gold, the dv-C-v02-s42 requests/traces and the Haiku control rows live under `blind/bench-v02/` (v0.2 is burnt → dev status, CLAUDE.md). **Scoped script-only exception (coordinator, 2026-10-15 22:0x, as DEEPVPARA/THINK4B):** the S1 agent's scripts may read those files to build requests, run the adapter, the precheck and the judge; the agent never prints, greps or reads item text or answers (counts, ids, hashes, aggregates only); one row in coordinator/EXPOSURES.md (set v0.2 random20 slice, runs c-cb/t-cb/t-kit, 80 Haiku).

## Power
expected_delta: −0.03 raw (source: Q35 screen, Qwen3.5-4B Q4_K_M closed-book v0.1 0.437 vs Qwen3-4B 0.487 = −0.05 (arms/q35/Q35-screen.md); ternary PTQ adds a further loss (27B card: knowledge −2.4 pts MMLU-Redux). The prior is negative. The arm is a cheaper-parity question, not a lever hunt.)
n: 20 (slice), then 110 (v0.2 full) only if the parity clause is still open
seeds: 1
mde: ≈ 0.05 raw at the 20-id slice (L1-PROTOCOL; v0.2 full one seed ≈ 0.025)
slice: random20-v02.ids
l1_futility: RULE 29. Parity variant: close **NO (Haiku, dev)** if the paired Δ CI low < −0.05 on either configuration. Mark **parity-plausible** if Δ ≥ −0.02 and CI low ≥ −0.05 on both, and then go to the v0.2 full Haiku stage (only within calls_cap; otherwise 'not decided'). A Δ > 0 near-miss goes to Opus N = 4 only with a new budget (Opus cap 0 here).
reopen: Q35 (Qwen3.5-4B Q4_K_M, closed 2026-10-05) is the same base family. What is new: a ternary PTQ at 0.38× file / 0.5× RSS, and the full engine with the kit (Q35 was closed-book only).
split: none

## Ceiling (RULE 29; 0 calls, before the freeze)
ceiling: n/a (parity/cheaper arm)
bar_ceiling: n/a (product/device-tier arm; it never preempts bar work)
launch: parity arm, so the clause decides; expected_delta < 0 is declared
transfer: product-only (fast-tier swap; V-para not used)

## Budget (RULE 29)
wall_cap: 1.5 h mini (4 × 20 generations at ≈ 10–20 s/item for the kit path, plus smoke)
calls_cap: Haiku 80 (T-cb vs C-cb 40 + T-kit vs C-kit 40, N = 4 both orders) / Opus 0
smoke: 10 items -> s/item, fire rate, parse rate; projected wall logged in QUEUE before any run > 2 h
kill_if: projected_wall > 1.5 × wall_cap, OR any empty/cut answer, OR reasoning tokens > 0 on the fast path (thinking leak), OR `<think>` in an answer
checkpoint: the slice L1 itself
subset_step0: n/a

## Precheck (to fill before the freeze)
token_projection: <mean prompt tokens of the T-kit smoke> / token_budget: <C's mean + 5 % (same prompts; tokenizer differs Qwen3 vs Qwen3.5)>
disk_peak_gib: 0 (models already on the mini; traces < 50 MB)
off_baseline: dv-C-v02-s42 (kit); c-cb-v02-s42-slice (to be generated)
call_pattern: Haiku N=4 both orders on random20-v02, two comparisons (cb, kit)
lane: mini-long
opus_clause: none
wall_cap_h: 1.5
parallelism: 1
run_type: 4b-patch

## Stages and rules
1. Smoke: 3 v0.1 items + 2 slice items on T-kit: 0 errors, non-empty, `reasoning_content` empty, the server log shows `--device none` in effect (see Blockers 2), modelId `bonsai2-4b-ptq1_0` in the trace.
2. Generate C-cb, T-cb and T-kit on the 20 ids (one server at a time, port chosen by the adapter).
3. L1 Haiku 5.5-low N = 4 both orders: T-cb vs C-cb, T-kit vs C-kit.
4. Verdict (label names judge and set): **CHEAPER-PARITY (Haiku, dev slice)** if both configurations meet the parity clause; **CHEAPER-LOSS** if CI low ≥ −0.05 but Δ < −0.02; **NO** otherwise. There is no LEVER label in this arm.
- One generation per seed and stage. No rerun, except after an infrastructure error before the first token.

## Blockers for launch (adapter check 2026-10-15)
1. `--server-bin` exists (adapter.ts: `--backend server --server-bin <llama-server>`), and the fork's llama-server accepts every hard-coded flag (`-tb`, `--jinja`, `--no-webui`, `--cache-ram 0`, `--reasoning-format deepseek`; `--version` = "0.2.0-dev (build 10777, commit e3de71522)", which the version regex parses). **Missing: a model entry.** `MODELS` and `ADAPTER_CATALOG` in runner/adapter.ts have no `bonsai2-4b-ptq1_0`. The fix is a THINK4B-style patch (boar-eval 796add7): `{ file: "bonsai2/Ternary-Bonsai-2-4B-PTQ1_0.gguf", sha256: "56711263ec9a9ffeaa74a3a0e58dece8127cf9268404746c721113ca76994d60" }`, plus a catalog entry with answerTier default, roles general+fast, usesChatTemplate true, and sizeBytes 949549920.
2. **Missing: extra server args.** The server args are hard-coded (`-ngl 0` only), and the fork binary is a Metal build. Without `--device none --no-op-offload`, op offload can put prefill on the GPU. Quality probably stays the same, but the speed/RSS fields would not be CPU numbers. The fix is a 1-line env, `BOAR_SERVER_EXTRA_ARGS`, appended to `args` and recorded in versions. A default-off differential is needed (unset = byte-identical args).
3. The C-cb generation (above).
