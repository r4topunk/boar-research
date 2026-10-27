# CUT7 (2026-10-07, runner): cut 6 + FACTS r6. All gates PASS; FACTS fires 0/110 on v0.2 held-out and 0/58 on V-para → **ADOPT on gates alone** (zero-fire clause). 0 judge calls.
Criterion CUT7-criterion.md sha 2d430a70… (`shasum -c` OK before reading; not edited). Metric on v0.2 / V-para unchanged by construction; the only measured effect stays the v0.1 projection **+0.027** (FACTS-JUDGE.md, 8 fires).

## Build
| item | value |
|---|---|
| worktree | wt/cut7, branch coord/cut7 (local, not pushed), node_modules → wt/detmax/node_modules (as wt/facts) |
| base | 5e5567ca (coord/detmax) = cut 6: tree-hash (bench-app/scripts/tree-hash.mjs) b0f53fe0d30a… = 0cfd4a77 + detmax-on-cut4 patch 824e0b35… (both recomputed today) |
| applied | arms/facts/facts-r6.vs-cut6.patch, sha 0eee6a0b… (`shasum -c` OK), `git apply --check` clean; no other change |
| commit | **6d0b93b191b4dc4290cb22997bcf3bede17cec05** (5 files, +825) |
| tree-hash | **7c96e59e001b6273baa4f8dcaa7c696c1aa8f356321914b29e38fe58a900cf79** |
| cut7 vs cut6 | arms/cut7/cut7.vs-cut6.patch = `git diff 5e5567ca 6d0b93b1`, sha **0eee6a0b…** (byte-identical to facts-r6.vs-cut6.patch and to wt/facts 98db9827's diff) |

## Gates (all PASS; outputs in arms/cut7/gates/)
| gate | bar | result | output |
|---|---|---|---|
| G1 | tsc 0 errors, full vitest green | tsc exit 0, 0 lines; **118/118 files, 1346/1346 tests** | g1.out.txt, g1-tsc.log, g1-vitest.log |
| G2 | 7/8 v0.1 targets, answers identical to r6 | **7/8 (trv-002 judge-only)**; g2 output byte-identical to g2-precheck-r6; facts-check jsonl byte-identical to facts-check-r6.jsonl | g2-precheck-cut7.out.txt, facts-check-cut7.jsonl |
| G3 | 0 fires v0.1 non-target / safety / V-exact; dev chat 2 known | **0/52, 0/12, 0/11; chat 2/192 (v2-045, v2-054, same as r6)** | facts-check-cut7.out.txt |
| G4 | replay non-target raw identical to cut 6, 52/52 | **52/52** vs saved replay-detmax.jsonl and 52/52 vs a fresh wt/detmax replay; cut7 vs r6 60/60; 8 targets fast→instant | g4-compare-cut7.txt, g4-compare-cut7-fresh.txt, replay-*.jsonl |
| G5 | warm p95 ≤ 0.2 ms, cold ≤ 250 ms | warm n=5,500 p50 0.054 / **p95 0.090** / p99 0.155 / max 0.331 ms; cold (module load + first call, 5 fresh processes) **111–129 ms** | g5-cold-cut7.txt |

## Fire count (tools/fire_count.mts; deterministic, no LLM; arms/cut7/fire-count.md)
Queries = the exact `item.question` of the cut 6 claim-run requests (s42; s43 queries verified identical in-process), wired condition of answer.ts (not PT/ES/health/card-emergency → factsAnswer). Detector not simulated → upper bound.
| set | total | fired | fired ids |
|---|---|---|---|
| v0.2-new held-out (Run A; all 110 ∈ ship-all.en.ids) | 110 | **0** | — |
| V-para (Run B, all 58 incl. 7 venue) | 58 | **0** | — |
| v0.1 public + safety (Run A, 72; not blind, for completeness) | 72 | 8 | the 8 known v0.1 targets; safety 0/12 |
Engine-level confirmation (tools/replay_compare.py): replay-retrieval.sh (real `answer()`, LLM stubbed, gate + detector taken from the cut 6 claim traces) on wt/detmax vs wt/cut7: v0.2 **110/110 identical** (instant tier 4 → 4), V-para **58/58 identical** (7 → 7), v0.1 64/72 (only the 8 targets fast → instant).

## Judge
Skipped per the zero-fire clause: **0 judge calls**, 0 cut 7 LLM traces produced. Judged table: none (no fired ids). Projected Δ on the full-set ratio: **0.000 on v0.2 held-out and V-para** (Σ Δ item rubric = 0 over any denominator; CLAIM-RESULTS-cut6 headline 0.512 / V-para 0.413 stand for cut 7). v0.1 full/EN view: +0.027 projected (r2 judge on the 8 fires, not re-judged).

## Why non-fired items cannot change (code path, wt/cut7 src/routing/answer.ts)
The only engine edit outside src/rag/facts.* is the import (l. 82) and one block inside the instant section (l. 648 `if (!req.reuseSources && req.tier !== "deep")`, l. 721–731): `fact = deps.facts === false || learned?.fire || PT || ES || health || cardEmergency ? null : factsAnswer(req.query)`; `if (fact) { … return }`. When `fact` is null nothing is emitted, no state is written (facts.ts holds only its own lazy alias index, l. 182–183), and control falls through to the cut 6 code unchanged. The adapter passes `query: q.question` with no history (runner/adapter.ts l. 779). Every other path (snakebite, co-hazard, numbers, small talk, calculator, arithmetic, travel distance, places) runs before it and is untouched. Hence 0 fires ⇒ cut 7 traces = cut 6 traces for all 168 v0.2/V-para items, modulo latency fields (+≈0.1 ms per call, ≈100 ms once per process for the cold index).

## Verdict (read once)
All gates PASS; fired = 0 on v0.2 and on V-para → **ADOPT cut 7 (commit 6d0b93b1, tree 7c96e59e…) as the claim build on gates alone**: product gain (instant table answers), held-out and V-para metrics unchanged.

## Deviations
1. G5 cold-load script of r6 was not saved; reconstructed as tools/g5_cold.mts (same four numbers, fresh process per run). Measured on the MacBook, not the mini.
2. G4 run with `--tasks-from boar-eval/runs/kiln/detmax/ctl-v01-s44.traces.jsonl --compress` (FACTS.md names ctl-v01-s44 without its dir); a fresh wt/detmax replay with the same args confirms 52/52 too.
3. No mini replay of 5 non-fired ids with the LLM (step 5 is conditional on fires > 0); replaced by the full-set MacBook engine replay above. Mini untouched (36 GiB free, no lock taken, detector not started).
4. Fire-count source = the claim-run requests files (what the runner actually fed) instead of the bench question files directly; ids checked against questions.v02-new.jsonl ∩ ship-all.en.ids (110/110).

## Exposure log (all script-only; nothing displayed)
- tools/fire_count.mts read: blind/bench-v02/live/v0.2/questions.v02-new.jsonl (ids only), blind/bench-v02/runs-ship/ship-all.en.ids, blind/bench-v02/runs-cut6/cut6-v0{1,2}-s4{2,3}.requests.jsonl, blind/V-para/runs-cut6/cut6-vpara-s4{2,3}.requests.jsonl.
- replay-retrieval.sh read the same s42 requests + cut6-{v02,v01,vpara}-s42.traces.jsonl (gate/detector codes); outputs blind/{bench-v02,V-para}/runs-cut7/replay-*.jsonl/.stderr.txt (contain search queries; stay in blind/). tools/replay_compare.py printed counts/ids/tiers only.
- One schema probe printed key names, types and counts of questions.v02-new.jsonl, items.jsonl and a requests file (no values).
- Left blind/: ids, counts, the summary JSON fields n/retrieved/identicalRaw, tier labels. No FACTS text from a blind item exists (0 fires). No question, gold, rubric or reference text reached the runner's context.

## UNKNOWN
- No device smoke: no device available. Cut 7 adds a 761 KB asset (facts.v1.json, 760,970 B) and ≈ 107–129 ms cold load on desktop; phone cold load unmeasured.
- Learned detector not simulated in the deterministic count (it can only suppress fires; the replay used the trace detector and agrees: 0).
- FACTS benefit on held-out is 0 by construction of these sets; real-user recall stays 60–70 % on fresh phrasing (FACTS-r6-SET4.md).
