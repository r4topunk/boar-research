# QUANTLITE: Q8_0 does not beat Q4_K_M on the lite 1.7B with X2b: FLAT/NEGATIVE (Haiku, dev, n 20), Δ −0.003 (−0.025…+0.019); speed clause FAIL (decode 0.68×) (2026-10-16 10:0x; Haiku 40, Opus 0, 0 paid)

Qwen3-1.7B Q8_0 vs Q4_K_M behind cut 7 + HEADPASS-X2b on selftest20: ratio 0.507 vs 0.510. Head to head 9/6/5. Quant precision is not where the lite model's residual loss sits.

## Frozen inputs
- Criterion `QUANTLITE-criterion.md` v2 sha `e0642c01…87d1` (Ruleset 30), frozen after the 5-item smoke and before any st20 generation or judge call. v1 (9e6cea89…) set token_budget = the smoke mean exactly (959.8), and smoke-project.py read that as FAIL. This was a float-equality artefact (smoke.verdict.v1-FAIL.json). v2 sets token_budget 960, same smoke. Smoke verdict PASS.
- Model: **unsloth/Qwen3-1.7B-GGUF @ d7f544ee, Q8_0, 1,834,426,944 B, sha 0becaa82… (= LFS oid).** This is the same repo and revision as the Q4, so template and tokenizer are shared and quant is the only variable. The brief named Qwen/Qwen3-1.7B-GGUF; that file (oid 061b54da…) is a different producer/template, so it was not used (recipe in MODELS.md).
- Requests (tools/mkreq_q.py): LITE5's Q4 + X2b st20 requests with only runId and modelId changed (asserted). Adapter be/adapter-quantlite.ts 89e31b5e… = adapter-lite5.ts + the q8_0 entries. Tree: the X2b tree rsynced to the mini (50 MB, no .cache / node_modules; node_modules re-linked to identical package versions). Stock b11010, `--reasoning off`, -t 4, seed 42, mini M4.
- Control: LITE5 Q4 + X2b traces and Haiku rows (MacBook), reused. References: 4B plain c4b-st20, 4B X2b x2b4b-st20 (the same rows LITE5 used).

## Gates (0 calls)
- Smoke (5 items): 0 errors/empty/reasoning; codes, kept and promptTokens = Q4 5/5.
- st20 gate (aggregates/gate-q8.json): PASS. G0 0/0/0/0; G1 headpass codes + kept = Q4 20/20; G2 promptTokens = Q4 17/17 LLM items. Retrieval and prompt are byte-identical, so only the generation differs. Answers identical to Q4: 3/20.

## Δ (Haiku 5.5-low N=4, both orders, paired.mjs 2000 boots; W/T/L vs gold 0/0/20 in every arm)
| comparison (20) | ratio a / b | Δ raw (CI) | floor-adj Δ (CI) | h2h a>/=/b> |
|---|---|---|---|---|
| **Q8 + X2b − Q4 + X2b** | 0.507 / 0.510 | **−0.003 (−0.025…+0.019)** | +0.001 (−0.029…+0.029) | 9 / 6 / 5 |
| Q8 + X2b − 4B plain | 0.507 / 0.518 | −0.011 (−0.079…+0.065) | −0.015 | 8 / 1 / 11 |
| Q8 + X2b − 4B X2b | 0.507 / 0.582 | −0.075 (−0.121…−0.029) | −0.094 | 3 / 2 / 15 |
(LITE5 Q4 for reference: −0.008 vs 4B plain, −0.072 vs 4B X2b.)

Declared split by the LITE6 bucket of the Q4 item (mean BOAR score Q8 / Q4, up/same/down): thin 8: 2.77 / 2.63, 4/4/0; not_read 4: 1.96 / 2.00, 2/0/2; invented 1: =; above-4B 5: =, 3/0/2; tie 2: 1.50 / 1.58. Descriptive only (n 1–8). Thin moves slightly; nothing else does.

## Speed and memory (mini M4, same host; Q4 anchor = the same 20 requests re-generated with Q4, 0 judge)
| | decode tok/s p50 | prefill tok/s p50 | ttft p50 s | total p50 s | RSS llama-server max / median of run medians |
|---|---|---|---|---|---|
| Q8_0 | 34.5 | 292 | 3.15 | 4.61 | 3.55 / 2.78 GiB |
| Q4_K_M | 50.5 | 216 | 4.00 | 4.97 | 2.54 / 1.88 GiB |
| ratio Q8/Q4 | **0.68 (clause ≥ 0.70: FAIL)** | 1.35 | 0.79 | 0.93 | **1.40 (clause ≤ 2: PASS)** |
- On the desktop CPU, Q8 decodes slower (it reads 1.65× more bytes) but prefills faster, because there is less dequant work. With X2b's ≈ 815-token prompts, Q8 is 7 % faster end to end. A phone's decode and prefill balance differs, so this was not measured on a device.
- Host anchor: Q4 on the mini vs the same Q4 on the MacBook gives identical answers on 6/20 (kept/promptTokens 20/20). The Q8 − Q4 Δ therefore carries one host re-sample, and that noise is as large as the effect being looked for.

## Verdict
**FLAT/NEGATIVE (Haiku, dev, n 20): Δ(Q8 − Q4) −0.003 (−0.025…+0.019); speed clause FAIL on decode (0.68×).** The CI excludes a gain ≥ +0.02 at this n. The Q4_K_M stays the lite file (1.1 GB vs 1.8 GB, ≈ 1 GiB less RSS). The 180 and the kit slice were not licensed, so 40 of the 80 Haiku calls were not spent.
Caveats: n 20, one seed, Haiku only, cross-host control, agent-written gold. The LITE6 loss (thin/not_read) is not a 4-bit precision artefact.

## Files
`QUANTLITE-criterion.md` (+ .sha256, v1 + .v1.sha256), `smoke.verdict.json` (+ v1-FAIL), `arm-st-Q8.conf`; `tools/{adapter-quantlite.ts, adapter-quantlite.vs-lite5.patch, mkreq_q.py, quantlite-remote-run.sh, quantlite-batch.sh, gate_q.py, split_q.py}`; `runs/` (smoke, st20 per-pack requests/traces/status/logs, merged Q8 + Q4-anchor traces, Q8 Haiku judgments); `aggregates/{quantlite.json, gate-q8.json, anchor-q4mini.json, smoke-gate.json, split-q8.json, L1-*.json, think-*.json}`.
Public self-tests only: blind/ and rnd/veil/ were not read, so there is no EXPOSURES row. Mini: both GGUFs deleted at the end (DISK-LOG), the X2b tree copy is kept (50 MB), free 27.4 GiB. No servers left running (only the :8094 detector, untouched).
