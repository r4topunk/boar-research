# MP4B: the engine's own multi-pass path (decompose → research → synthesize) on the 4B — NO at the slice (criterion arms/deepiter/DEEPITER-criterion.md sha 432fddf9…, arm M; 2026-10-10)

TL;DR: with `alwaysComplete: true` and no deep model the engine runs `runDeepResearch` (≤ 5 LLM calls on the 4B, ≤ 3 retrievals). On the random20-v02 slice (s42) it scores the same as the single-pass 4B: Haiku paired Δ **−0.007 (−0.036…+0.023)**, floor-adj −0.008, head-to-head 7 ↑ / 4 = / 9 ↓, wins 0/0 → futility rule met (Δ ≤ 0 and h2h ≤ control) → **NO**, not a near-miss. Cost ×4: p50 26.3 s vs ≈ 6 s, answers 393 tokens median (the 4B's single pass ≈ 51 words). The 4B side stays closed; multi-pass was the last untested 4B-side mechanism.

| | M (multi-pass 4B, cut 7, MacBook server backend) | C (single-pass 4B, mini, same backend) |
|---|---|---|
| Haiku 5.5-low ratio (20 ids) | 0.534 (0.444–0.620) | 0.541 (0.461–0.613) |
| floor-adj | 0.411 | 0.420 |
| wins / ties / losses vs ref | 0 / 0 / 20 | 0 / 1 / 19 |
| mode | multipass 15, single 5 (health / no-retrieval tasks) | single |
| generation events / item | 5 (median) | 1 |
| p50 / p90 total | 26.3 s / 37.1 s | ≈ 6 s |

Method: tree `kiln-local/be-0cfd4a77-cut7` (0cfd4a77 + cut 7 patch 0fba26b8…, tree 7c96e59e…) with adapter boar-eval 4a22a4e (runMultipass wired to the tree's `runDeepResearch`; engine code untouched); `tools/local-run.sh` (server backend, llama-server b11010 CPU, 4 threads, ship profile, mmbert v3b detector on the MacBook's :8094, noplaces); requests = C's s42 with `alwaysComplete: true` (sha 9ba23a08…); traces `blind/bench-v02/runs-mp4b/mp-M-v02-s42-slice.traces.jsonl` (sha 62333738…); L1 via `arm.sh l1` (REPLAY=1), Haiku N = 4 both orders vs C's Haiku rows; aggregates in `aggregates/`. Backend caveat: M ran on the MacBook (M1 Pro) and C on the mini (M4), both llama-server; times are not directly comparable across machines, the ×4 is the call count.

Not run: full 110, Opus. Post-hoc split: none. Exposure: v0.2 1 slice generation + Haiku 20 ids (40).
