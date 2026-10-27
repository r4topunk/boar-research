# G4E4B screen result: Gemma 4 E4B QAT Q4_0 as the 12 GB default reader (run 2026-10-05; criterion sha256 d62e54df2f8b6f9f96d87ae1cd32f7d0b8a18ebb002ba307b40cc6d79749a51d, the rewritten non-empty file)

TL;DR: **FAIL on quality only. Closed-book ratio 0.495 vs bar 0.517 (baseline 0.487, Δ +0.008, a tie); cw 26 vs 30, pass 21 vs 10. Decode, RSS, empties and leaks all pass. G4E4B ends here (stop rule); no full-engine L1.**

Model: `gemma-4-E4B_q4_0-it.gguf` saved as `gemma-4-E4B-it-qat-Q4_0.gguf`, 5,154,941,280 B, sha256 `676c35070db6dbe52f93e9c864ee0fba4eddea94b9c875d9cb10daff453fbaee` = the boar-eval adapter MODELS sha (verified). Mini llama.cpp `llama-b11010/build-cpu` loads `gemma4` fine.

## Harness
- Same as Q35: Anvil's `server-anchors.py` + `--seed` (`../q35/server-anchors-seed.py`), seed 44, anchor.v1, bare question, no tools, sampler 0.7/40/0.95/0.05, max_tokens 450, ctx 4096, `-t 4`, inside the heavy lock (574 s).
- Chat template: the GGUF's own Jinja template via `llama-server --jinja`, thinking off (Gemma only thinks when `<|think|>` is in the system prompt, which the harness never adds; `enable_thinking=false` is also sent). Not separately compared with the engine's Oct-1 template; no channel/think tokens appeared in any answer.
- Judge: `boar-eval/harness/judge.mjs --bench bench/v0.1 --effort medium` (judge.v1-med), both orders, 114 calls, 0 errors. `ratio.py` same as baseline (control re-scored 0.487 in the Q35 run).

## GO bars
| bar | result | verdict |
|---|---|---|
| closed-book ratio ≥ 0.517 | **0.495** (mean rubric 2.43 vs 2.40; pass 21 / cw 26 / fail 10; control 10 / 30 / 17) | **FAIL** |
| decode ≥ 0.8× Qwen3-4B | llama-bench tg64, `-t 4`, 2 runs × 3 reps each: Gemma 23.46 / 23.79 vs Qwen 27.27 / 27.04 tok/s = **0.87×** (server decode 22.5-23.4 tok/s) | PASS |
| peak RSS ≤ 7.0 GiB at 4k | 3,871-token prompt + 225 out: **2.95 GiB** (Qwen3-4B 2.96 GiB, same method). ps sum of llama-server procs; mmap'd PLE tensors are not resident, and the mini was swapping a little, so RSS under-reads vs a footprint number (the Q35 run read 5.4 GiB for the same Qwen file); either way far under 7.0 | PASS (soft) |
| 0 empty answers | **0** / 57 | PASS |
| no thinking/channel tokens | **0** leaks (regex for channel/think/turn tokens, no warnings, 0 answers at the 450 cap) | PASS |

## Decode: the Oct-1 2.5 tok/s was the host
Mini state, before: 14:21, load 2.18, swap used 1744 MB, swapouts 229,908; after (4 bench runs): load 3.46, swap used 2015 MB, swapouts 249,292 (Chrome/WindowServer were the top CPU users; not fully idle, swap grew ~270 MB during the bench). Even so Gemma ran 23.5-23.8 tok/s, steady across runs, so the 2.5 tok/s trace figure (PLE thrash on a loaded, swapping host) does not reproduce: Gemma decodes at ~0.87× the 4B on a normal mini. File 4.79 GiB vs 2.32 GiB.

## Verdict
Gemma 4 E4B is the first same-class reader that does not lose closed-book (cw 26 vs 30, pass 21 vs 10), but +0.008 is a tie, 0.022 short of the +0.03 bar and well inside noise on 57 items (seed 44 here vs control seed 42). Per the frozen rule a FAIL ends G4E4B. Phone-side speed and RAM (7.5 B params in file, 4.6 B matmul) remain unmeasured and were not part of this screen. Not run: full-engine L1.

## Files
`runs/g4-e4b-s44.traces.jsonl`, `runs/g4-e4b-s44.judgments.jsonl`, `runs/judge.log`, `rss35.py`, `benchg4.sh`. GGUF deleted from the mini (MODELS.md, DISK-LOG.md).
