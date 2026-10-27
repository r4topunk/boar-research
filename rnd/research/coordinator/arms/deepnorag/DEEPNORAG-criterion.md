# DEEPNORAG: does retrieval still matter for the deep tier + thinking 512? (frozen 2026-10-10 03:0x, coordinator; diagnostic)

Question: DEEPVPARA found 84 % of the deep tier's gain on items where retrieval gave nothing usable, and the 4B's retrieval captured only +0.02 of its +0.10 scorecard. With thinking 512 (the recommended configuration), how much do the knowledge packs add? If ≈ nothing, a device deep path could skip retrieval (≈ 400 fewer prompt tokens, no embedder) and the claim can say so; if they matter, the number says by how much.

## Fixed inputs
- Arm **N**: exactly DT512's configuration (tree `be-0cfd4a77-dt512`, runner `dt512-remote-run.sh <run> D`, persona succinct, `--deep-model qwen3.6-35b-a3b-ud-q2kxl`, `--places` kit-vexact, detector v3b, thinking 512, ctx 4096, `--timeout-ms 600000`) with **`config.kit = []`** in the requests (no knowledge packs: boar-crypto and boar-wikivoyage-en removed; places and the detector/cards unchanged). Everything else byte-identical to DT512's requests (runId, kit and arm label aside).
- Control **H** = DT512 `dh-H-vpara-s42-slice` (slice) / `dh-H-vpara-s42` (full) Haiku rows; D/T rows not needed.
- Judge: Haiku 5.5-low N = 4, both orders, V-para refs; no Opus (diagnostic, not a claim number). Script-only scoped exception as DT512; exposure logged.
## Stages and rules
1. Smoke (2 v0.1 items): 2/2 `generate:deep-thinking`, 0 errors, non-empty answers, and the route shows no pack sources (`grounding:no-source-memory` or 0 kept); else FAIL-INFRA (an empty kit is not accepted → stop, report).
2. Slice 20 (signal20-vpara, s42) vs H slice, paired Haiku Δ (N − H). Reading: **RETRIEVAL-MATTERS** if Δ ≤ −0.03; **RETRIEVAL-ADDS-LITTLE** if Δ > −0.03. If |Δ| < 0.03 run stage 3 to tighten.
3. Full 51 ids s42 vs H full (Haiku 102): same reading with the CI; report per-category Δ and the share of items whose H run had kept sources.
- No promotion: N is never adopted by this arm; it informs the device plan and the claim wording.
## Budget
Mini ≤ 1.5 h (smoke 5 min, slice ≈ 27 min, full ≈ 1 h); Haiku ≤ 142; Opus 0.
## Outputs
`arms/deepnorag/DEEPNORAG.md` (≤ 40 lines), `aggregates/`, `arm.conf`; traces/judgments in `blind/V-para/runs-deepnorag/`; smoke in `boar-eval/runs/kiln/deepnorag/`. QUEUE entry by the coordinator.
