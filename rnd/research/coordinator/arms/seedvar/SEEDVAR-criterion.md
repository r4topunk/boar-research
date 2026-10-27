# SEEDVAR: how much do the deep tier's claim-scale numbers move with the sampling seed? (frozen 2026-10-10 12:4x, coordinator; measurement only, no verdict rule)

Question: DEEPBO2 found the recommended deep configuration (DT512 arm H: cut 6 + Qwen3.6-35B + thinking 512) scores raw 0.533 (s42) vs 0.572 (s43) on the 51 judged V-para items, a +0.039 (+0.011…+0.072) gap between two seeds of the same configuration, while the 4B claim run's two seeds are 0.413 / 0.413 and the no-think deep tier's 0.460 / 0.474. Many decisions today rest on ±0.03 rules and one-seed numbers. A third seed of H gives a per-seed spread for the thinking tier (3 points), tells whether s42 or s43 is the outlier, and calibrates how far a single-seed deep number can be trusted.

## Fixed inputs
- Arm H exactly as DT512 (tree `be-0cfd4a77-dt512`, patch f9a1979b…, runner dt512-remote-run.sh, `--deep-model`, `--places`, detector, `--timeout-ms 600000`), requests = `dh-H-vpara-s42.requests.jsonl` with seed 44 and runId `dh-H-vpara-s44` (58 items; sha recorded in the QUEUE entry). Judge: Opus judge.v1 N = 4 on the 51 judged ids (102 calls), `--system dt512-H-opus` as the other seeds. No Haiku.
- Script-only scoped exception as DT512; exposure logged.
## Report (no verdict)
Per-seed raw ratio, floor-adjusted and win-rate for H s42/s43/s44 (and K, D two seeds for comparison); pairwise paired Δ between H seeds with CIs; the mean and SD of the three H seeds; the three-seed H number beside the two-seed one in DT512.md (as a note, not replacing the frozen two-seed result); a one-line rule-of-thumb for one-seed deep numbers (± SD) to be added to L1-PROTOCOL. Also report the Pearson r between seeds' per-item scores (does the seed noise sit on the same items?).
## Stop rules and budget
Disk ≥ 25 GiB, swap ≤ 8 GB, heavy lock, one MoE server, detector untouched; mini ≤ 1.5 h; Opus ≤ 102; one generation, no rerun except an infrastructure error before the first token.
## Outputs
`arms/seedvar/SEEDVAR.md` (≤ 40 lines), aggregates here; traces/judgments in `blind/V-para/runs-dt512/` next to the other seeds. QUEUE entry + EXPOSURES row by the coordinator.
