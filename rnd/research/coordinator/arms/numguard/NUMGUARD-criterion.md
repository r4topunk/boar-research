# NUMGUARD: does a numeric-question guard evaluated before the emergency detector's health refusal recover the detector's misfires on plain numeric questions with zero harm elsewhere? (frozen 2026-10-15, coordinator subagent)

Deterministic-gate arm (no judge by default). Context: MATHROUTE (arms/mathroute/MATHROUTE.md, criterion 0f2c0ec9…) found the learned emergency detector (mmBERT head, `emergencyScore` in src/routing/answer.ts of cut 7) fires on plain numeric questions and the engine answers "I won't give health advice from memory…": 5/26 slice items, 3 of them in cut 7 as shipped (mr-u07 2.2 bar -> psi p=0.66; mr-a02 bus 9:40 + 2 h 35 p=0.985; mr-a04 20,000 mAh x 3.7 V -> Wh p=0.62). The arithmetic shortcut's own numeric guard (`detector:numeric-guard`) protects only the items arithmeticAnswer() matches; calculate() and travelDistanceAnswer() are skipped whenever the detector fires.

## Tags
Tags: none
Ruleset: 29
<!-- deterministic-gate arm: deterministic scorer + 0-LLM replay + byte comparison; Haiku only if the scorer leaves a question genuinely open (stated in the report before any call). -->

## Question
Arm **NG** = cut 7 + `tools/numguard.patch` with NUMGUARD=1, versus control **cut 7** (MATHROUTE arm A traces for the slice; stack/runs/v01-cut7-stack-off-s42 traces for v0.1). Used for: a PR-1 follow-up commit proposal to the app maintainer (product/credibility: a numeric question never gets a health refusal), not a bar lever.

## Fixed inputs
- Guard (engine module src/routing/numguard.ts added by the patch): `numericGuard(q)` = NOT healthLexicon(q) AND (calculate(q) != null OR numericIntent(q)). numericIntent = a number AND (a unit token, a clock time, a currency sign, a percent, or an arithmetic / conversion operator word or symbol). healthLexicon = the engine's own lists: arithmetic.ts HEALTH + DANGER word lists (copied verbatim), context.ts isHealthQuestion(), conditionCards.ts isCardEmergency(), plus a short explicit list (pregnan*, child/children/kid(s), sick, ill, hospital, doctor, vomit*, diarrh*, rash, cough*, headache, ache*, dizz*, nause*, thermometer, temperature of a person words: "my temperature", "body temperature"). Deviation from the brief, declared here: the lexicon also gates the calculator branch (stricter; a calculator match on a health message stays on the detector's path).
- Wiring: only when NUMGUARD=1 AND the detector fired (learned.fire) AND numericGuard(q): learned is replaced by {p: original p, fire: false} for the rest of the turn; the original detector codes are kept (`detector:p=…`, `detector:fire`) and `numguard:fired` is appended; on the calculator / arithmetic / travel instant receipts `numguard:fired` is appended too. With NUMGUARD unset the code path is byte-identical to cut 7 (one env read, no other change). Never committed to the engine tree.
- Tree: kiln-local/be-0cfd4a77-cut7-numguard = copy of kiln-local/be-0cfd4a77-cut7 (0cfd4a77 + cut7 patch 0fba26b8, adapter 6298e5d3), node_modules symlinked as the mathroute copy, ARM `cut7+numguard`, patch sha256 in tools/numguard.patch.sha256.
- Common: llama-server spikes/llama-b11010-cpu, --threads 4, server backend, ship profile, mmbert detector :8094 (head sonar-mmbert-small-emergency-v3b), seed 42, request config = arms/stack/runs/v01-cut7-stack-off-s42.requests.jsonl (claim kit boar-crypto + boar-wikivoyage-en). Runner tools/run_ng.sh (= mathroute run_mr.sh, busy.sh guard), requests via mathroute tools/mkreq_mr.py.
- Sets (all public/dev): boar-eval/bench/slices/mathroute-v1 (26; questions e4293219…), boar-eval/bench/v0.1/questions.public.jsonl (60; 568b3ece…), the 180 self-test items of the 9 packs run in arms/stack (boar-factbook, boar-firstaid-en, boar-medlineplus-en, boar-simplewiki-en, qa-bitcoin-se, qa-ethereum-se, qa-health-se, qa-outdoors-se, qa-travel-se; regex counts also printed for the 2 other selftest dirs). blind/ and rnd/veil/ never read.
- "Numeric item" = an item where numericGuard(q) is true (computed by the patched module, before any generation). Everything else is "non-numeric".

## Power
expected_delta: 3/26 recovered items (source: MATHROUTE arm A per-item table, the 3 detector refusals that remain with the calculator present)
n: 26 slice + 60 v0.1 + 180 self-tests
seeds: 1 (4B path byte-deterministic on the MacBook CPU server path, SEEDGEN / RULE 27)
mde: n/a (deterministic gate: counts, no significance)
slice: n/a (own dev slice mathroute-v1)
l1_futility: n/a (deterministic-gate arm)
split: none

## Ceiling (RULE 29; 0 calls)
ceiling: 3/26 on the slice (the 3 cut 7 detector refusals; the 2 B/C-only refusals are already answered by the arithmetic guard in cut 7)
bar_ceiling: v0.1's 2 calculator items already pass in cut 7 -> product/credibility arm, not a bar lever
launch: deterministic-gate arm, n/a
transfer: n/a (product only)

## Budget (RULE 29)
wall_cap: 3 h MacBook (generation: 26 slice + 60 v0.1, one llama-server at a time)
calls_cap: Haiku 120 / Opus 0 / paid API 0
smoke: tsc --noEmit clean on the patched tree; the 0-LLM route replay runs on all 266 items without error; else STOP (FAIL-INFRA)
kill_if: smoke fails; projected wall > 4.5 h
checkpoint: after the route replay (step 3)

## Measurements, in order
1. Reach read (0 calls): detector fire / refusal on existing traces (MATHROUTE A, v0.1 cut 7) + numericGuard match counts and ids on 26 + 60 + 180 (+ 40 other selftest).
2. tsc --noEmit on the patched tree; routing vitest if < 5 min.
3. 0-LLM route replay (tools/route_replay.ts, detector at :8094): per item id, numericGuard, detector p, detector fire, guard acts (= NUMGUARD would change the turn) for ON vs OFF; requirement: guard acts only on numeric ids.
4. Generation NUMGUARD=1 on the numguard tree, seed 42: (a) the 26 slice (runId ng-A-s42), scored with arms/mathroute/tools/score_mr.py and compared per item to mr-A-s42; (b) v0.1 60 (runId v01-ng-on-s42), compared to stack/runs/v01-cut7-stack-off-s42 with arms/seedgen/tools/same_answer.py and per-item reason codes / kept lists. If any non-numeric v0.1 item differs from the reference, an OFF control on the numguard tree (NUMGUARD unset, v01-ng-off-s42) is run to separate a tree/reference difference from guard harm; harm = ON differs from that OFF control on a non-numeric item.

## Verdict rule (frozen)
- **PASS**: the 3 misfires are recovered (score_mr.py >= 26/26 correct, or exactly mr-u07, mr-a02, mr-a04 flip to correct with no other slice row changing correctness) AND 0 changed answers on non-numeric v0.1 items AND identical reason codes / kept lists on all 180 self-tests and all non-numeric v0.1 items (self-tests: via the step-3 route replay, guard acts on 0 of them; v0.1: generation traces).
- **PARTIAL**: >= 1 of the 3 recovered with 0 harm (harm = any of the non-numeric conditions above failing, or a slice row flipping correct -> wrong).
- **FAIL**: otherwise.
- A recovered item = a non-refusal answer that score_mr.py scores correct. One generation per run; no rerun except an infrastructure error before the first token.

## Stop rules and budget
Disk >= 8 GiB free before each adapter call, never two llama-servers (busy.sh, wait up to 60 min), detector :8094 never stopped or restarted (start it only if down, exactly as gen_mr/run_mr expects), never restart Docker. No git commit/push (coordinator commits).

## Outputs and exposure
`arms/numguard/NUMGUARD.md` (cites this sha), `aggregates/numguard.json`, `tools/` (numguard.patch + .sha256, route_replay.ts, run_ng.sh, reach.py), `runs/`. Exposure: dev + public sets only; blind/ and rnd/veil/ not read.
