# NOREPACK (W63, 2026-10-21): does llama-server --no-repack make the MacBook and the mini agree? (0 LLM, 0 paid, 80 generations, no source change)

TL;DR: **yes, 10/10.** With `--no-repack` the MacBook (M1 Pro) and the mini (M4) give byte-identical answers at seed 42; with default repack they agree on 1/10.
Cost: none on the mini decode, MacBook decode -16 %, prefill is FASTER (+55 % both hosts). n = 10 ids, one seed: a strong lead, not yet a rule.

## Setup
- First 10 sorted ids of ruler/ids/stage1-pool.ids (dng-002, lan-cmp-002..005, lan-exp-002..005, lan-exp-007), requests = MINI-BASELINE K1 v01 rows unchanged (runId nr), tree be-0cfd4a77-cut7-litepacks (answer.ts 0d1ac07d), Qwen3-1.7B Q4_K_M, seed 42, temp 0.7, llama-server b11010 (4bc272f), -t 4, LITEDECLINE_OFF=5.
- Flag pass-through: the adapter's `BOAR_SERVER_EXTRA_ARGS` ("--reasoning off" vs "--reasoning off --no-repack"; recorded in each trace as runtime.versions.server.extra_args). No engine/llama.cpp edit.
- Arms (each host: default x2, no-repack x2, sequential, no other job on that host except the mini detector): tools/norepack_mac.sh, tools/norepack_mini.sh + norepack_mini_all.sh (mini_gen.sh copy, 2-slot guard), tools/norepack_agg.py -> aggregates/norepack.json. Traces in norepack/traces (MacBook) and norepack/mini.
- MacBook detector :8094 was down, so I started one temporarily (same GGUF/args as the mini's) and stopped it after; the mini detector was never touched. The MacBook binary has a stale rpath: recreated a symlink at the old scratchpad path (outside the repo).

## Identity (answer text byte-identical / first 32 words identical, of 10)
| pair | text | w32 |
|---|---|---|
| mac default vs mac no-repack | 2 | 3 |
| mini default vs mini no-repack | 2 | 3 |
| mac default vs mini default (the MINI-BASELINE gap) | 1 | 2 |
| **mac no-repack vs mini no-repack** | **10** | **10** |
| mac default vs mini no-repack | 2 | 3 |
| mac no-repack vs mini default | 2 | 3 |
Within-host repeats (same binary, -t 4): mac default 10/10, mini default 10/10, mac no-repack 10/10, mini no-repack 10/10 (deterministic). Prompt tokens identical in every arm.

## Speed (median over the 9 rows that generated; per-arm repeats agree within 5 %)
| host | decode tok/s default -> no-repack | prefill tok/s default -> no-repack | sum totalMs default -> no-repack |
|---|---|---|---|
| MacBook | 49 -> 42 (-16 %) | 205 -> 314 (+53 %) | 56.0 s -> 42.0 s |
| mini | 52.3 -> 52.8 (0 %) | 236 -> 380 (+61 %) | 45.5 s -> 31.9 s |

## Reading
- The cross-host divergence is the REPACK weight layout (CPU-specific interleaved kernels: I8MM/SME on the M4 vs DOTPROD on the M1); the plain GGML path is bit-reproducible across the two chips for these rows. CPU-feature list in MINI-BASELINE stays as the mechanism candidate; this arm confirms the repack layout is the lever.
- Consequences: (1) MacBook and mini traces become pairable once both run `--no-repack` (kills the "mini baseline only" rule for text, not for judged results); (2) no-repack is a different decode path from the shipped phone path (Android uses repack): its text differs from default on 8/10 rows, so it is a measurement tool for cross-host work, not a claim-number change. Whether quality differs is unmeasured (0 judge calls).
- Caveats: n 10 ids, one seed, one binary, and the 4 default-vs-default repeats show determinism only within a host. Next cheap step: the 97-row MAIN set with --no-repack on both hosts (about 7 min each) to confirm 97/97 and to judge default vs no-repack quality on the 45 % that differ.
