# PARJUDGE result (2026-10-07 18:06, runner; criterion PARJUDGE-criterion.md sha256 f47b3bb5…, verified OK before the first call)
**Verdict: N = 4 and N = 8 both USABLE; recommend N = 8** (highest usable). Judge Haiku 5.5 effort low (`claude-haiku-5-5`, judge.v1-low), deep35-R450 traces, bench/v0.1, seed 7, `--gap-ms 0`. 228 Haiku calls, 0 Opus, 0 mini (cap 228).

## Per level (114 calls each; reference = sequential HAIKUJUDGE A1, gap 1000 ms, 1 process; analysis.json)
| level | wall | calls/min | speedup | 429/overloaded | timeouts (>60 s) | failures / reruns | median / p90 s/call | same winner vs A1 | r BOAR mean vs A1 | ratio (Δ vs A1, 95 % CI) | pos. cons. | [usage detail removed] USD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sequential A1 | 694 s (11.6 min) | 9.9 | 1.0× | 0 | 0 | 0 / 0 | 3.52 / 4.50 | — | — | 0.566 | 96.5 % | 0.073 |
| N = 4 | 154 s (2.6 min) | 44.4 | 4.5× | 0 | 0 | 0 / 0 | 3.60 / 4.38 | **55/57** | 0.949 | 0.566 (+0.001 [−0.011, +0.013]) | 100 % | 0.073 |
| N = 8 | 145 s (2.4 min) | 47.2 | 4.8× | 0 | 1 slow call (77.7 s, ok) | 0 / 0 | 3.58 / 4.37 | **55/57** | 0.960 | 0.560 (−0.005 [−0.017, +0.007]) | 100 % | 0.074 |
κ corr ≥ 4 vs A1: N4 0.930, N8 0.895. All rows ok, 114 unique (itemId, order) per level, judgeModel claude-haiku-5-5 on every row; 114 spend rows per level (purpose `deep35-R450-par<N>-k`), 0 rate-limit/error lines in the 12 shard logs, 0 nonzero exits.

## Rule (criterion, read once)
usable = 429s ≤ 5 %, failures ≤ 2/114, same winner vs sequential ≥ 52/57.
- N = 4: 0 % · 0 · 55 → USABLE. N = 8: 0 % · 0 · 55 → USABLE. Stop rule not triggered at either level.
- **Recommend N = 8** for L1 triage at 47.2 calls/min: 57 × 2 L1 pass ≈ **2.4 min**; 110 × 2 × 2 claim-size pass (440 calls) ≈ **9.3 min** (N = 4: 2.6 / 9.9 min; sequential gap 1000: 11.6 / 44.7 min).

## Wall-time anatomy
- N = 8 gains only 9 s over N = 4: 7 of 8 shards finished in 64–84 s; shard 7 carried one 77.7 s call (lan-rsn-004/boarB, CLI duration_ms; no error, verdict ok) and ended at 145 s. Without that straggler N = 8 would be ≈ 84 s (≈ 80 calls/min). Wall at N ≥ 8 is straggler-bound, not rate-bound.
- Per-call latency did not degrade with concurrency (median 3.52 → 3.60 → 3.58 s; p90 flat). Wall per call inside a shard ≈ 5 s (≈ 1.5 s CLI start-up on top of duration_ms).
- Same-winner drift vs A1 (2/57 at both levels) is same-model sampling noise, within the 54/57 Haiku-vs-Opus figure; ratio Δ CIs straddle 0.

## Files
- tools/shard_run.sh (level runner: round-robin shards by traces file order, N concurrent judge.mjs, rerun once on exit 3/4, STOP on second death, epoch times) sha b14eb5d73b7a; tools/analyze.mjs (timing + spend + agreement; reuses arms/judge2/judge2-analysis.mjs as is, A1 in the reference slot) sha 15c6d299d9a4.
- shards-4/, shards-8/ (id lists; N8 shard 0 has 8 items, others 7). Outputs boar-eval/runs/kiln/parjudge/N4|N8/ (shard jsonl + logs + times.txt) and N4.judgments.jsonl (d83ddcf05d68) / N8.judgments.jsonl (f9cb63fd156b).

## Deviations
- Sequential wall = last `elapsed=` in the A1 log (694 s; HAIKUJUDGE.md rounds it to 11.5 min); A1 used --gap-ms 1000, so part of the 4.5× is the removed gap (≈ 114 s of 694), not concurrency.
- A JUDGE2 gemma4q2 judge (local model via shim on the mini, not the Claude [usage detail removed]) was running concurrently on the MacBook; it does not share the rate limit but shares CPU.
- 429 counting: log grep + spend-row count; spend rows carry no error field, so "0" means no CLI call ended in a rate-limit stop, not that the CLI never retried internally (the 77.7 s call may be an internal retry).

## UNKNOWN
- Whether the 77.7 s straggler is an internal overload retry (CLI hides it) or random tail; one occurrence in 228 calls. If it is rate-related, N = 8 is near the knee.
- Levels > 8, and behaviour when other team agents use the [usage detail removed] at the same time (in this window no other judge.mjs on the [usage detail removed] was running per ps; other Claude sessions not measured).
- Throughput for Opus or Sonnet judges at N = 8 (not tested; Opus rate limits are tighter).
- Straggler mitigation (more, smaller shards or a per-call timeout < 180 s) needs a harness change; not done (no harness edit).
