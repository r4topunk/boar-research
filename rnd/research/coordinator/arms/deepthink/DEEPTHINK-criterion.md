# DEEPTHINK: does thinking mode on the deep tier lift the bounty-style set? (frozen 2026-10-08 17:2x, coordinator)

Question: all deep-tier runs so far had thinking off (`depth.ts` deep branch `thinking: false`); the engine already defines DEEP_THINKING_BUDGET = 1024 and the server runner enforces it (`thinking_budget_tokens` + "I have thought enough" message). DEEPVPARA-CATS shows the deep tier still at correctness ≈ 2.5–2.75 on V-para comparison/synthesis/reasoning. Does a 1024-token thinking budget lift V-para, and at what time cost? Ceiling measurement (desktop); product speed is a separate question.

## Fixed inputs
- Arm **T**: cut 6 tree (mini `be-0cfd4a77-detmax`, PATCH_SHA256 824e0b35…) copied to `be-0cfd4a77-deepthink` with `arms/deepthink/deepthink-on-cut6.patch` applied (sha in `.patch.sha256`; one line in `src/routing/depth.ts`: deep branch `thinking: true` + reason code `generate:deep-thinking`); `tsc --noEmit` must pass; vitest not required (a depth test asserting `thinking: false` may fail; record it). Everything else exactly as DEEPVPARA arm D: `--backend server --deep-model qwen3.6-35b-a3b-ud-q2kxl`, settings {quickFirst, alwaysComplete, deepModelId}, detector v3b ON, ship profile, V-para config (b) with `--places` kit-vexact, llama-server b11010 CPU, GGUF sha 96b9c0af…. The runner sends `thinking_budget_tokens 1024` (server.ts) because `gen.thinking` is now true; `enable_thinking` is not forced off. Record per item: reasoning tokens, budget-hit count (the budget message), answer tokens, total ms.
- Control **D**: `blind/V-para/runs-deepvpara/dv-D-vpara-s42.traces.jsonl` + its Haiku rows `dv-D-vpara-s42.judgments.haiku55-low.jsonl` (same tree minus the patch, same seed 42). Opus rows `dv-D-vpara-s42.judgments.jsonl` for L2.
- Set: V-para, requests = `runs-cut6/cut6-vpara-s42.requests.jsonl` (58; 51 judged ids from `runs-cut6/judged.ids`), seed 42. Script-only scoped exception as DEEPVPARA (ids, counts, hashes, route codes, timings, aggregates only); logged as an exposure.
- Judge L1: Haiku 5.5-low sharded N = 4, both orders, V-para refs (952e2c44…), `--system deepthink-T-haiku55-low`. L2 (on promotion): Opus judge.v1 sharded N = 4 (OPUSSHARD), `--system deepthink-T-opus`, then seed 43 for T (generation + Opus) and the two-seed claim scales beside DEEPVPARA's D.
## Rules (strict)
- Promote: per-item winner T vs D (both orders, disagreement = tie): T wins ≥ D wins + 3 OR Haiku paired Δ ratio (T − D) ≥ +0.03. Else **NO** (thinking does not help the deep tier on V-para at 1024 tokens); stop.
- Report either way: thinking tokens median, budget-hit count/51, desktop p50 total ms for T vs D (33 s), Haiku ratios and Δ with CI, per-category Δ (counts only).
- One generation per seed, no rerun except an infrastructure error before the first token; a budget hit is a result, not an error.
## Stop rules and budget
Mini disk ≥ 25 GiB, swap ≤ 8 GB, heavy lock, one 35B server at a time, never restart Docker, never stop the detector. Stage 1 ≤ 4 h mini (expected 51 × ≈ 2.5 min ≈ 2.2 h); Haiku ≤ 120; Opus ≤ 204 (two seeds) only after promotion.
## Outputs
`arms/deepthink/DEEPTHINK.md` (≤ 60 lines, cites this sha and the patch sha), aggregates JSON in `arms/deepthink/aggregates/`, traces/judgments in `blind/V-para/runs-deepthink/`, tools in `arms/deepthink/tools/`. QUEUE entry by the coordinator.
