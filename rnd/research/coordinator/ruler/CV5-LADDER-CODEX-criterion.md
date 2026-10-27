# CV5-LADDER-CODEX criterion (round 3, hypotheses-round3-2026-10-21.json; frozen 2026-10-21 before any Codex call)

## Question (verbatim statement)
A cross-family judge (the XFAM OpenAI judge via r4to's Codex CLI, same judge.v1 rubric, orders and blinding) reproduces the ladder ordering on
the same v0.1 51 traces (4B > Gemma ≈ 1.7B ≈ closed-book 1.5B). It does so with the same separability verdicts as Claude and with an offset that
is roughly constant across arms (|offset spread| <= 0.03). That would make S1 a two-family sentence before R4.

## Items, rungs, judge
- Ids: the 51 of ruler/cv5-ladder/in/set.json (= RV2 primary 51; dev v0.1; no blind/, rnd/veil, v0.4). Copy: ruler/codex-ladder/in/ids51.txt.
- Rungs: the CV5-LADDER-OPUS single-seed frame, existing traces, no generation: L0 Qwen2.5-1.5B closed-book (floor-anchors s42), L1 1.7B K0
  control s42, L2 Gemma 4 E2B desktop stage2 s42, L3 Qwen3-4B cut 7 Pixel 8a. Trace paths = set.json "rungs" (judged via --ids, so the rows'
  tracesSha256 equal the Haiku rows').
- Judge: boar-eval/harness/judge-codex.mjs unchanged (judge.v1 system prompt, rubric, blinding and verdict schema from judge-core.mjs; seed 7
  both orders; judgeVersion judge.v1-codex; default model gpt-5.6-sol; reasoning effort high; no tools, no web), run by r4to on his Codex
  [usage detail removed]. bench boar-eval/bench/v0.1 (questions sha 568b3ece...), refs bench/v0.1/refs/refs.jsonl (sha bd235bb9...).
- Calls: 4 rungs x 51 ids x 2 orders = **408 Codex calls** (no dedup across rungs: identical answers judged twice give a free Codex
  test-retest number, reported). Claude calls 0, paid API 0, phone 0.

## Analysis (ruler/tools/cv5_ladder_codex.py, committed with this file)
- s, r = mean of the 3 dimensions averaged over both orders; U = sum(s-1)/sum(r-1). Item-cluster bootstrap B 2000, numpy default_rng(11),
  2.5/97.5 pct, pairs on the same draws (as rv2_ladder.py). SEPARABLE iff dU >= 0.05 and CI low > 0.
- Haiku column = the identical single-seed frame with rv2_ladder.py load semantics; Opus column = ruler/cv5-ladder/out rows if complete.
- Offset per rung = U_codex - U_haiku (same draws); offset spread = max - min over the 4 rungs; per-rung Spearman of per-item s (Codex vs Haiku).

## Decision (kill rules verbatim from the hypothesis)
- **Kill**: the Codex 4B - 1.7B CI includes 0, OR the Codex offset spread across the four arms exceeds 0.03 (lenience that depends on the arm).
  Either way the page states S1 as "Claude-family result; the OpenAI judge disagrees" with the numbers, and R4 must report the arm-specific offset.
- **Support**: neither kill fires, Codex 4B - 1.7B >= +0.05 and 4B - Gemma SEPARABLE, 1.7B - 1.5B NOT separable under Codex.
- Anything else: report the three columns (Haiku / Opus / Codex) with the judge family named next to every number; no new sentence.
- **NOT RUN**: if r4to cannot run it by 2026-10-23 18:00, mark it NOT RUN and state S1 as single-family.

## Known limits (stated before the run)
One seed per rung; n 51 dev ids; Codex sampling has no temperature control (fixed reasoning effort high); one Codex pass; the 4B rung is cut 7 +
claim kit on the phone vs the K0 litepacks engine for the lower three (RV2 confound). EXPOSURES: one row after the run (v0.1 dev now also
exposed to an OpenAI judge; dev status unchanged).
