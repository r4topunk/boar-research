# L1CTL: signal20 paired L1 control re-judged with Haiku 5.5-low (2026-10-07 18:59, runner). Control run: no criterion, no verdict.
Per L1-PROTOCOL.md + addenda HAIKUJUDGE (Haiku 5.5-low) and PARJUDGE (N = 4 shards). 40 Haiku calls, 0 Opus, 0 mini, MacBook only.

## Inputs
| what | path | sha256 (12) |
|---|---|---|
| ids (20) | coordinator/arms/signal20.ids | 4542bfcd829d (full sha verified) |
| control traces (cut 3 = cut 6 answers, seed 44) | boar-eval/runs/kiln/speedpack-l1/spctl-v01-s44.traces.jsonl | 0a22d2b371e5 |
| Opus control judgments (judge.v1-med) | boar-eval/runs/kiln/speedpack-l1/spctl-v01-s44.judgments.v1-med.jsonl | 41de49901bfd |
| **Haiku control judgments (judge.v1-low, claude-haiku-5-5)** | boar-eval/runs/kiln/speedpack-l1/spctl-v01-s44.judgments.haiku55-low.jsonl | **c8d46a92869b** |
Check: all 20 slice answers in spctl traces byte-identical to the traces the Opus rows were judged on (g4eng-l1 ctl-v01-s44; dng-005 from g4eng-v01-s44), 20/20.

## Command
`tools/shard_run.sh` (sha df7f2eac74e2; adapted from parjudge/tools/shard_run.sh): signal20.ids round-robin into 4 shards (shards-4/), 4 concurrent
`node harness/judge.mjs --traces runs/kiln/speedpack-l1/spctl-v01-s44.traces.jsonl --out <shard>.jsonl --bench bench/v0.1 --ids <shard ids> --judge-model claude-haiku-5-5 --effort low --gap-ms 0 --seed 7 --system spctl-v01-s44-haiku55-low`,
rerun on exit 3/4, concatenate (shard files + logs + times.txt in boar-eval/runs/kiln/speedpack-l1/haiku55-shards/), assert 40 rows / 40 unique (queryId, order).

## Numbers (tools/analyze.mjs sha 56ac5baf48ae, judge-core combineOrders, disagreement = tie; analysis.txt)
- Rows 40, unique 40, ok 40; failures 0, reruns 0, 0 rate-limit lines; 40 spend rows (purpose spctl-v01-s44-haiku55-low).
- Wall 50 s (shards 45–50 s); s/call mean 3.24, median 3.28 (CLI duration); ≈ 48 calls/min. [usage detail removed] cost [usage detail removed].
- Same winner vs Opus-med: **20/20** (ref wins all 20 under both judges, 0 ties). Trivial on this slice: it is the 20 worst items by Opus correctness.
- Ratio on the 20 (never pooled): Haiku-low **0.334**, Opus-med **0.340** (Δ −0.006).
- BOAR correctness (mean of 2 orders): Haiku 1.83 vs Opus 2.03; per item Haiku lower 9, equal 8, higher 3 (largest: dng-005, vit-cry-006, vit-hum-003 −1.0; lan-rsn-001 +1.0).
- Position consistency: Haiku 100 %, Opus 100 %.
- Caveat: Opus-med (judge.v1-med) and Haiku-low (judge.v1-low) are different judge versions; this is a sanity comparison on a floor-heavy slice, not a calibration (calibration = HAIKUJUDGE, 54/57, r 0.92).

## Paste into future `<arm>-L1-criterion.md`
control judgments: boar-eval/runs/kiln/speedpack-l1/spctl-v01-s44.judgments.haiku55-low.jsonl, sha c8d46a92869b3f5c9dfbc38352ec13415747c9fa4b05905baf244f06a4fdd39f (Haiku 5.5-low, judge.v1-low, signal20 sha 4542bfcd…, seed 7, system spctl-v01-s44-haiku55-low)

## UNKNOWN
- The slice is all ref-wins, so same-winner here says nothing about Haiku's ability to detect arm wins on it; the paired Δ-ratio arm of the rule carries the signal.

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file by design (measurement / descriptive / tooling); nothing to freeze.
