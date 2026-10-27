# LITE2: LOSS for the ternary 2B: Qwen3-1.7B Q4_K_M on stock llama.cpp is at least as good (2026-10-15 22:45–23:15; 120 Haiku, 0 Opus, 0 paid)

Ternary-Bonsai-2-2B (PTQ1_0, PrismML fork) vs Qwen3-1.7B Q4_K_M (b11010) as the lite fast model behind cut 7. Kit: the 2B loses −0.057 (CI −0.104…−0.014). Self-tests: −0.020 (−0.077…+0.038). The frozen clause needs Δ ≥ −0.02 and CI low ≥ −0.05 on both slices, and it fails on both, so the verdict is **LOSS**. The 1.7B decodes faster (56 vs 47 tok/s). The 2B keeps only its size and RAM edge (0.43 vs 1.1 GB file, ≈ 0.8 vs ≈ 2.3 GB RSS). The ternary runtime lock-in is not worth it on quality.

## Frozen inputs
- Criterion `LITE2-criterion.md` sha256 `628f60c26e9c8167b783eb8f5f43ade8874ade572733ca1f50cb93ebf1fa1fa1`, frozen after the 5-item 1.7B smoke and before any judged run. `smoke.verdict.json` PASS (483.4 mean prompt tokens vs a budget of 503.37; projected 0.055 h; identity PASS).
- Patch `tools/adapter-lite2.patch` 6f53bc17… (adapter.ts e37b5a89…; side dir be-repo-lite2/). Runner `lite2-remote-run.sh` d8f26094… (arms L and T2, plus a 2 s RSS sampler). Slices: `random20-v02.ids` a3e43672… and `selftest20.ids` abc23353… (`tools/make_st20.py`: seed 42, 2 per pack over the 9 packs of the 180, plus 2 extra, so outdoors and medlineplus have 3 each).
- Model: unsloth/Qwen3-1.7B-GGUF @ d7f544ee, Q4_K_M, 1,107,409,472 B, sha b139949c…1897 (= LFS oid). The official Qwen repo has Q8_0 only. Thinking is OFF: b11010 accepts `--reasoning off` (it appears in every server log) on top of the engine's enable_thinking:false. Reasoning tokens = 0 on all 45 1.7B traces and all 20 new 2B traces.
- Infra fix before the first token: the adapter refused the one-file l-st20-s42 run (one config per file, and each pack has its own kit). I split it into 9 per-pack runs per arm (`tools/run_st20.sh`) and merged them. The one-file requests are kept as `*.onefile-infrafail.jsonl`.
- Reused rows: the T2-kit traces and Haiku rows come from BONSAI2-2B, not regenerated (T2 vs C reproduces −0.168 exactly). The 4B kit rows are dv-C-v02-s42. The 4B st20 rows are SELFTEST-SCORES with-pack (MacBook), filtered to the 20 ids. Precheck kept-diff = 0 on every pair (L/T2/4B, both slices), so retrieval is identical and only the model differs.

## Δ ratio (Haiku 5.5-low N=4, both orders; paired, 2000 boots; W/T/L vs gold)
| slice | 1.7B ratio (CI) / floor-adj | 2B ratio (CI) / floor-adj | 4B ratio / floor-adj | **2B − 1.7B** (CI) | floor-adj Δ (CI) | h2h 2B>/=/1.7B> | clause |
|---|---|---|---|---|---|---|---|
| kit random20-v02 | 0.430 (0.342–0.523) / 0.282 | 0.373 (0.294–0.472) / 0.210 | 0.541 / 0.420 | **−0.057 (−0.104…−0.014)** | −0.072 (−0.133…−0.020) | 4 / 5 / 11 | FAIL |
| selftest20 (pack) | 0.430 (0.376–0.492) / 0.270 | 0.411 (0.353–0.476) / 0.245 | 0.518 / 0.384 | **−0.020 (−0.077…+0.038)** | −0.025 (−0.094…+0.050) | 4 / 5 / 11 | FAIL (CI low) |

| vs the 4B | kit Δ (CI) | h2h arm>/=/4B> | st20 Δ (CI) | h2h |
|---|---|---|---|---|
| 1.7B − 4B | −0.111 (−0.191…−0.047) | 3 / 5 / 12 | −0.088 (−0.141…−0.040) | 4 / 2 / 14 |
| 2B − 4B | −0.168 (−0.238…−0.105) | 1 / 3 / 16 | −0.108 (−0.186…−0.032) | 3 / 2 / 15 |
- W/T/L vs gold is 0/0/20 for both lite models on both slices (4B: kit 0/1/19, st20 0/0/20). The deterministic layer answers 3 st20 health items (firstaid-008/009, medlineplus-017) with the same no-source refusal for every model.

## Speed and memory (mini M4, -t 4, ctx 4096; generated items only)
| model | file | RSS llama-server (2 s sampler, per-run median / max) | kit p50 total / ttft s | kit decode tok/s | st20 p50 total / ttft s | st20 decode tok/s |
|---|---|---|---|---|---|---|
| Qwen3-1.7B Q4_K_M (b11010) | 1.11 GB | 2.1–2.5 GB / 2.71 GB | 2.59 / 1.62 | 56.0 | 3.31 / 2.31 | 53.7 |
| Bonsai2-2B PTQ1_0 (fork) | 0.43 GB | 0.66–0.81 GB / 0.83 GB (S0 steady 0.93) | 2.44 / 1.43 | 47.2 | 2.61 / 1.61 | 47.5 |
| 4B Q4_K_M (control) | 2.5 GB | – | 6.54 / 3.63 | 25.5 | 8.12 / 5.39 (MacBook) | 26.9 (MacBook) |
- Both lite models are ≈ 2.5× faster end to end than the 4B. The 2B has a lower ttft (prefill) and the 1.7B a higher decode rate. The 2B's real advantage is RAM, ≈ 3× less, which matters on a 4–6 GB phone.

## Worst 2B answers vs the 1.7B (public self-tests; BOAR mean 2B / 1.7B)
- st-qa-health-se-003 hiccups (1.33 / 2.33): "you might try a warm compress or rest your stomach" (no vagal manoeuvres).
- st-qa-bitcoin-se-019 faucets (1.17 / 2.00): "Sharing your address is dangerous" (gold: an address is harmless to share).
- st-qa-outdoors-se-007 contouring (1.50 / 2.33): "rather than strictly maintaining a fixed elevation" (this inverts the definition).

## Verdict
**LOSS (Haiku, dev slices).** The ternary 2B does not match the 1.7B. It is clearly worse on the bounty-shaped kit slice, and on the pack self-tests its CI reaches −0.077. The only thing the ternary runtime buys is footprint (0.43 GB file, ≈ 0.8 GB RSS vs 1.1 GB / ≈ 2.3 GB). For LITE3/LITE4 the stock-runtime Qwen3-1.7B is the lite candidate. Both lite models still sit 0.09–0.11 below the 4B, and the unsafe-answer warning (HEALTHGAP) is still needed before either ships.

## Files
`LITE2-criterion.md` (+ `.sha256`), `smoke.verdict.json`, `selftest20.ids` (+ `selftest20.sha256`), `arm-L.conf`, `arm-st-{L,T2}.conf`, `lite2-remote-run.sh` (+ `.sha256`), `tools/{adapter-lite2.patch(.sha256), make_st20.py, build_st20.py, mkreq_swap.py, run_st20.sh, gate.py}`, `bench-st20/`, `runs/{l,t2}-st20*` + `runs/c4b-st20-s42.*` (public self-test traces and judgments), `aggregates/{lite2.json, latency.json, L1-*.json, L1-rule-*.txt, think-*.json, gen-*.txt}`. v0.2: `blind/bench-v02/runs-lite2/{l-smoke, l-kit-v02-s42-slice}.*`.

Exposure: one v0.2 random20 slice (20 generations + a 5-item smoke with 2 slice ids, 40 Haiku calls) under the scoped exception. No v0.2 item text, answer or gold was read. rnd/veil/ was not read. EXPOSURES row 2026-10-15 LITE2. Mini: both models deleted (class A, DISK-LOG), no servers left (only the 8094 detector), free 26.2 GiB. The boar-eval working tree carries the 1.7B adapter entries, uncommitted.
