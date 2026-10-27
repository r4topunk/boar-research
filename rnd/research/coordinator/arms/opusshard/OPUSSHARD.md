# OPUSSHARD result (2026-10-08): Opus judge.v1 in N = 4 shards, 20-call probe
Criterion: `OPUSSHARD-criterion.md`, sha256 b78c9550ed1e15a6f7b0a2b0b0a673e0fb9df6f05473363276bcf0b929dea4d9 (verified before the run, unedited).
Setup: traces deep35-R450 (sha12 05710eee2f92), reference rows deep35-R450.judgments.jsonl (sha12 b40265bf921b, Opus judge.v1 sequential, gap 5000). bench/v0.1, log line showed refs bd235bb9811f, questions 568b3ececd8a. `--judge-model opus` (claude-opus-5-5, judge.v1, no --effort), `--gap-ms 0`, seed 7, `--system opusshard-probe`. Runner: `tools/run.sh N` (round-robin shards, exit 3 -> wait 60 s and rerun; none occurred). No other judge job was observed to fail; load on the machine was whatever ran at the time (not controlled).
Ids (first 10 of signal20.ids present in traces, all have reference rows): dng-005, lan-exp-002, lan-hlt-001, lan-rsn-001, lan-rsn-003, lan-rsn-005, trv-002, trv-004, vit-cry-001, vit-cry-002.

| Measure | N = 4 probe | Bar |
|---|---|---|
| calls / rows / unique (itemId, order) / ok | 20 / 20 / 20 / 20 | 20 ok |
| wall s (first start to last end) | 57 (shards 29, 37, 39, 57) | - |
| calls/min | 21.1 | - |
| 429 / rate-limit exits (exit 3), resumes | 0 / 0 / 0 | <= 1 |
| structured-output failures | 0 | <= 1 |
| same winner vs sequential (10 items, orders combined) | 10/10 | >= 9 |
| ratio probe / sequential (same 10 items) | 0.5608 / 0.5743 | - |
| Δratio | -0.0135 (boot CI -0.025 to -0.002) | abs <= 0.03 |
| position consistency probe / sequential | 100 % / 100 % | - |
| Pearson (BOAR rubric mean), kappa corr>=4 | 0.988, 1.0 | - |

Rule (quoted): "USABLE (adopt N = 4 for Opus L2/claim runs, addendum to L1-PROTOCOL + CLAIM-RUNS method note) if: 429 <= 1 of 20 AND failures <= 1 AND same winner >= 9/10 AND |Δratio| <= 0.03. Otherwise NOT USABLE: keep sequential; optionally one more probe at N = 2."
Verdict: **USABLE at N = 4** (0 <= 1, 0 <= 1, 10 >= 9, 0.0135 <= 0.03). The optional N = 2 probe was not run (not needed); Opus calls used: 20 of 40.
Caveats: 10 items, short calls (median about 3-10 s, quicker than the 5 s-gap sequential reference implies), so 429 behaviour under a 110 x 2 x 2 claim pass is still unmeasured; Δratio is slightly negative with a CI that excludes 0 on 10 items (small, within bar). Files: probe.judgments.jsonl, N4/ (shard logs, times.txt, ids), ref10.judgments.jsonl, analysis-N4.json (judge2-analysis.mjs reused as in PARJUDGE).
