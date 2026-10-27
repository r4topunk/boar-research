# Q8SCREEN criterion (frozen 2026-10-20 before any Q8 generation)

## Question
Does the same Qwen3-1.7B LITEPACKS system with the Q8_0 GGUF instead of Q4_K_M (QUANT17: Q4 KLD 0.148 / top-1 91.2 % vs BF16, Q8 0.007 / 97.2 %) pass GATE v2 on the K0 and K1 screens?

## Gate
GATE v2 as frozen in arms/null-cal/GATE-V2.md, sha256 34ada53f1a9ab4ae31d971b6989eba3b4b979de8e05516fa687aad238a582982 (tools/screen_gate_v2.py sha256 fa726fc0ac0b2380b528a5447b8058aec125a39b516eaec4f91df3173275729b).
GO iff net >= 10 on K0 (>= 9 on K1), false refusals <= 2/20 (K1 4/20), U_cov delta >= -0.059 (K1 -0.071). Screens: null-cal/pool/screen2-K0.ids (sha 891b67e2...) and screen2-K1.ids (sha 2d45ca83...). Controls: null-cal/control/pool-K0.json, pool-K1.json (mini, Q4_K_M, seed 42).

## Candidate
q8.patch (sha256 in q8.patch.sha256): one line in be/adapter-litedecline.ts MODELS["qwen3-1.7b-q4km"]: file lite/Qwen3-1.7B-Q8_0.gguf, sha256 0becaa825564295d82e9af4d008bca5f8b7f5f73bf1c6a0b58f7c53ef26b47fd (unsloth/Qwen3-1.7B-GGUF @ d7f544ee Q8_0; the adapter sha256-checks the file). On the mini the file is a symlink in shared-models/lite to <runner>/kiln/quant17/models/Qwen3-1.7B-Q8_0.gguf (no copy: disk). Everything else identical (prompts, retrieval, packs, warning line, sampler T 0.7 / top_k 40, seed 42, llama-server b11010 CPU -t 4, --reasoning off, ctx 4096).
Run: OUT_BASE=arms/q8screen/arms SCREEN_JSON=null-cal/pool/screen2-<K>.json bash null-cal/tools/run_pool.sh q8 <K0|K1> null-cal/pool/screen2-<K>.ids q8screen/q8.patch. Haiku 5.5-low judge.v1-low, N = 4, both orders; only answers that differ from the control are judged. 0 Opus, 0 paid.

## Reported
Both gate lines verbatim; CE-unwarned (control vs candidate, on the screen); false refusals; U_cov; answer tokens (mean generated tokens per live item, Q4 control vs Q8); mini wall time (trace latency sum / job start-end) vs Q4 control; phone cost = RSS delta from the file-size difference (1,834,426,944 - 1,107,409,472 = +0.73 GB weights) and a PROJECTED Pixel 8a decode = measured Q4 12-16 tok/s x (Q4 bytes / Q8 bytes = 0.604) = 7.2-9.7 tok/s (projection, bandwidth-bound assumption, not measured).

## Stage 2 (only on GO on a screen that the rule makes binding: K0 GO required)
MAIN n 97 on K0 vs the mini K0 MAIN control (lp-screens lpctl-K0-main-s42); paired item bootstrap B 2000 seed 11. PASS iff U change >= +0.03 with CI low > 0 AND CE-unwarned change <= +0.02. NO-GO at stage 1 ends the arm; no re-run to rescue a NO.

## Budget
calls_cap: Haiku 400 for stage 1 (K0 + K1; nulls used 68-94 per run).
