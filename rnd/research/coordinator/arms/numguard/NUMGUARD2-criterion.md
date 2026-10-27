# NUMGUARD-2: with the numeric guard ON, does skipping retrieval on the turns where the guard fired and no calculator/arithmetic shortcut answered remove the fake citations on model-answered numeric questions with zero harm? (frozen 2026-10-15, coordinator subagent)

Deterministic-gate arm (0 judge calls). Context: NUMGUARD (arms/numguard/NUMGUARD.md, criterion 03587d67…, PASS) recovers the 3 detector refusals on numeric questions, but the two model-answered conversions (mr-u07 2.2 bar -> psi, mr-a02 bus 9:40 + 2 h 35) still cite a fake source ([1]) because retrieval runs on them: slice cited count 4 (A) -> 6 (ng-A-s42). MATHROUTE arm B (arms/mathroute/MATHROUTE.md, `MATHROUTE_RETRIEVE=off`) removed citations on math (7 -> 0) without changing arithmetic correctness.

## Tags
Tags: none
Ruleset: 30
<!-- deterministic-gate arm: deterministic scorer + 0-LLM route replay + byte comparison; no judge. -->

## Question
Arm **NG2** = cut 7 + `tools/numguard2.patch` (superset of numguard.patch) with NUMGUARD=1 and NUMGUARD_NORETRIEVE=1, versus control **NG** = the NUMGUARD ON runs (ng-A-s42 for the slice, v01-ng-on-s42 for v0.1; same tree, same seed). Used for: the PR-1 follow-up commit proposal (a numeric question never gets a health refusal and never cites a source it did not use), not a bar lever.

## Fixed inputs
- Change (answer.ts only, on the numguard tree): when NUMGUARD_NORETRIEVE=1 AND the NUMGUARD guard fired for the turn (`numguard` true, which already requires NUMGUARD=1) AND the turn reached planAnswer (no calculator / arithmetic / travel / FACTS shortcut returned), `plan.retrieve` is set to false right after planAnswer (the place mathroute-env.patch forces it) and `numguard:noretrieve` is appended to plan.reasonCodes. NUMGUARD unset -> byte-identical to cut 7; NUMGUARD=1 alone -> byte-identical to numguard.patch behaviour (the new branch reads one more env var only when the guard fired).
- Tree: kiln-local/be-0cfd4a77-cut7-numguard (ARM `cut7+numguard`), patched in place to numguard2.patch; patch sha256 in tools/numguard2.patch.sha256; runner tools/run_ng2.sh (= run_ng.sh with the new answer.ts sha pin).
- Common: as NUMGUARD (llama-server b11010 CPU --threads 4, server backend, ship profile, mmbert detector :8094 never restarted, seed 42, claim kit requests via mathroute tools/mkreq_mr.py, busy.sh guard: one llama-server at a time on the MacBook).
- Sets (public/dev only): boar-eval/bench/slices/mathroute-v1 (26), boar-eval/bench/v0.1/questions.public.jsonl (60), the 180 self-test items of the 9 STACK packs (route replay, 0 LLM). blind/ and rnd/veil/ never read.
- "Guard-fired model-answered item" = a slice / v0.1 item whose NG2 trace carries `numguard:fired` and no `answer:calculator-*` / `answer:temperature-conversion` code (expected: mr-u07, mr-a02). "Numeric item" = numericGuard(q) true (route replay), as in NUMGUARD.

## Power
expected_delta: cited on guard-fired model-answered items 2 -> 0 (source: ng-A-s42 traces; MATHROUTE arm B 7 -> 0 with retrieval off)
n: 26 slice + 60 v0.1 + 180 self-tests
seeds: 1 (4B path byte-deterministic on the MacBook CPU server path, SEEDGEN / RULE 27)
mde: n/a (deterministic gate: counts, no significance)
slice: n/a (own dev slice mathroute-v1)
l1_futility: n/a (deterministic-gate arm)
split: none

## Ceiling (RULE 29; 0 calls)
ceiling: 2 citations removed on the slice (mr-u07, mr-a02); correctness ceiling 0 (already 26/26)
bar_ceiling: 0 (v0.1 has no guard-fired model-answered item in NG: vit-sci-003 is answered by the arithmetic shortcut) -> product/credibility arm
launch: deterministic-gate arm, n/a
transfer: n/a (product only)

## Budget (RULE 29)
wall_cap: 1 h MacBook (smoke 5 + slice 26 + v0.1 60, one llama-server at a time)
calls_cap: Haiku 0 / Opus 0 / paid API 0
smoke: tsc --noEmit clean on a scratch copy with numguard2.patch; the 5 guard-fired slice items (vit-sci-003, mr-u07, mr-a02, mr-a04, mr-a07) with both flags: rc 0, 0 empty answers, `numguard:noretrieve` on the model-answered ones, still correct; else STOP (FAIL-INFRA)
kill_if: smoke fails; projected wall > 1.5 h
checkpoint: after the smoke

## Precheck (S2 of the smoke ladder, LOOP v2 §5; 0 calls)
token_projection: n/a / token_budget: n/a
disk_peak_gib: 0.1
off_baseline: ng-A-s42
call_pattern: none (0 judge calls; deterministic scorer score_mr.py + same_answer/compare_ng + route replay)
lane: mac-gen
opus_clause: none
wall_cap_h: 1
parallelism: 1
run_type: 4b-patch

## Measurements, in order
1. Smoke (above), runId ng2-smoke-s42.
2. Slice 26 with both flags (runId ng2-A-s42, seed 42) -> score_mr.py; per item vs ng-A-s42 and mr-A-s42 (correct, cited, retrieved).
3. v0.1 60 with both flags (runId v01-ng2-on-s42) vs v01-ng-on-s42: answer text / reason codes / kept list per item (compare_ng.py) + same_answer.py.
4. Route replay on the 180 self-tests (+ slice, v0.1) with the patched module: a turn changes under NG2 vs NG only when the guard acts AND no shortcut answers; count changed turns per set.

## Verdict rule (frozen)
- **PASS**: slice correct >= 26/26 (as NG; per item no correct -> wrong vs ng-A-s42) AND cited = 0 on every guard-fired model-answered item AND 0 changed answers on non-numeric v0.1 items (vs v01-ng-on-s42) AND 0 changed turns on the 180 self-tests (route replay).
- **FAIL**: otherwise.
- One generation per run; no rerun except an infrastructure error before the first token.

## Stop rules and budget
Disk >= 8 GiB free before each adapter call, never two llama-servers (busy.sh, wait up to 60 min), detector :8094 never stopped or restarted, never restart Docker, the Mac mini untouched. No git commit/push (coordinator commits).

## Outputs and exposure
`arms/numguard/NUMGUARD2.md` (cites this sha), `aggregates/numguard2.json`, `tools/` (numguard2.patch + .sha256, run_ng2.sh), `runs/` (ng2-*). Exposure: dev + public sets only; blind/ and rnd/veil/ not read.
