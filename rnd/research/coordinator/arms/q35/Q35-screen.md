# Q35 screen result: Qwen3.5-4B as the 12 GB default reader (run 2026-10-05, frozen criterion Q35-criterion.md sha 187bbae9…)

TL;DR: **FAIL. Closed-book ratio 0.437 vs bar 0.517 (baseline 0.487, Δ −0.050); cw 45 vs 30. Q35 ends here (stop rule). No full-engine L1.**

Model: `Qwen3.5-4B-Q4_K_M.gguf` from unsloth, 2,740,937,888 B, sha256 `00fe7986ff5f6b463e62455821146049db6f9313603938a70800d1fb69ef11a4`. Mini llama.cpp `llama-b11010/build-cpu` (0.4.1-dev, 4bc272f) loads `qwen35` fine.

## Harness
- Anvil's `server-anchors.py` unchanged except a `--seed` flag (`server-anchors-seed.py`), seed 44 per the criterion (Anvil used 42): anchor.v1, bare question, no tools, sampler 0.7/40/0.95/0.05, max_tokens 450, ctx 4096, `-t 4`, `enable_thinking=false`, run through `<runner>/bin/run-heavy` (801 s).
- Judge: `boar-eval/harness/judge.mjs --bench bench/v0.1 --effort medium` (judge.v1-med), both orders, 114 calls, 0 errors. Ratio from Anvil's `ratio.py` (same code as the baseline). Same script on the stored Qwen3-4B control rows reproduces 0.487 (pass 10 / cw 30 / fail 17).

## GO bars
| bar | result | verdict |
|---|---|---|
| closed-book ratio ≥ 0.517 | **0.437** (boar mean rubric 2.16 vs 2.40; pass 2 / cw 45 / fail 10; control 10 / 30 / 17) | **FAIL** |
| decode ≥ 0.8× Qwen3-4B | llama-bench tg64, idle mini, `-t 4`, 2 runs × 3 reps: 23.20 / 23.07 vs 27.47 / 27.49 tok/s = **0.842×** (server decode during the screen: 22.6 tok/s) | PASS |
| peak RSS ≤ Qwen3-4B + 0.5 GiB | 4k ctx, 3,871-token prompt + 225 out: **5.47 vs 5.42 GiB** (Δ +0.05), ps sum over llama-server procs, CPU/BLAS build with default mmap (absolute values are desktop, not phone) | PASS |
| 0 empty answers | **0** / 57 | PASS |
| no thinking text in answers | **0** think leaks (no `<think>`, no `reasoning_content`, no warnings) | PASS |

Other: 1 answer hit the 450-token cap. Model size is 2.54 GiB vs 2.32 GiB (Q4_K Medium, 4.21 B vs 4.02 B params).

## Verdict
Speed and memory are fine, quality is not: the ratio is 0.05 below baseline and 0.08 below the bar, with more confidently-wrong answers (45 vs 30), consistent with the desk evidence (AA-Omniscience ≈ baseline) and with the Qwen3.5-9B tie. Closed-book, the 4B-class Qwen3.5 reader is worse than Qwen3-4B-Instruct-2507. Caveat: seed 44 here vs the control's seed 42 (the criterion froze 44); a 0.05 gap on 57 items is inside what one reseed can move, but the bar needed +0.03 and the result is below baseline, so a rerun is not warranted. Not run: full-engine L1 (a FAIL ends Q35).

## Files (this directory)
`runs/q35-4b-s44.traces.jsonl`, `runs/q35-4b-s44.judgments.jsonl`, `runs/judge.log`, `server-anchors-seed.py`, `rss35.py`, `bench35.sh`. GGUF deleted from the mini after the run (DISK-LOG.md, MODELS.md).
