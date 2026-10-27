# MOESCREEN criterion (frozen 2026-10-07 before any download). Coordinator, overnight autonomous loop (r4to: "continue until 8am").
Decision 3 of HANDOFF-2026-10-07 executed under the overnight mandate; logged as such.
Question: does Qwen3.5-35B-A3B (UD-Q2_K_XL, unsloth) know more than the current deep tier Qwen3.6-35B-A3B and the 4B, closed-book?
Setup: Mac mini (M4 16 GB), llama-server as in arms/deepread (same binary/version as DEEPREAD; record it). Model file
unsloth/Qwen3.5-35B-A3B-GGUF UD-Q2_K_XL (≈ 12.2 GB), downloaded with a generic UA to the mini, DELETED after the run.
Pre-gates (any fail → stop, delete, report): free disk after download ≥ 25 GiB; model loads; smoke on 3 v0.1 items: decode ≥ 5
tok/s, 0 thinking/hidden tokens in the output, 3 non-empty answers; peak RSS ≤ 13 GB.
Run: CLOSED-BOOK (no retrieval, no context) on v0.1 EN 57 (ids anvil/exp/outofkit/v01-en-ids.txt), 1 seed (s42), thinking off,
prompt/sampler/max-tokens identical to the deep35 closed-book row of the ORACLE TABLE if one exists (arms/deepread), else to the
DEEPREAD R450 run minus the context block; the deviation is recorded. Traces to boar-eval/runs/kiln/moescreen/.
Judge: judge.v1 Opus (-med as the ORACLE rows), 114 calls, refs bd235bb9 (desktop), paired on the same 57 vs (a) the 4B
closed-book row and (b) the deep35 closed-book row if present; else (a) only and the result is a knowledge number, not a verdict.
Verdict: GO (Qwen3.5 becomes the deep-tier candidate) if paired Δ vs deep35 closed-book ≥ +0.03 AND vs 4B closed-book ≥ +0.05;
NO otherwise. No rescue, 1 seed only (screen). Gemma 4 26B-A4B UD-Q2_K_XL runs the same protocol only if this run is judged
before 05:00 and disk allows; separate result file, same verdict rule.
Never: blind/, v0.2, V-para. Never restart Docker on the mini. Shared detector port: do not start one (closed-book needs none).

## Addendum 1 (2026-10-07 02:36, coordinator, before the deep35 run): the deep35 closed-book comparator row does not exist, so the
GO/NO rule cannot be applied to the Qwen3.5 number (0.603, Δ vs 4B +0.116). Pre-registered: run Qwen3.6-35B-A3B UD-Q2_K_XL (deep35,
already on the mini) CLOSED-BOOK with the exact Qwen3.5 protocol (4B closed-book row protocol: anchor.v1 prompt ea2f484e, max 450,
0.7/40/0.95/0.05, seed 42, thinking off, same llama-server b11010 and runner moescreen-anchors.py ed1decad…), 57 items, judge.v1
Opus 114 calls, same refs bd235bb9. Then apply the ORIGINAL rule unchanged: GO if Δ(Qwen3.5 − deep35) ≥ +0.03 AND Δ(Qwen3.5 − 4B)
≥ +0.05; NO otherwise. Same rule for Gemma 4. Runs after the Gemma 4 run, only if it can finish (incl. judge) before 08:00.
Deep35 file stays on the mini (it is the current deep tier). Disk note: free space dipped to 24 GiB during the runs (swap/logs),
below the 25 GiB policy by 1 GiB, transient; GGUFs deleted after each run.
