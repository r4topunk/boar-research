# DEEPTHINK-2: thinking budget 3072 on the deep tier, V-para (frozen 2026-10-08 18:5x, coordinator)


## Fixed inputs
- Arm **T2**: cut 6 tree copy `be-0cfd4a77-deepthink2` + `arms/deepthink2/deepthink2-on-cut6.patch` (sha in `.sha256`): depth.ts deep branch `thinking: true` + reason code `generate:deep-thinking-3072`; answer.ts `DEEP_THINKING_BUDGET = 3072`. `tsc --noEmit` passes. Context: the engine's context budget formula (answer.ts l.992–1000) subtracts the thinking budget from the window, so llama-server must run with `-c 8192`: set env `BOAR_SERVER_CTX=8192` (boar-eval adapter commit after 060845f, default 4096 unchanged; record the adapter sha). Everything else as DEEPTHINK arm T / DEEPVPARA arm D (server backend, deep model, detector ON, ship profile, V-para config (b) with places, seed 42).
- Control **T** (budget 1024): `blind/V-para/runs-deepthink/dt-T-vpara-s42.*` (traces, Haiku rows `judgments.haiku55-low.jsonl`, Opus rows `judgments.jsonl`). Secondary: D (DEEPVPARA) and K (claim) for the ladder.
- Set: V-para s42 (58 requests, 51 judged ids). Script-only scoped exception as before; logged as an exposure.
- Judge L1: Haiku 5.5-low N = 4, both orders, `--system deepthink2-T2-haiku55-low`; L2 on promotion: Opus judge.v1 N = 4 (`--system deepthink2-T2-opus`), seed 43 afterwards, two-seed claim scales.
- Record per item: reasoning tokens, budget hits (≥ 3000 or the budget message), answer tokens, total ms; p50 and p90 total s.
## Rules (strict)
- Promote T2 over T: wins ≥ T wins + 3 OR Haiku paired Δ (T2 − T) ≥ +0.03. Else NO (the budget, not the thinking, is saturated at 1024; keep 1024 as the reference thinking configuration).
- Report either way; no rerun except infrastructure error before the first token.
## Stop rules and budget
Must start only after `dt-T-vpara-s43` has finished (STATUS end or no 35B server running); disk ≥ 25 GiB; swap ≤ 8 GB; heavy lock; one 35B server; never restart Docker or stop the detector. Expected ≈ 58 × 5 min ≈ 5 h; hard stop at 7 h for stage 1 (write FAIL-INCOMPLETE with the items done if the cap hits). Haiku ≤ 120; Opus ≤ 204 only after promotion.
## Outputs
`arms/deepthink2/DEEPTHINK2.md` (≤ 60 lines, cites criterion + patch shas + adapter sha), `aggregates/`, `tools/`; traces/judgments in `blind/V-para/runs-deepthink2/`. QUEUE entry by the coordinator.
