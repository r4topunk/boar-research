# NUMGUARD-FINAL: is the merge candidate (the r2 numeric guard + NUMGUARD-2's closed-book step, one patch, one deps option) safe and complete? (frozen 2026-10-15, coordinator subagent)

Deterministic-gate arm (0 judge calls). Context: NUMGUARD-r2 (criterion 5c69f4fc…, patch e6a5af54…) failed only its own check (b), which was a coordinator threshold error (QUEUE ruling 21:07: (b) becomes agreement with the review's expected column). NUMGUARD-2 (criterion 209c103c…, patch b182609c…) PASSED the closed-book step on the r1 guard. This arm verifies the two together as ONE merge-ready patch from a new freeze; everything is regenerated.

## Tags
Tags: none
Ruleset: 30
<!-- deterministic-gate arm: probe matcher + 0-LLM route replay + deterministic scorer + byte comparison; no judge. -->

## Question
Arm **NGF** = cut 7 + `tools/numguard-final.patch` with NUMGUARD=1 and NUMGUARD_NORETRIEVE=1 (the eval runner's env fallback for `deps.numguard = { guard: true, skipRetrieval: true }`), versus **OFF** (v01-ng-off-s42 = cut 7 behaviour), **cut 7** (arms/mathroute/runs/mr-A-s42) and **r2** (ngr2-A-s42, v01-ngr2-on-s42). Used for: the PR-1 follow-up commit to the app maintainer; not a bar lever.

## Fixed inputs
- Patch `tools/numguard-final.patch` sha256 **08b742a1a7d46554181a95c25c0dac7c6d69edaed9bac0c86ab32107356224f2** (diff -ruN vs clean wt/cut7 src; 4 files: src/routing/numguard.ts ba3afe9b929f6499… (= r2, unchanged), src/routing/answer.ts 42617ed556bc0702…, src/routing/numguard.test.ts 0f663442ce8a3c47… (= r2), src/routing/answer.test.ts 269a77dccc217a90…).
  - answer.ts vs r2: the deps option becomes `numguard?: { guard: boolean; skipRetrieval: boolean }` (unset = env fallback `{ guard: NUMGUARD === "1", skipRetrieval: NUMGUARD_NORETRIEVE === "1" }`, off otherwise). After planAnswer: when the guard fired, skipRetrieval is on and plan.retrieve is true, set plan.retrieve = false and replace the `retrieve:yes` code with `retrieve:no`, `numguard:noretrieve`. Reaching planAnswer already means no calculator / arithmetic / travel / FACTS shortcut answered (as in NUMGUARD-2). Guard logic byte-identical to r2.
  - answer.test.ts vs r2: the 3 r2 cases use the object option; 2 new cases: (1) the detector fires on "2.2 bar … psi" → retrieve not called, codes contain numguard:fired + retrieve:no + numguard:noretrieve and not retrieve:yes (and with skipRetrieval false, retrieval runs and retrieve:yes stays); (2) the detector fires on the 20,000 mAh × 3.7 V question → the calculator answers, no numguard:noretrieve, no generation, no retrieval.
- Tree: kiln-local/be-0cfd4a77-cut7-numguard-r2 reused, its 4 routing files replaced by the patched ones (src identical to wt/cut7 + this patch), ARM `cut7+numguard-final`. Runner tools/run_ngf.sh (= run_ngr2.sh with the final pins: answer.ts 42617ed556bc0702, numguard.ts ba3afe9b929f6499, both env flags required on this ARM); driver tools/gen_ngf.sh.
- Common: llama-server spikes/llama-b11010-cpu, --threads 4, server backend, ship profile, mmbert detector :8094 (head v3b, threshold 0.2; not restarted), seed 42, requests via arms/mathroute/tools/mkreq_mr.py (claim kit); busy.sh: one llama-server at a time.
- Probes: review/health.jsonl (32), review/benign.jsonl (15), review/multiturn.jsonl (6). Benign expected column = REVIEW-numguard.md "guard with fix": guard true on exactly b01, b02, b03, b10; false on the other 11.
- Sets (public/dev only): boar-eval/bench/slices/mathroute-v1 (26), boar-eval/bench/v0.1/questions.public.jsonl (60), boar-eval/bench/selftest/* (the 180; cooking + money 40 info only). blind/ and rnd/veil/ never read.

## Declared before the freeze
- While writing the patch (development): tsc --noEmit clean and vitest src/routing 29 files / 649 tests green on a fresh scratch copy of wt/cut7 + this patch; `git apply --check` against wt/pr1 clean. These are re-run after the freeze as the measurement for (f) and (g). No matcher, replay or generation run on the final tree before this freeze (r2's matcher/replay numbers are known; the guard module is byte-identical, so (a), (b), (e) are expected to equal r2's).

## Power
expected_delta: slice cited 6 -> 4 (= cut 7), guard-fired model-answered cited 2 -> 0; everything else = r2 (source: NUMGUARD2.md, NUMGUARD-R2.md)
n: 32 + 15 + 6 probes, 26 slice, 60 v0.1, 180 self-tests
seeds: 1 (4B path byte-deterministic on the MacBook CPU server path, SEEDGEN / RULE 27)
mde: n/a (deterministic gate: counts)
slice: n/a (own dev slice mathroute-v1)
l1_futility: n/a (deterministic-gate arm)
split: none

## Ceiling (RULE 29; 0 calls)
ceiling: 3/26 recoveries on the slice (mr-u07, mr-a02, mr-a04); safety ceiling 0/38 probe bypasses; 2 fake citations removable
bar_ceiling: 0 -> product/safety arm
launch: deterministic-gate arm, n/a
transfer: n/a (product only)

## Budget (RULE 29)
wall_cap: 1 h MacBook
calls_cap: Haiku 0 / Opus 0 / paid API 0
smoke: tsc clean + routing vitest green on the scratch copy; route replay runs on all items without error; else STOP (FAIL-INFRA)
kill_if: smoke fails; projected wall > 1.5 h
checkpoint: after the matcher stage

## Precheck (S2 of the smoke ladder, LOOP v2 §5; 0 calls)
token_projection: n/a / token_budget: n/a
disk_peak_gib: 0.1
off_baseline: v01-ng-off-s42 (v0.1, OFF = cut 7 behaviour) + mr-A-s42 (slice, cut 7)
call_pattern: none (0 judge calls; guard_match_r2 + route_replay_r2 + score_mr.py + compare_ng.py / same_answer.py)
lane: mac-gen
opus_clause: none
wall_cap_h: 1
parallelism: 1
run_type: 4b-patch

## Measurements, in order
1. tsc --noEmit + vitest src/routing on the scratch copy of wt/cut7 + the frozen patch; `git apply --check` of the patch on wt/pr1 (read-only).
2. Matcher (0 LLM, tools/guard_match_r2.mts on the final tree): health 32, benign 15, multi-turn 6. Route replay ON vs OFF (tools/route_replay_r2.mts, detector :8094, no history): v0.1 60, the 180 (+40 info), slice 26.
3. Generation seed 42, NUMGUARD=1 NUMGUARD_NORETRIEVE=1: slice 26 (ngf-A-s42) -> score_mr.py vs mr-A-s42 and ngr2-A-s42, per item, citation counts, answers > 2 sentences; v0.1 60 (v01-ngf-on-s42) -> compare_ng.py + same_answer.py vs v01-ng-off-s42 and vs v01-ngr2-on-s42.

## Verdict rule (frozen)
- **PASS** iff all seven hold:
  (a) numericGuard true on 0/32 health probes AND 0/6 multi-turn probes (with their earlier turns);
  (b) the 15 benign probes agree 15/15 with the expected column above (guard true on exactly b01, b02, b03, b10);
  (c) slice score_mr.py correct 26/26, mr-u07, mr-a02, mr-a04 correct, 0 items correct in ngr2-A-s42 -> wrong in ngf-A-s42, AND cited sources on guard-fired (numguard:fired) model-answered items = 0, AND the slice cited total = cut 7's (mr-A-s42) total;
  (d) v0.1: 0 changed answer texts (whitespace-normalised) on all 60, ngf vs v01-ng-off-s42 (any numeric-item change listed);
  (e) route replay on the 180: 0 turns changed (on_acts = fire AND guard = 0);
  (f) tsc --noEmit clean AND vitest src/routing all green, including numguard.test.ts and the 2 new answer.test cases;
  (g) `git apply --check` of the frozen patch on wt/pr1 clean.
- **FAIL** otherwise. One generation per run; no rerun except an infrastructure error before the first token.

## Stop rules and budget
Disk >= 8 GiB free before each adapter call, never two llama-servers (busy.sh, wait up to 60 min), detector :8094 never stopped or restarted, never restart Docker, the Mac mini untouched, wt/pr1 never written. No git commit/push (coordinator commits).

## Outputs and exposure
`arms/numguard/NUMGUARD-FINAL.md` (cites this sha), `PR-NOTE.md`, `aggregates/numguard-final.json`, `tools/` (numguard-final.patch + .sha256, run_ngf.sh, gen_ngf.sh), `runs/` (final-*, ngf-*, v01-ngf-*). Exposure: dev + public sets only; blind/ and rnd/veil/ not read.
