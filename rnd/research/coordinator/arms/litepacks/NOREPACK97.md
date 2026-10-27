# NOREPACK97 (2026-10-21): --no-repack on MAIN 97 = 97/97 byte-identical across hosts, quality-neutral (Haiku 5.5-low, 130 calls, 0 Opus, 0 paid)

TL;DR: **both clauses pass.** With `--no-repack` the MacBook (M1 Pro) and the mini (M4) give byte-identical answers on 97/97 (seed 42, -t 4); vs the mini default K1 baseline paired dU = -0.012 (CI -0.030...+0.005), CE-unwarned 11 vs 12. Adopt as the cross-host pairing flag (text pairing; not the shipped phone path).
Criterion NOREPACK97-criterion.md sha 27d05cde (committed d6f85b14 before generation); cap line in NOREPACK97-budget.md (e5efb390, before judging).

## Setup
- Same system as NOREPACK/MINI-BASELINE: tree be-0cfd4a77-cut7-litepacks (answer.ts 0d1ac07d), Qwen3-1.7B Q4_K_M, seed 42, temp 0.7, -t 4, LITEDECLINE_OFF=5, llama-server b11010; flag via BOAR_SERVER_EXTRA_ARGS "--reasoning off --no-repack". Requests = lp-K1 cm+v01 rows restricted to lp-screens/main-97.ids, runId nr97. No engine/llama.cpp edit.
- MacBook and mini ran in parallel, one job each (tools/norepack97_mac.sh, norepack97_mini.sh, 2-slot guard). A temporary MacBook detector on :8094 (same GGUF/args as the mini's) was started and stopped after; the mini detector was untouched. Stale rpath symlink still in place.
- Traces: norepack97/traces/mac97-nr.jsonl, norepack97/mini/mini97-nr.traces.jsonl. Judge: tools/norepack97_judge.sh, Haiku 5.5-low N=4 both orders, 63 changed arm rows + 2 baseline rows (baseline reuses lp-screens/control lpctl-K1-main judgments where its text equals the mini baseline: 95/97), aggregation with lp-screens/tools/agg_run.py.

## (a) Identity
| pair | text | first 32 words |
|---|---|---|
| **mac no-repack vs mini no-repack** | **97/97** | 97/97 |
| mini no-repack vs mini default | 34/97 | n/a |
Prompt tokens identical on 97/97. Threshold >= 95: PASS.

## (b) Quality, mini no-repack vs mini default (63 changed answers judged)
| | default (mini) | no-repack | delta |
|---|---|---|---|
| U | 0.4107 | 0.3983 | -0.0123 (-0.0299...+0.0048) |
| CE (of 97) | 29 | 28 | -1 |
| CE-unwarned (CE among non-warned) | 12 of 51 | 11 of 53 | -1 |
| warned | 46 | 44 | -2 |
Rule: |dU| <= 0.02 and CE-unwarned up by < 3: PASS (CI includes 0).

## Speed (median over the 75 rows that generated; sum of totalMs over 97)
| arm | decode tok/s | prefill tok/s | sum totalMs |
|---|---|---|---|
| MacBook no-repack | 43.9 | 309 | 290 s |
| mini no-repack (1 job) | 53.3 | 373 | 230 s |
| mini default (MINI-BASELINE, 2 jobs in parallel; not a like-for-like speed) | 41.0 | 162 | 432 s |
10-id NOREPACK (like-for-like, single job): mini decode 52.3 -> 52.8, prefill +61 %; MacBook decode -16 %, prefill +53 %.

## Reading and caveats
- Confirms NOREPACK at 10x the size: the repack layout is the only cross-host lever; MacBook arms can now be paired with the mini 1:1 for text (judged results still need the same judge run).
- no-repack is a different decode path from the phone (repack). dU -0.012 is a one-seed point inside the rule but with 63 changed answers a real +-0.03 shift is not excluded; keep default repack for claim numbers and use no-repack only for cross-host/pairing work.
- Deviations: the cap line was added as a separate budget addendum (criterion prose had it but not in the machine-readable calls_cap form); the baseline for 2 rows was judged here because the lpctl control text differed from the MINI-BASELINE text; mini default timing is not like-for-like (2 jobs in parallel).
- Aggregates: aggregates/norepack97.json, norepack97-arm.json, norepack97-base.json.
