# LESPORT-L1 result: judged parity of the LES fork (llama-omni 0b74404c, bank 1280) vs llama-server b11010, deep35 R450: **TRANSFER**

Criterion: `LESPORT-L1-criterion.md` sha256 `5756268cabdaef19a88a6aa45afbf845cb402bd8f777f82b0e914a0316d217bf` (= sibling .sha256, verified 19:3x before start, not edited). Replay of DEEPPAR-L1 (criterion sha256 `1d9745879102cc891deb11f14c5b641403a76a4f3edd30da5102dc5ae3d69be5`, TRANSFER for bmoe). Runner: Kiln, 2026-10-16 19:39-20:10 (gen 19:39-20:05, judge 20:05-20:09).

**Pre-checks (mini 19:38):** free 40.9 GiB, swap used 614 MB / 2048, no engine besides ollama and the :8094 detector. GGUF sha256 `96b9c0af5c77a4ecaabe3983175112b5ece763261c1ece12b2494b692a70dad7` = expected. Fork `llama-completion` sha256 `29cbcbc27628f9030c172b27f07f3497231d4496afba9b1c227dd5509a574580`, source `<runner>/spikes/llama-omni/src` HEAD `0b74404c9b3dfe2c6b11aebe0dd58fc23f133ee2`; experts/ 41 files. Controls: A traces `05710eee2f92`, A judgments `b40265bf921b`, B judgments `d51e87775b38` (= criterion).
**Prompts:** the 57 DEEPPAR-L1 rendered strings, still on the mini (`<runner>/kiln/deeppar-l1/out/rendered/`); 57/57 sha256 = `arms/deeppar/raw/l1/rendered-sha256.txt`; no re-render, llama-server not started. **Prompt tokens fork = control A on 57/57.**
**Generation:** `tools/run_l1.py` under `<runner>/bin/run-heavy`, one `llama-completion` process per item (as S1), `LLAMA_MOE_LOOKAHEAD_PREFETCH=1`, `-m <full GGUF> --moe-experts experts --moe-slot-bank 1280 --no-mmap -t 4 -c 4096 --temp 0.7 --top-k 40 --top-p 0.95 --min-p 0.05 --seed 42 -n 512 -f <rendered> -no-cnv --no-display-prompt`. Smoke on 3 items: 25.4 s/item, projected 24 min (kept as items 1-3 of the run, same config); checkpoints 18.5/22.2/23.6/24.2/24.6 s/item; 57/57 answers, rc 0, 0 empty, 0 `<think>` blocks, 0 hit 512 tokens (median 73 output tokens).

## Quality (Opus judge.v1, combined orders, 57 items each)
| arm | ratio [95 % CI] | floor-adjusted [CI] | win / tie / loss vs ref | pos. consistency | C / Cm / U (answer) |
|---|---|---|---|---|---|
| **LES fork R450** | **0.625** [0.581, 0.670] | 0.528 [0.472, 0.584] | 1 / 3 / 53 | 0.965 | 3.81 / 2.62 / 2.75 |
| A: deep35 llama-server | 0.634 [0.590, 0.683] | 0.541 [0.479, 0.597] | 1 / 3 / 53 | 0.965 | 3.89 / 2.66 / 2.78 |
| B: 4B llama.rn | 0.606 [0.558, 0.658] | 0.505 [0.440, 0.567] | 1 / 2 / 54 | 0.982 | 3.58 / 2.58 / 2.76 |

| paired Δ (n = 57, bootstrap 2000, items jointly) | Δ ratio [95 % CI] | Δ floor-adjusted [CI] |
|---|---|---|
| **LES − A** | **−0.010** [−0.042, +0.018] | −0.013 [−0.055, +0.023] |
| LES − B | +0.019 [−0.017, +0.056] | +0.023 [−0.023, +0.072] |

Per-item LES vs A (combined-order mean score vs the same ref; equal = tie): **LES 19 / tie 24 / A 14**. `les-R450.items.csv` has per-item means. (A and B rows reproduce DEEPPAR-L1's A/B rows, as they are the same judged controls.)

## Verdict rule (quoted) and application
"TRANSFER: paired Δ(LES − A) point ≥ −0.030 AND its 95 % CI includes 0." -> Δ = −0.010 >= −0.030, CI [−0.042, +0.018] contains 0 -> **TRANSFER**. llama-server deep-tier numbers may be quoted for an LES device plan with the caveat "judged parity on 57 dev items, 1 seed, temperature 0.7 (noise floor ≈ 0.05)". (Context, not part of the rule: LES ratio 0.625 is also >= 0.606; the CI vs A does not exclude a ≈ 0.04 loss; the result is a hair better than bmoe's -0.012.)

## Speed (mini M4, CPU, -t 4, median over 57; descriptive)
| engine | prefill s | decode tok/s | total s | output tokens | RSS / footprint GiB |
|---|---|---|---|---|---|
| LES fork, bank 1280 + lookahead prefetch (1 process per item, incl. load) | 19.8 | 17.22 | 26.4 | 73 | 2.81 (max 2.82) / 2.78 |
| A: llama-server b11010 (control traces) | 41.1 | 9.43 | 48.7 | — | ≈ 7.9 (control `peakRssMb`) |
| bmoe session (DEEPPAR-L1, for reference) | 25.7 | 8.57 | 35.3 | 76 | 9.13 RSS / 11.72 footprint (whole session) |
Decode range 16.6-17.7 tok/s; warm page cache (items run back to back, S1 showed cold = warm on this host). The mini is not a phone: UFS and fewer big cores are still unmeasured.

## Deviations from the criterion
1. Model file: the criterion says "stripped.gguf + experts/", but S0/S1 established that `stripped.gguf` is Metal-only; the CPU build needs the full GGUF + `--no-mmap` + `--moe-experts experts` (as S1's best config). Model weights are the same bytes (experts extracted from the same GGUF).
2. Raw prompt via `-f <file>` (not `-p`); fork prints a trailing `[end of text]` on EOS: stripped from 57/57 answers (spliced text = whitespace-stripped, marker removed). The splice script `tools/splice_les.py` also sets runtime/engine fields to the fork; `timing` uses fork fields; `resources` = per-item time -l RSS/footprint.
3. Judge command: `--bench bench/v0.1` added (as DEEPPAR-L1 deviation 1); first log line `57 items, 114 calls, refs bd235bb9811f, questions 568b3ececd8a` = pins. Run as 4 round-robin shards (`tools/shard_judge.sh`, `--gap-ms 0`, OPUSSHARD), allowed by the criterion; seed 7, system `oracle-R450-les` in all shards.
4. `harness/validate.mjs` does not apply: it enforces the full EvalTrace schema (adapter enum, ttft/total/retrieval/prefill ms, thermal...); DEEPPAR-L1's bmoe traces were equally non-conforming. judge.mjs reads only itemId/error/answer.text.
5. Smoke items (1-3) and the remaining 54 are separate driver invocations of the same config; `results.jsonl` holds all 57.

## Stop-rule events
None. Watchdog (5 s): free disk min 40.8 GiB (>= 25), swap used peak 614 MB (< 8 GB); no other engine process; projected wall 24 min (< 3 h); 0 items without an answer. Docker untouched. Mini after: free 40 GiB, swap 566 MB, no llama-completion/bmoe process. GGUF, experts/, stripped.gguf kept.

## Spend and wall

## Files
`les-R450.traces.jsonl` (sha256 `2157a545f5b5b334b7360b94f971321f1b2a63aeef8f0f482ca02126e8022149`), `les-R450.judgments.jsonl` (sha256 `ad35b7ba2807abfc4b7b38e0bcddf298a6be835bb9fd2ed2231c68e0d806b60d`), `les-R450.items.csv`, `tools/` (`run_l1.py`, `splice_les.py`, `analyze_les.mjs`, `shard_judge.sh`), `shards/`, `raw/l1/` (results.jsonl, per-item .err, run/gen/smoke/watch logs, judge shard logs, analysis.json; 0.8 MB). Mini copy: `<runner>/kiln/lesport-l1/`. Not committed; QUEUE entry by the coordinator.
