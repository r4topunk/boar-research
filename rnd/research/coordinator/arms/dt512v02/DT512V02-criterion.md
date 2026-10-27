# DT512-V02: the recommended deep configuration (thinking 512) measured on v0.2 (frozen 2026-10-09 21:0x, coordinator; measurement only)

Why: DT512 (V-para) made 512 the recommended thinking budget; the v0.2 thinking number in the claim draft (floor-adj 0.514, point above 0.50) is at 1024. This measures 512 on v0.2 so the recommended configuration has its own row on the second set. No decision follows except the wording of the claim row; the recommendation stays 512 regardless (DT256 fixed the knee).

## Fixed inputs
- Arm **H** (as DT512): tree `be-0cfd4a77-dt512` (cut 6 + deepthink patch eb3f464b… + dt512 patch f9a1979b…), `dt512-remote-run.sh <run> D noplaces` (v0.2 = Run A config, no places, as DEEPVPARA Stage 2 / DEEPTHINK-V02), persona succinct, `--deep-model qwen3.6-35b-a3b-ud-q2kxl`, detector v3b, `--timeout-ms 600000`, ctx 4096. Requests = `runs-cut6/cut6-v02-s42.requests.jsonl` (110) rewritten (arm dt512, settings {quickFirst, alwaysComplete, deepModelId}); seed 42; seed 43 only if the one-seed paired Δ vs TV (1024) CI excludes 0 in either direction (then the two-seed scales), else the one-seed number is reported as such.
- Controls (Opus rows): **TV** = `runs-deepthinkv02/dtv-TV-v02-s{42,43}` (1024), **D** = `runs-deepvpara/dv-D-v02-s{42,43}`, **K** = `runs-cut6/cut6-v02-s{42,43}`. Judge: Opus judge.v1 N = 4, 110 ids, `--system dt512v02-H-opus`, v0.2 refs 1e2668c488a1 / questions c883053b0595. No Haiku stage (measurement; the slice rule applies to decisions, not to this row).
- Driver `arms/_lib/arm.sh arms/dt512v02/arm.conf`. Script-only scoped exception as DEEPTHINK-V02; exposure logged.
## Report
Raw / floor-adjusted (questions.v02-new strata, D_decl 0.306) / above-decline with CIs, win-rate, paired Δ vs TV, D, K with CIs, per-category Δ vs TV, thinking stats and p50 time vs TV's 133–137 s. Bar reading as DEEPTHINK-V02 ("floor-adj CI low > 0.50 and win-rate > 0", else "point above / below, CI …").
## Stop rules and budget
Disk ≥ 25 GiB (33), swap ≤ 8 GB, heavy lock, one MoE server, detector never stopped. Mini ≤ 3 h per seed (expected 110 × ≈ 75 s ≈ 2.3 h). Opus ≤ 220 (+ 220 on seed 43). 0 Haiku.
## Outputs
`arms/dt512v02/DT512V02.md` (≤ 40 lines), `aggregates/`, `arm.conf`; traces/judgments in `blind/bench-v02/runs-dt512v02/`. QUEUE entry by the coordinator.
