# PR1-REBASE: cut 7 rebased onto rferrari/boar-app main (2026-10-14)

TL;DR: branch `pr/cut7-engine` = upstream/main 8fdb665f + the 13 cut 7 commits (rebased as they were, no squash) + 1 test-only commit.
**HEAD 8882b175f95bc4320a426ac9375ba96fd7bcb3df**. Worktree: $BOAR_WS/wt/pr1. Not pushed. No PR opened.
2 textual conflicts and 2 semantic test conflicts were resolved. tsc is clean and vitest is 1,360/1,360. The retrieval replay
is identical to cut 7 on 60/60 items. Generation: answers 59/60 byte-identical to the reference traces, and tier, kept titles and
reason codes 60/60. The one text difference (lan-exp-007) is run-to-run noise in the reference run, not the rebase: re-run now,
the cut 7 tree itself gives the pr1 text from a byte-identical prompt. **PR-1 is the measured engine.**

## Branch and commits
| ref | sha |
|---|---|
| upstream/main (base) | 8fdb665f3a0e3791740e932d518741747855242f |
| coord/cut7 (source, untouched) | 6d0b93b191b4dc4290cb22997bcf3bede17cec05 |
| pr/cut7-engine rebased cut 7 tip | eb95ac7deddfd2a82fcd810b6ea9f0829fc09f17 |
| pr/cut7-engine HEAD (+ test reconciliation) | **8882b175f95bc4320a426ac9375ba96fd7bcb3df** |
The full commit list is in branch.txt.

Commands:
```
git -C boar-app worktree add -b pr/cut7-engine wt/pr1 coord/cut7
cd wt/pr1 && git rebase --onto upstream/main 0cfd4a77      # 13 commits, 2 stops
```
Squash: not done. The chain has 13 commits, under the ~25 limit, and none are WIP.

## Conflict log
| # | where (commit being applied) | file | upstream change | cut 7 change | resolution |
|---|---|---|---|---|---|
| 1 | 285df041 "cut 2" | src/routing/context.ts `riskyHealthInstruction` | 3f5e6c9e…94e200c7: new hypothermia exertion check (`HYPOTHERMIA_CONTEXT`, `EXERTION`, `exertionNegated`, id `exertion-hypothermia`) after the RISKY_HEALTH loop | health-retrieval agent exp-29: the RISKY_HEALTH loop ignores "not only" when testing negation (and cut 2 adds RISKY_HEALTH id `hypo-exertion`) | Both kept: cut 7's loop line (with the "not only" strip), then upstream's two exertion lines. Order: cut 7's ids win when both match. |
| 2 | 84cd9c17 INSTANT-FRAG | src/routing/answer.test.ts | 3f5e6c9e: new test "'Answer anyway' runs the model…" | two INSTANT-FRAG tests at the same spot | Both kept, upstream's test first. |
| auto | several | answer.ts, context.ts, ptQuery.ts, context.test.ts | `quickFirst && !req.answerAnyway`; PT `bebês?` regex; hypothermia tests | — | Merged cleanly; checked below. |

Semantic conflicts (tests failed after the rebase; resolved in commit 8882b175, tests only, no engine code):
| test (from main) | why it failed | change |
|---|---|---|
| context.test.ts "flags walking/exercise advice…" and "flags direct walking instructions…" | cut 2's narrower `hypo-exertion` RISKY_HEALTH rule fires first on those texts, so the id is `hypo-exertion`, not `exertion-hypothermia`. The answer is replaced by a safe excerpt either way; only the reason code differs (`grounding:health-unsafe-<id>`). | Those 2 blocks accept either id (`EXERTION_ID` regex). The other blocks are unchanged and still pass with `exertion-hypothermia`. |
| ptQuery.test.ts "bebê is a baby, beber is to drink" | cut 7's exp-30 rule: a translation made only of modifier terms (child/stop/treat/prevent) returns null. "Os bebês podem tomar sol?" → null, not "child". | Plural checked with "Os bebês estão com febre" (→ "fever child"). The old query is asserted null. Engine behaviour unchanged (cut 7's). |

Behaviour note: we did not reorder the two hypothermia rules. Running main's rule first would change cut 7's
measured reason codes, so cut 7's order is kept.

## Invariant (deliverable 1)
- `git diff --name-only upstream/main pr/cut7-engine` at eb95ac7d is the same 40-file set as `git diff 0cfd4a77 coord/cut7`
  (diffstat-pr1-vs-upstream.txt). At HEAD 8882b175 it is 41 files: + src/routing/ptQuery.test.ts (the test reconciliation above,
  the only file outside the cut 7 set).
- 35 non-conflict files: blob in pr1 == blob in coord/cut7 and base blob == upstream blob → diff identical to cut 7's (35/35).
- 5 conflict-set files: `git diff coord/cut7 pr1 -- f` == `git diff 0cfd4a77 upstream/main -- f` in size for all 5 (answer.ts +3/−1,
  context.ts +46, ptQuery.ts +1/−1, answer.test.ts +45, context.test.ts +72), so pr1 = cut 7 + exactly main's changes.
  context.test.ts then gets the test edit described above.

## Checks
| check | upstream/main 8fdb665f (wt/pr1-base) | pr/cut7-engine |
|---|---|---|
| deps | `npm ci --ignore-scripts` (package-lock.json, no pnpm lock) | same |
| `npx tsc --noEmit` | exit 0, 0 errors | exit 0, 0 errors (pr1.tsc.log) |
| `npx vitest run` | 105 files, **1,178/1,178** passed | at eb95ac7d: 1,357 passed / **3 failed** (pr1.vitest.before-testfix.log, the 3 semantic conflicts above); at 8882b175: 117 files, **1,360/1,360** passed (pr1.vitest.log) |
| retrieval replay, 60 v0.1 public items, `--tasks-from` reference traces, `--compress`, claim kit | — | wt/pr1 vs wt/cut7: **60/60 identical** (task, tier, query, k, raw, sources, pre); identicalRaw vs reference 60/60 on both trees (replay-compare.txt, replay-*.jsonl/log) |
| generation identity, 60 items, seed 42 | — | answer text **59/60** byte-identical; tier 60/60, task 60/60, outcome 60/60, kept titles 60/60, reason codes 60/60 (gen-compare.txt) |

Replay command (both trees):
```
boar-eval/adapters/desktop-node/tools/replay-retrieval.sh --questions boar-eval/bench/v0.1/questions.public.jsonl \
  --tree wt/{cut7,pr1} --tasks-from arms/stack/runs/v01-cut7-stack-off-s42.traces.jsonl --compress --out arms/pr1/replay-{cut7,pr1}.jsonl
```

Generation setup:
- Tree runner-local/be-8882b175-pr1 = `git archive 8882b175 src assets locales modules package.json tsconfig.json`, COMMIT = 8882b175…,
  ARM = pr1, no PATCH_SHA256. The runner be/ is copied from runner-local/be-0cfd4a77-cut7-stack (adapter sha a77838f1, the same one
  that wrote the reference).
- Requests: runs/v01-pr1-s42.requests.jsonl = the reference requests with only runId → v01-pr1-s42, config.commit → 8882b175 and
  config.arm → pr1. Item, settings, kit, seed and device are unchanged.
- Env, server bin (llama-b11010-cpu), `--threads 4`, mmbert detector :8094 and pack dirs are as arms/stack/tools/run_stack.sh.
  Runner: tools/run_pr1_gen.sh. It waited 12 min for a longsession run to finish, then ran. rc 0, 60 rows.
- Comparison: `python3 tools/compare_gen.py ../stack/runs/v01-cut7-stack-off-s42.traces.jsonl runs/v01-pr1-s42.traces.jsonl`.

### The one differing item: lan-exp-007 (Greenland)
- Reference "…about 80% of **its land area** is covered by ice." vs pr1 "…about 80% of **the territory** is covered by ice."
  Prompt tokens are 631 in both; context, kept sources and reason codes are identical; the texts diverge at the 49th output token.
- Diagnosis run (tools/rerun_one.sh, `--dump-prompts`): the single item was re-run on the **cut 7 tree** (runner-local/be-0cfd4a77-cut7-stack,
  original requests) and on the pr1 tree. Both gave "the territory", and the dumped prompts are **byte-identical** (`cmp` OK;
  runs/rr-*-lan007.*).
- Conclusion: the difference is not caused by the rebase or by any upstream routing commit. The cut 7 tree itself does not reproduce
  its own reference text today. The reference ran at load avg 18.8 (pr1: 12.8). This is the first observed exception to
  RULE 27's byte-determinism on this path (1/60), and it is worth a note in SEEDGEN. No upstream commit in src/routing plausibly
  touches this item: the 7 commits change "Answer anyway", hypothermia exertion, emergency numbers by country, and the PT `bebê`
  term. None applies to an English, non-health Greenland question, and the prompt is identical.

## Evidence files (this folder)
branch.txt, diffstat-pr1-vs-upstream.txt, pr1-base.{tsc,vitest}.log, pr1.{tsc,vitest}.log, pr1.vitest.before-testfix.log,
replay-{cut7,pr1}.{jsonl,log}, replay-compare.txt, runs/v01-pr1-s42.* (requests, traces sha a17a9b80…, logs, status),
runs/rr-{cut7,pr1}-lan007.*, gen-compare.txt, tools/{run_pr1_gen.sh,rerun_one.sh,compare_gen.py}, PR-DESCRIPTION.md.
The reference traces sha is e412b898… (arms/stack/runs/v01-cut7-stack-off-s42.traces.jsonl).

## Blockers / open items
- None for the engine. Before a real PR: fill the https://github.com/r4topunk/boar-research placeholders in PR-DESCRIPTION.md.
- Leftover worktree wt/pr1-base (detached at upstream/main, with node_modules): it can be removed with `git worktree remove`.
