# DEEPTHINK-V02: deep tier + thinking on v0.2 (frozen 2026-10-08 22:3x, coordinator; parametrised on DEEPTHINK-2's verdict)

Question: on v0.2 (110 items, burnt → dev) the deep tier without thinking scored floor-adjusted 0.457 (0.417–0.500). Does deep + thinking cross 0.50 there, and by how much does it lift the 4B claim run (0.388)? Same design as DEEPVPARA Stage 2 with the thinking arm.

## Fixed inputs
- Budget **B** and tree: if DEEPTHINK-2 (arms/deepthink2) ends PROMOTED, B = 3072 → tree `be-0cfd4a77-deepthink2` with `BOAR_SERVER_CTX=8192`; otherwise B = 1024 → tree `be-0cfd4a77-deepthink` (ctx 4096). Record which, with the patch sha and the adapter.ts sha of the tree's be-repo. No other engine/adapter change.
- Arm **TV**: that tree, `--backend server --deep-model qwen3.6-35b-a3b-ud-q2kxl`, settings {quickFirst, alwaysComplete, deepModelId}, detector v3b ON, ship profile, **no places** (v0.2 = Run A config, as DEEPVPARA Stage 2), `--timeout-ms 600000` (ratified), seed 42 then 43.
- Controls: **D** = `blind/bench-v02/runs-deepvpara/dv-D-v02-s{42,43}` (Haiku rows `.judgments.haiku55-low.jsonl`, Opus rows `.judgments.jsonl`); **K** = `blind/bench-v02/runs-cut6/cut6-v02-s{42,43}` (Opus). Requests = `runs-cut6/cut6-v02-s42.requests.jsonl` (110) and s43.
- Script-only scoped exception as before (ids, counts, hashes, route codes, timings, aggregates only); logged as an exposure.
- Judge L1: Haiku 5.5-low N = 4, both orders, v0.2 refs (`refs 1e2668c488a1, questions c883053b0595` in the judge's first log line), `--system deepthinkv02-TV-haiku55-low`. L2 on promotion: Opus judge.v1 N = 4 (`--system deepthinkv02-TV-opus`), seed 43 generation + Opus, two-seed claim scales (raw / floor-adjusted / above-decline with CIs, win-rate, paired Δ vs D and vs K), per-category Δ, thinking stats (median reasoning tokens, budget hits, p50/p90 total s).
## Rules (strict)
- Promote TV over D (110 ids, seed 42): wins ≥ D wins + 3 OR Haiku paired Δ (TV − D) ≥ +0.03. Else NO; stop after L1.
- Bar reading at L2: "floor-adjusted CI low > 0.50 and win-rate > 0" = meets the bar on v0.2 (dev); otherwise "below by X" or "point above, CI straddles".
- One generation per seed; no rerun except an infrastructure error before the first token.
## Stop rules and budget
Start only after DEEPTHINK-2 has fully finished (no 35B server; its s43 run ended or not promoted). Disk ≥ 25 GiB, swap ≤ 8 GB, heavy lock, one 35B server, never restart Docker or stop the detector. Expected ≈ 110 × 2.5 min ≈ 4.5 h per seed; hard stop 7 h per seed. Haiku ≤ 240; Opus ≤ 440 only after promotion.
## Outputs
`arms/deepthinkv02/DEEPTHINKV02.md` (≤ 60 lines; cites this sha, the patch sha, the adapter sha, the DEEPTHINK-2 verdict used), `aggregates/`, `tools/`; traces/judgments in `blind/bench-v02/runs-deepthinkv02/`. QUEUE entry by the coordinator.
