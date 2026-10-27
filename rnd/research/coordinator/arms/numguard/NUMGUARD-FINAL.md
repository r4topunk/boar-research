# NUMGUARD-FINAL: the merge candidate (r2 guard + NUMGUARD-2 closed-book step, one patch, one deps option). **PASS**

Criterion `NUMGUARD-FINAL-criterion.md` sha256 **6820cbc8fd1145ad31e531dad9a5f4384373c29a90de53bcdb2f88d65ac98f3c**, frozen 21:11:11, before any matcher, replay or generation run on the final tree (Ruleset 30, Precheck filled: 4b-patch, mac-gen, wall_cap_h 1, calls 0/0, parallelism 1).
Patch `tools/numguard-final.patch` sha256 **08b742a1a7d46554181a95c25c0dac7c6d69edaed9bac0c86ab32107356224f2** (diff vs clean wt/cut7, 4 files in src/routing: numguard.ts = r2 unchanged, numguard.test.ts = r2 unchanged, answer.ts, answer.test.ts). Changes vs r2: deps option `numguard?: { guard; skipRetrieval }` (env fallback NUMGUARD=1 / NUMGUARD_NORETRIEVE=1, off otherwise); after planAnswer, a guarded turn with retrieval planned gets `plan.retrieve = false` and `retrieve:yes` is replaced by `retrieve:no`, `numguard:noretrieve`; 2 new answer.test cases. Tree kiln-local/be-0cfd4a77-cut7-numguard-r2 reused (src = cut 7 + this patch), ARM `cut7+numguard-final`; runner tools/run_ngf.sh pins answer.ts 42617ed5… and requires both env flags.
Seed 42, llama-server b11010 CPU --threads 4, claim kit, detector :8094 (not restarted). **Judge calls 0** (Haiku 0, Opus 0, paid 0). Wall: generation 657 s (slice 140 + v0.1 516, no busy wait), matcher + replay ≈ 10 s, tsc + vitest ≈ 1 min.

## The seven rule checks
| check | rule | result | |
|---|---|---|---|
| (a) health / multi-turn probes pass the guard | 0/32, 0/6 | **0/32, 0/6** (turn 2 alone 5/6; earlier-turn lexicon blocks; window fires 6/6) | pass |
| (b) benign probes vs the review's expected column | 15/15 | **15/15** (guard true on exactly b01, b02, b03, b10) | pass |
| (c) slice | 26/26, 3 targets, 0 c→w vs r2, 0 cited on guard-fired model answers, cited total = cut 7 | **26/26**; mr-u07, mr-a02, mr-a04 ✓; 0 c→w; guard-fired model-answered cited **0** (mr-u07, mr-a02); total cited **4 = cut 7's 4** (same 4 items: mr-u04, mr-u08, mr-t01, mr-t06) | pass |
| (d) v0.1 60 vs v01-ng-off-s42 | 0 changed | **0/60** answers, 0 codes, 0 kept lists changed; 0 numeric items; same_answer 60/60 vs OFF and 60/60 vs r2 | pass |
| (e) route replay 180 | 0 turns changed | **0** (fire 26, guard 0); 306/306 replay rows identical to r2's | pass |
| (f) tsc + routing vitest | clean, green | **tsc clean; 29 files / 649 tests green** (2 new; 57 numguard tests) on a fresh scratch copy of wt/cut7 + the frozen patch | pass |
| (g) git apply --check on wt/pr1 | clean | **clean** (wt/pr1 6643aa9f; hunk offsets only, no fuzz) | pass |

## Per item (the 5 ever-fired slice items)
| item | p | cut 7 | r2 | final | final codes |
|---|---|---|---|---|---|
| mr-u07 2.2 bar → psi | 0.664 | refusal ✗ | ✓ model, cited [1] | ✓ model, closed-book, 0 cited | retrieve:no, numguard:noretrieve, detector:fire, numguard:fired |
| mr-a02 bus 9:40 + 2 h 35 | 0.985 | refusal ✗ | ✓ model, cited [1] | ✓ model, closed-book, 0 cited | retrieve:no, numguard:noretrieve, detector:fire, numguard:fired |
| mr-a04 20,000 mAh × 3.7 V | 0.624 | refusal ✗ | ✓ calc | ✓ calc (no closed-book step) | numguard:fired, answer:calculator-battery |
| vit-sci-003 · mr-a07 | 0.291 · 0.898 | ✓ calc | ✓ calc | ✓ calc (not guard-matched; = cut 7) | detector:numeric-guard |
Only mr-u07 and mr-a02 change vs r2; all 26 slice texts are byte-identical to NUMGUARD-2's (ng2-A-s42). No `retrieve:yes` on the two closed-book items (retrieval.raw empty).

## Worst 3 (quoted briefly)
1. mr-u07 adds unasked advice: "Most car manufacturers recommend between 30–35 psi…" (+2 sentences).
2. mr-a02 no longer leads with the answer: it ends "It arrives at 12:15." (headline 21 → 20).
3. Benign misses that stay (safe direction, by design of MF1): "15% of 80 dollars", "Convert 250 ml to cups", "How many kWh?".

## Verdict (frozen rule)
**PASS**: all seven checks hold. Merge candidate = tools/numguard-final.patch.

## Costs outside the rule
Answers > 2 sentences 5 → 7 (slice, vs r2 and cut 7); number-first 21 → 20 vs r2 (cut 7 18); p50 model-only 7.5 s vs r2 8.0 s (noise). Same costs NUMGUARD-2 reported.

## Files
tools/ (numguard-final.patch + .sha256, run_ngf.sh, gen_ngf.sh, analyze_ngf.sh; guard_match_r2.mts and route_replay_r2.mts reused), runs/ (final-tsc.txt, final-vitest.txt, final-vitest-new.txt, final-apply-check-pr1.txt, final-guard-match.jsonl/.txt, final-route-replay.jsonl/.txt, ngf-A-s42.*, v01-ngf-on-s42.*, final-score-slice.txt, final-slice-items.txt, v01-final-compare-vs-{off,r2}.json, v01-final-same_answer-vs-{off,r2}.txt, gen_ngf.log), aggregates/ (numguard-final.json, score_slice_final.json), PR-NOTE.md. The r2 tree now carries the final patch (run_ngr2.sh refuses it by design; r2 is reproducible from numguard-r2.patch).
Exposure: dev + public sets only (mathroute-v1, v0.1 public, selftest/*, review probes); blind/ and rnd/veil/ not read.
