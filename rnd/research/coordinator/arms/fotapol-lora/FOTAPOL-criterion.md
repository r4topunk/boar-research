# FOTAPOL criterion (frozen 2026-10-20 before any screen generation; only the 5-item onboarding smoke ran before this file)

## Question
Does the same Qwen3-1.7B LITEPACKS system with the LoRA adapter `fotapol/qwen3-1.7b-financial-rag-lora-v4` applied (card: false refusal 41.4 % -> 4.4 %, citation completion 33 % -> 83 % on its own financial RAG validation set) pass GATE v2 on the K0 and K1 screens?

## Gate
GATE v2 as frozen in arms/null-cal/GATE-V2.md, sha256 34ada53f1a9ab4ae31d971b6989eba3b4b979de8e05516fa687aad238a582982 (tools/screen_gate_v2.py sha256 fa726fc0ac0b2380b528a5447b8058aec125a39b516eaec4f91df3173275729b).
GO iff net >= 10 on K0 (>= 9 on K1), false refusals <= 2/20 (K1 4/20), U_cov delta >= -0.059 (K1 -0.071). Screens: null-cal/pool/screen2-K0.ids (sha 891b67e2...) and screen2-K1.ids (sha 2d45ca83...). Controls: null-cal/control/pool-K0.json, pool-K1.json (mini, plain Q4_K_M, seed 42).

## Candidate
fotapol.env (sha256 in fotapol.env.sha256): `BOAR_SERVER_EXTRA_ARGS="--reasoning off --lora <runner>/kiln/fotapol/fotapol-v4-lora-f16.gguf"` (quoted, arms/greedy lesson). The LoRA GGUF is sha256 a04b72ac33670121a9c300a4e9c5da6836fa0a501f07ee1b390586f768dcfe45 (392 tensors, f16), converted with llama.cpp b11010 `convert_lora_to_gguf.py --outtype f16 --base <Qwen3-1.7B rev 70d244cc config + tokenizer>` from adapter_model.safetensors sha256 6a89a40cb988567ee09e1ed049b19f09456ec84975738da9edec27613627b2e2 (= card; HF rev d1af458b). Scale 1.0. Everything else identical to the control: base lite/Qwen3-1.7B-Q4_K_M.gguf (b139949c), BOAR prompts and `[n]` source numbering unchanged (deployability variant (a) of the shortlist; the card's `[Source N]` format is NOT used), retrieval, packs, warning line, sampler T 0.7 / top_k 40, seed 42, llama-server b11010 CPU -t 4, thinking off, ctx 4096.
Run: OUT_BASE=arms/fotapol-lora/arms SCREEN_JSON=null-cal/pool/screen2-<K>.json CRITERION=<this file> bash null-cal/tools/run_pool.sh fotapol <K0|K1> null-cal/pool/screen2-<K>.ids fotapol-lora/fotapol.env. Haiku 5.5-low judge.v1-low, N = 4, both orders; only answers that differ from the control are judged. 0 Opus, 0 paid.

## Reported
Both gate lines verbatim; CE-unwarned (control vs candidate, on the screen); false refusals; U_cov; declines and warned counts; citation compliance = share of live non-decline non-warned answers containing an engine-format `[n]` marker (and count of `[Source n]` markers), candidate vs control; mean output tokens per live item; mini wall time (sum of trace timing.totalMs, and p50) vs the control traces, noting the LoRA leaves the CPU_REPACK path.

## Stage 2 (only on GO on K0; K1 is reported)
MAIN n 97 on K0 vs the mini K0 MAIN control (lp-screens lpctl-K0-main-s42) via lp-screens/tools/run_arm.sh fotapol K0 main fotapol-lora/fotapol.env; paired item bootstrap B 2000 seed 11 (agg_run.py --control). Corrected labels (null-cal/tools/labels.py). PASS iff U change >= +0.03 with CI low > 0 AND CE-unwarned change <= +0.02. NO-GO at stage 1 ends the arm; no re-run to rescue a NO.

## Budget
calls_cap: Haiku 600 (stage 1 K0 + K1 <= 400, the nulls used 68-94 per run; stage 2 MAIN 97 <= 200 = changed answers x 2 orders). Opus 0.
