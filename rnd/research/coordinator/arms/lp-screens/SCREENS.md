# LP-SCREENS: shared stage-1 screen harness (GRILL-2026-10-20 Q6/Q13)

TL;DR: stage-1 screens for B-HONEST (K0), SHORTCTX (K1) and QUOTEFIRST (K1). Each screen = the LITEPACKS confident errors of that pack set + 10 sentinels.
Generation runs on the Mac mini (slot lock, 2 jobs max); the judge (Haiku 5.5-low, judge.v1-low, N = 4, both orders) runs on the MacBook.
**Arms compare against the MINI control (arms/lp-screens/control/), never the MacBook LITEPACKS traces.**

```bash
# stage 1 (screen) -> prints GO / NO-GO; stage 2 (MAIN n 97) -> aggregate with paired deltas vs the mini MAIN control (generated once per pack set, cached)
nohup bash <workspace>/rnd/research/coordinator/arms/lp-screens/tools/run_arm.sh <arm> <K0|K1> screen <patch|.env|none> > /tmp/<arm>-screen.log 2>&1 &
CRITERION=<abs path to the arm's frozen criterion.md> bash .../run_arm.sh <arm> <K0|K1> main <same patch>
```

## Mini tree (step 1)
- `the mini:<runner>/kiln/be-0cfd4a77-cut7-litepacks` = rsync of the mini's `be-0cfd4a77-cut7-headpass-x2` (answer.ts 289607fd, as on the MacBook) without be/.cache
  + the CMP30OFF answer hunks (`arms/cmp30off/tools/cmp30off.vs-cut7.answer.diff`, first file) -> answer.ts **0d1ac07d** + `be/adapter-litedecline.ts` **d53c1487**
  (copied from the mini's `be-0cfd4a77-cut7-litedecline`; same sha as the MacBook LITEPACKS adapter), ARM `cut7-headpass-x2+litepacks`.
- Tree hash (sha256 of the sorted per-file sha list, node_modules and be/.cache excluded, tools/treehash.sh): mini **33244341690b43ca** (392 files),
  MacBook 33f3c7eed7298601 (385 files). All 385 shared files are byte-identical; the mini has 7 extra unused files (be/adapter-quantlite.ts, be/vendor-protocol/*).
- Pack shas on the mini (full sha256 checked): boar-crypto ae9fbd2c, boar-wikivoyage-en ff8595e3, v3proto boar-simplewiki-en 99bcec30 (nothing copied);
  Qwen3-1.7B Q4_K_M b139949c, bge-small ec38e8da. llama-server b11010 (4bc272f) build-cpu, -t 4, --reasoning off.
- Engine tests: not run (the LITEPACKS flow did not run them; CMP30OFF ran 1350/1350 on its own copy).

## Screen lists (step 2, tools/mk_screens.py, 0 LLM)
Selection uses the MacBook LITEPACKS judgments (MAIN n 97 = v01 57 + qa-cooking-se 20 + qa-money-se 20; K1 reuses K0 rows for byte-identical answers, as agg.py).
- PROBLEMS = every MAIN item that is a confident error in that arm (not declined, correctness mean over both orders <= 1.5).
- SENTINELS = 10 MAIN items not CE, not declined, correctness 5.0; 6 from v01 + 4 from cm, by ascending sha256(id). Too few items at 5.0
  (K0: v01 5, cm 0; K1: v01 4, cm 0), so each group is filled best-by-correctness (ties by ascending sha256(id)): the cm sentinels are at 3.0-4.0.

| Pack set | Problems (v01 / cm) | Sentinels | ids file sha256 | Stage-1 need |
|---|---|---|---|---|
| K0 (B-HONEST) | 27 (14 / 13) | 10 | `b6ff7da735c370932e56e74a65589d9ee5b6d277426dceb01fd2e5d7b3b509e1` | fixed >= 6, sentinels worse <= 1 |
| K1 (SHORTCTX, QUOTEFIRST) | 27 (15 / 12) | 10 | `c7ea13c3165c6d42c13f9866a77e936b7f11a859845cd3aeee5e1e3e270bd158` | fixed >= 6, sentinels worse <= 1 |

MAIN ids (stage 2): `main-97.ids` sha256 `9664d81fdf182603617d31d75b34eaa8fcb1eeb5f0fa87e68352e1fe09d2a462`. Full lists in screen-K0.json / screen-K1.json; ids files list problems then sentinels.

```
K0 problems lan-cmp-004 lan-cmp-005 lan-exp-007 lan-rsn-001 lan-rsn-003 st-qa-cooking-se-002 st-qa-cooking-se-003 st-qa-cooking-se-008 st-qa-cooking-se-012 st-qa-cooking-se-013 st-qa-cooking-se-015 st-qa-cooking-se-020 st-qa-money-se-004 st-qa-money-se-007 st-qa-money-se-009 st-qa-money-se-010 st-qa-money-se-011 st-qa-money-se-020 vit-cry-002 vit-cry-003 vit-cry-005 vit-cry-006 vit-cry-007 vit-hum-004 vit-hum-005 vit-sci-002 vit-trv-003
K0 sentinels lan-exp-003(5.0) lan-ref-002(5.0) lan-rsn-002(5.0) lan-rsn-007(5.0) st-qa-cooking-se-001(3.5) st-qa-cooking-se-019(4.0) st-qa-money-se-002(3.5) st-qa-money-se-019(3.5) vit-sci-003(5.0) vit-trv-004(4.5)
K1 problems lan-cmp-003 lan-rsn-003 lan-rsn-004 lan-rsn-005 st-qa-cooking-se-002 st-qa-cooking-se-003 st-qa-cooking-se-008 st-qa-cooking-se-012 st-qa-cooking-se-013 st-qa-cooking-se-015 st-qa-cooking-se-019 st-qa-cooking-se-020 st-qa-money-se-004 st-qa-money-se-009 st-qa-money-se-010 st-qa-money-se-020 trv-004 vit-cry-002 vit-cry-003 vit-cry-005 vit-cry-006 vit-cry-007 vit-cry-009 vit-hum-004 vit-hum-005 vit-sci-002 vit-trv-003
K1 sentinels lan-ref-002(5.0) lan-rsn-002(5.0) lan-rsn-007(5.0) st-qa-cooking-se-009(3.5) st-qa-money-se-005(3.0) st-qa-money-se-013(3.5) st-qa-money-se-019(3.5) vit-hlt-002(4.5) vit-sci-003(5.0) vit-trv-004(4.5)
```

## Mini controls and parity vs the MacBook (step 3)
Unchanged system, seed 42, mini; judged with Haiku 5.5-low judge.v1-low, N = 4, both orders, on the MacBook.

| Control | n | U | CE count | Identical text vs MacBook | Identical retrieval.kept | CE agreement (on identical text) |
|---|---|---|---|---|---|---|
| lpctl-K0-screen | 37 | 0.357 | 23 (23 of the 27 problems, 0 sentinels) | 11/37 | 37/37 | 33/37 (10/11) |
| lpctl-K1-screen | 37 | 0.380 | 22 (21 of the 27 problems, 1 sentinel: st-qa-money-se-013) | 14/37 | 37/37 | 30/37 (14/14) |
| lpctl-K0-main (lazy, cached) | 97 | 0.4055 (MacBook 0.4059) | 27 (MacBook 27) | 29/97 | 97/97 | 85/97 (28/29) |
| lpctl-K1-main | not generated yet: generated on first `main` call for K1 | | | | | |

**Parity is not 100 %.** Retrieval is identical on every item (same kept chunks, same context sizes); the answer text differs on 60-70 % of items because
decoding at temperature 0.7 diverges between the M4 (mini) and the M1 Pro (MacBook) CPU kernels. **Arms compare against the MINI control, never the MacBook one.**
Parity files: control/aggregates/parity-*.json (tools/parity.py).

Determinism on the mini: the K0 screen control and the K0 MAIN control (separate runs, the first concurrent with the K1 job) give byte-identical text on 37/37 shared items.
**Judge noise:** re-judging those same 37 identical texts in a separate judge run gives equal correctness on only 24/37 and equal CE on 35/37 (on the MacBook-vs-mini identical
texts, 1 CE flip in 11 and 1 in 29). The harness reuses control judgments for byte-identical answers, so only changed answers are re-judged; still, a changed answer on
a problem item can "fix" by judge noise alone (about 5 % per CE item), and a changed sentinel can come out "lower correctness" by noise. Read the gate's fixed list with that in mind.

## Smoke (step 5)
- `IDS_OVERRIDE=smoke-K0.ids run_arm.sh lp-smoke K0 screen none` (lan-cmp-004, st-qa-cooking-se-002, lan-exp-003): answer text, retrieval.kept, route reason codes and
  declined byte-identical to lpctl-K0-screen on 3/3; 0 judge calls (all reused).
- Patch path + lazy MAIN control: `IDS_OVERRIDE=smoke-main.ids run_arm.sh lp-smoke K0 main tools/smoke-comment.patch` (comment-only answer.ts patch, answer.ts 0ffbd304 on the mini)
  generated + judged lpctl-K0-main first (194 calls), then reproduced it on 3/3 items byte-for-byte, 0 judge calls.

## Runner contract (step 4)
- `tools/run_arm.sh <arm> <K0|K1> <screen|main> <patch|file.env|none>`. Patch = unified diff relative to the tree root, applied with `patch -p1`
  (checked with --dry-run against the MacBook copy of the tree first); `.env` = KEY=VALUE lines exported after the defaults (LITEDECLINE_OFF=5, --reasoning off, ...).
  Env: `CRITERION=<frozen criterion.md>` (passed to the judge preflight for calls_cap), `IDS_OVERRIDE=<ids file>` (subset run), `JUDGE_N` (default 4).
- Mini job: `<runner>/kiln/lp-screens/jobs/<run>/` (APFS clone of the base tree + patch; the clone is deleted after the traces come back), `tools/mini_gen.sh` under nohup:
  slot lock = atomic `mkdir <runner>/kiln/slots/gen1|gen2` (owner in slots/genN.owner, stale slots of dead pids reclaimed, rmdir on exit), detector :8094 used never started,
  disk >= 25 GiB, waits while 2 non-detector llama-servers run, one llama-server per job on an OS-assigned port (the adapter starts and stops it).
- Judge: MacBook (`claude -p` on the mini fails: OAuth session expired), Haiku 5.5-low, judge.v1-low, N = 4 shards, both orders, deepthink/tools/shard_judge.sh with preflight
  and check_judgments.py (fail closed). Units v01 / qa-cooking-se / qa-money-se. Candidates re-judge only answers whose text differs from the mini control.
- Outputs `arms/<arm>/`: runs/req, runs/logs (`<run>.status` incl. inputs sha + patch sha, `<run>.calls` = Haiku calls), traces, judgments, aggregates/`<run>.json`
  (summary + paired deltas vs the mini control, bootstrap B 2000 seed 11), screen stage: aggregates/`<run>.gate.txt|json` from tools/screen_gate.py.
- Resumable: same inputs (requests + patch/env bytes) -> generation skipped; complete judgments skipped.
- Gate (tools/screen_gate.py): fixed = problem ids CE in the mini control and not CE in the candidate; sentinel worse = lower correctness, or newly declined / refusal-like,
  or newly CE; GO iff fixed >= ceil(0.22 x 27) = 6 AND sentinels worse <= 1.

## Deviations
- The mini had rebooted (up 4:55 at 19:11) and the detector on :8094 was down. It was restarted with the canonical command (SHA256SUMS checked, same flags as the MacBook detector,
  lite4-remote-run.sh recipe) at about 19:12; nothing else was started or stopped.
- Judge runs on the MacBook (mini claude -p not authenticated). Generation does not use `<runner>/bin/run-heavy` (it serializes to 1 job); the gen1/gen2 slots replace it (r4to 10-20).
- Haiku calls spent by this harness build: 342 (screen controls 74 + 74, K0 MAIN control 194, smokes 0).
