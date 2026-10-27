# codex-ladder: CV5-LADDER-CODEX packet (OpenAI-family judge on the v0.1 ladder, run by r4to on Codex)

TL;DR: `bash run.sh pilot` (0 + 4 calls, check), then `bash run.sh all` (408 Codex calls, ~1-2 h wall, resumable). Then tell the coordinator; it runs `python3 -I ../tools/cv5_ladder_codex.py ../CV5-LADDER-CODEX-2026-10-22.json`. Deadline 2026-10-23 18:00, else the hypothesis is marked NOT RUN.

```fish
cd <workspace>/rnd/research/coordinator/ruler/codex-ladder
codex login status                       # must say ChatGPT ([usage detail removed]); never set OPENAI_API_KEY for this
bash run.sh pilot                        # 4 dry-runs print "51 items, 102 calls to do", then 4 real calls on L3
bash run.sh all                          # CONC=2 GAP=2000 by default; rate limit -> it stops (exit 3); rerun = resume
bash run.sh status                       # 102/102 per rung when complete
```

## What it is
Same answers the Claude judges scored (Haiku done, Opus = CV5-LADDER-OPUS running), re-judged by Codex with the identical judge.v1 protocol. It tests whether "the 4B separates from the 1.7B/Gemma tier; the 1.7B is level with a closed-book 1.5B" (RV2, page sentence S1) holds under a second judge family, and whether the Codex lenience (+0.10 in XFAM) is the same for every arm.

| file | what |
|---|---|
| in/ids51.txt, in/ids51.csv | the 51 dev ids (= ruler/cv5-ladder/in/set.json ids; v0.1 57 minus 6 deterministic) |
| in/traces/<rung>.traces.jsonl | the 4 arms' answers on the 51 ids (copies for reading; run.sh judges the original files via `--ids`, so tracesSha256 matches the Claude rows) |
| in/refs51.jsonl | the 51 frozen references (copy of boar-eval/bench/v0.1/refs/refs.jsonl rows, sha of the full file bd235bb9...) |
| prompt/judge-system.txt, prompt/rubric.json, prompt/verdict-schema.json | judge.v1 system prompt, rubric, strict output schema (exported from boar-eval/scorers/vendor/eval-lib/judge-core.mjs) |
| prompt/rendered-<rung>.jsonl | the exact 408 user prompts judge-codex.mjs sends (102 per rung): queryId, order, boarIsA, prompt. Blinded: the judge sees "Answer A / Answer B", never which is BOAR |
| render-prompts.mjs | regenerates prompt/ (node, 0 calls) |
| run.sh | the run (checks criterion sha + SHA256SUMS + codex on PATH first) |
| out/ | Codex rows land here: `<rung>.codex.judgments.jsonl` + `.calls.jsonl` (wall time per call) |

Rungs (one seed each, the CV5-LADDER-OPUS frame): L0 Qwen2.5-1.5B closed-book; L1 Qwen3-1.7B K0 s42; L2 Gemma 4 E2B s42 (desktop); L3 Qwen3-4B cut 7 on the Pixel 8a.

## Both orders
Each (id, rung) is judged twice: once with BOAR's answer as A and the reference as B (`boarA`), once swapped (`boarB`). Which order goes first per id is seeded (`firstOrders(ids, 7)`), so it is identical to the Claude runs. The score of an item = the mean of the two orders (position bias cancels).

## Output format (one JSON line per (id, order); written by judge-codex.mjs, do not edit)
`{queryId, category, order: "boarA"|"boarB", ok, verdict: {scores_A: {correctness, completeness, usefulness: 1-5}, scores_B: {...}, winner: "A"|"B"|"tie", rationale}, mapped: {winner: "boar"|"ref"|"tie", boar: {...}, ref: {...}}, system, reference, runId, commit, arm, judgeModel, requestedModel, judgeVersion: "judge.v1-codex", sampling: {reasoningEffort: "high"}, seed: 7, durationMs, cliVersion, tracesSha256, refsSha256, questionsSha256, createdAt}`. A run is complete when every rung has 102 ok rows.

## Rules
- Dev ids only (v0.1 public bench). No blind/, no rnd/veil, no v0.4. Nothing here goes to git outside rnd; out/ rows are committed by the coordinator.
- [usage detail removed] only: no API key. If Codex rate-limits, wait and rerun `bash run.sh all` (the out file is the checkpoint).
- Do not edit judge-core.mjs, judge-codex.mjs or anything in in/ or prompt/ (SHA256SUMS check).
- After the run the coordinator adds one EXPOSURES.md row (v0.1 dev also exposed to an OpenAI judge; status unchanged) and one QUEUE row.

## Decision (frozen: ../CV5-LADDER-CODEX-criterion.md, sha 89f2b173...)
Kill if the Codex 4B - 1.7B CI includes 0 or the Codex offset spread across the 4 arms > 0.03 -> S1 is printed as "Claude-family result; the OpenAI judge disagrees" with the numbers. Support if neither fires and the separability verdicts match. Scorer: ../tools/cv5_ladder_codex.py (tested on Haiku rows copied as fake Codex rows: offsets 0, Spearman 1, verdict support).
