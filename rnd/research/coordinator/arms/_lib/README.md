# arms/_lib/arm.sh - one parametrised driver for per-arm tooling

TL;DR: `arm.sh <conf> <command> [args]`. Replaces the sed-derived copies (dh.sh/gt.sh/df.sh/dt.sh, l1.sh, l2.sh, chain*.sh).
All output is counts/ids/hashes/aggregates; shared pieces are still called, not rewritten:
`deepthink/tools/shard_judge.sh`, `deepvpara/tools/paired.mjs`, `deepthink/tools/dtcat.py`, `boar-eval/bench/v0.2/plan/floor_metrics.py`,
`boar-eval/bench/v0.3/plan/paired_gap.py`, `boar-eval/adapters/desktop-node/scripts/validate.ts`.

```
A=<workspace>/rnd/research/coordinator/arms
$A/_lib/arm.sh $A/dt512/arm.conf mkreq <src.requests> <out.requests> <runId> [id,id,...]   # rewrite runId/settings/arm
$A/_lib/arm.sh $A/dt512/arm.conf launch <requests> <runId>       # refuses if remote STATUS or local lock exists
$A/_lib/arm.sh $A/dt512/arm.conf wait <runId>                    # WAIT_EVERY=60 WAIT_HARD=5400 (s); RUNNER-FAIL/HARDSTOP rc 3
$A/_lib/arm.sh $A/dt512/arm.conf fetch <runId> [traces requests] # scp + validate + aggregate JSON + traces sha
$A/_lib/arm.sh $A/dt512/arm.conf think <traces> [idsFile] [out]  # per-item thinking stats
$A/_lib/arm.sh $A/dt512/arm.conf l1 <runId> <idsFile> <tag>      # fetch, think, Haiku N=4, paired vs control[0], rule
$A/_lib/arm.sh $A/dt512/arm.conf judge <seed>                    # Opus N=4 on $RUN_PREFIX-s<seed> (JUDGED_IDS)
$A/_lib/arm.sh $A/dt512/arm.conf scales "42 43"                  # floor_metrics + paired per seed + paired_gap + per-category
$A/_lib/arm.sh $A/dt512/arm.conf exposure                        # one line: set, runs, items, judge calls by model
$A/_lib/arm.sh $A/dt512/arm.conf chain                           # smoke gate -> slice -> l1;  also: status <runId>, gate <traces>
```

## Conf (sourced bash; copy dt512/arm.conf or gemmathink/arm.conf)
| Var | Meaning |
|---|---|
| ARM, LABEL | `config.arm` of requests; short name used in paired keys, file names and rule text (H, G) |
| TREE, REMOTE_RUNNER, REMOTE_ARM, REMOTE_ARGS | mini tree `be-0cfd4a77-$TREE`; runner script in `<runner>/kiln/`; its arg 2 (D/C/G); extra args (e.g. `noplaces`) |
| SETTINGS | JSON string for `config.settings` |
| RUN_PREFIX | run ids are `$RUN_PREFIX-s<seed>[-slice]` |
| SET, BENCH, QUESTIONS, JUDGED_IDS | set name, judge bench dir, items file (`-` = none), ids judged at L2 |
| OUT_DIR, AGG_DIR, JUDGE_SYSTEM | blind runs dir; aggregates dir; `--system` prefix (`-haiku55-low` / `-opus` appended) |
| CONTROLS | array of `name\|dir\|basename-with-{seed}`; first = L1 control + per-category; all get scales and paired_gap |
| PROMOTE_WINS, PROMOTE_D | promotion: wins >= control + N or dRatio >= D (always on) |
| CHEAPER / PARITY | optional `"dmin ratio"`: dRatio >= -dmin and arm p50 <= ratio x control p50 -> CONTINUE-cheaper / CONTINUE-parity-faster |
| THINK_HIT, DECL, SHARDS, L1_SEED | budget-hit threshold in `think` (dt512 keeps 1024 for frozen aggregates), decline ratio 0.306, shards 4, control seed 42 |
| GATE_MIN, GATE_MAX, SMOKE_GATE | default smoke gate: all deep-thinking, 0 errors, non-empty answers, GATE_MIN <= reasoning <= GATE_MAX; or a python path (argv1 = traces, rc 0 = pass) |
| SMOKE_RUN/REQ/DIR, SLICE_RUN/REQ/IDS | inputs of `chain` |
| CRITERION | path to the frozen criterion `.md` (absolute, or relative to the conf dir). **Required by `launch`** (also via `chain`): rc 7 "launch refused: criterion lacks Power block (expected_delta, n, seeds, mde) — see _lib/CRITERION-TEMPLATE.md" unless the file exists, matches its sibling `<name>.sha256` (if any), and has a `## Power` section with all four keys, or its `## Tags` section carries `Tags: blocker`. Unset = rc 7. Checked before any ssh. |

## Env
- `AGG_DIR`, `WORK_DIR` (perItem/paired JSON, symlink dir, shard logs; default OUT_DIR), `LOCK_DIR` (default `<conf dir>/.locks`) override the conf: use them to replay into a temp dir.
- `REPLAY=1`: `fetch` skips scp and only validates + aggregates local traces. `SKIPJUDGE=1`: no judge call; `l1` still runs paired + rule if the Haiku judgments file exists (old l1.sh exited before paired).
- `MINI=<host>` ssh target. Nothing in `think`, `l1` (with REPLAY), `scales`, `exposure`, `gate` touches the mini.

## Differences from the old scripts
- mkreq: one SETTINGS per arm (no control-arm `C` settings branch); `launch` takes no arm arg (REMOTE_ARM) and writes a local lock `<TREE>-<run>.lock`.
- `l1` prints "no Haiku judgments" and stops after think when the judgments file is missing (s43 runs).
- Rule text uses clause labels (cheaper / parity-faster); deepthinkv02's "PROMOTE" wording is not reproduced (CONTINUE-promotion).
- deepfull (two trees/arms per conf) and deepthinkv02 (v0.2, noplaces, K control) need their own conf; v0.2 runs: `REMOTE_ARGS=noplaces`, SET=bench-v02, BENCH=.../live/v0.2.

## Gotchas (2026-10-10)
- `shard_judge.sh` (and so `l1`/`judge`) `cd`s into boar-eval: pass **absolute** paths for traces/out/ids when calling it directly (arm.sh already does).
- `mkreq` rewrites runId/settings/arm only; a different `config.modelId` or `seed` needs a jq pass (THINK4B, SEEDVAR).
- The default smoke gate requires `generate:deep-thinking`; 4B-side arms need `SMOKE_GATE=<python>` (think4b/tools/gate.py). The adapter flag `thinkingBudgetExceeded` counts the budget-message tokens, so it is always true when the budget binds; gate on reasoning ≤ budget + 10 instead.
- Runners refuse when another Qwen llama-server is up (DEEPBO2's selector server, SEEDVAR, …): chain the next launch behind the previous STATUS DONE.


## Fail-closed semantics (2026-10-11, details: FAILCLOSED-2026-10-11.md; tests: `bash _lib/tests/run.sh`)
- `l1` / `judge` / `scales` abort (rc 5) unless the judge exited 0 and `check_judgments.py` passes: every JUDGED id has an ok row in both orders, rows = 2 x ids, no non-empty `<out>.missing`. Control-arm files are checked too (`CONTROL_CHECK=warn` downgrades that and drops `--strict`).
- `shard_judge.sh`: rc 0 ok | 1 incomplete (ids on stderr + `<out>.missing`) | 3 a shard failed | 4 `<out>.shards/STOP` or `<out>.STOP` present (nothing runs) | 5 `<out>.lock` held (mkdir lock, removed on exit). `JUDGE_FLOOR_ERRORED=1` passes `--floor-errored`; `JUDGE_CMD`/`BOAR_EVAL_DIR` stub the judge in tests.
- `l1`/`scales` hold `$AGG_DIR/.agg-$LABEL.lock` (rc 6 if held). A stale lock after a kill -9 is removed by hand (`rm -r`).
- `remote-run.sh` writes `FAIL rc=N` (not DONE) when the adapter rc != 0; `wait` returns 3 (RUNNER-FAIL), `fetch` aborts (rc 3) on FAIL or a STATUS without DONE. Mini copies in `<runner>/kiln/` must be re-pushed to pick this up.
- `paired.mjs` / `floor_metrics.py` print `n judged = X of n planned = Y` on stderr; `--strict` exits 1 if X < Y; `--floor-missing` scores unjudged items at the rubric floor (1/1/1) instead of dropping them. Default stdout is byte-identical to before.
- `boar-eval/harness/judge.mjs`: errored traces are dropped with `WARN dropped N errored traces`; `--strict` exits 5 before any call; `--floor-errored` appends 2 floor rows per errored item (no LLM call, reference side imputed).


## Criteria and the Power block (2026-10-11)
New criteria start from `_lib/CRITERION-TEMPLATE.md` (mandatory `## Power`: expected_delta, n, seeds, mde, slice = random20-*.ids, l1_futility, optional reopen). Criteria frozen before 2026-10-11 are not edited (their sha256 is frozen) and have no Power block: they are exempt only through their already-launched runs; any new launch, including a rerun with a new run id, needs a criterion that passes the check.


## precheck (2026-10-11)
- `arm.sh <conf> precheck <armTraces> <controlTraces> [idsFile] [--min 0.20]`: before any judge call, did the arm change the model input vs its control? Pairs by itemId (restricted to idsFile), 0 judge calls, counts/ids only (`precheck.py`).
- An item counts as changed if (a) kept titles differ (order-insensitive), (b) reasonCodes differ after dropping run-dependent noise (`context:N->M`, `detector:p=`, timing-like codes), or (c) a code with a prefix in the conf's `PRECHECK_MARKERS` (e.g. `addpack:`, `deepcover:`) is in the arm trace.
- Output: `precheck: n= changed= (share) kept-diff= codes-diff= marker=` (+ unchanged ids if <= 20); rc 0 if share >= min, else rc 8 `PRECHECK FAIL ... do not judge`. Run it right after `fetch`, before `l1`.
- Caveat: a marker proves the setting fired, not that the prompt text changed (DEEPCOVER: marker 82 %, kept-diff 0); where the effect is a cap or truncation, pair it with a kept/context-size check.
- Tests: T8 in `tests/run.sh` (identical, noise-only, kept 30 %, marker 50 %, idsFile on unchanged, --min).

## Gotchas (2026-10-12)
- The mini's `be-repo/` keeps an old self-contained `protocol.ts` (48268ba7…); the current boar-eval `protocol.ts` imports the `@boar-eval/protocol` workspace package, absent on the mini. Deploying a newer adapter: copy adapter.ts/server.ts/trace.ts/app-shims next to the mini's own protocol.ts/gate.ts (QUANTCEIL used a side dir `be-repo-quantceil/` sharing node_modules, vendor and runs/ by symlink, so the dt512 be-repo stays byte-identical).
- A model swap needs the rule RULE-CHANGES #22 (never remove a model a queued arm uses).


## Smoke gate (LOOP v2 T3, 2026-10-15; tests: `bash _lib/tests/smoke-tests.sh`)
- `arm.sh <conf> smoke <smoke traces|units.jsonl> --n-full N [--marker code]` runs `smoke-project.py` with the conf's CRITERION and writes `<criterion dir>/smoke.verdict.json` (`criterion_sha`, `verdict` PASS|FAIL|KILL, `reasons`, `projected_wall_h`, `wall_cap_h`, `empty_share`, `parse_share`, `s_per_unit`, `mean_prompt_tokens`, `token_budget`, `computed_at`). rc 0 PASS, 1 FAIL, 3 KILL, 7 criterion/Precheck refused. Inputs: adapter traces, or `units.jsonl` (one line per unit: `ok`, `empty`, `parsed`, `seconds`) for build/teacher runs.
- Rules: empty/cut answer, error or `ok=false`, `--marker` reason code missing, mean prompt tokens > `token_budget` (exact), projected wall (s/unit x n_full / parallelism) > 1.5 x `wall_cap_h` -> FAIL; build/teacher with empty share > 5 % or parse < 90 % -> KILL.
- `arm.sh <conf> crit_check`: rc 0 only if the verdict exists, is PASS, and its `criterion_sha` equals the criterion's sha256 now (any edit invalidates it; a FAIL/KILL is cleared only by a new freeze and a new smoke); else rc 7 with one line.
- `launch` (Ruleset >= 30 criteria only): Power check (as before, now `crit_power`) -> complete filled `## Precheck` block (waived by `Tags: blocker`; keys token_projection, token_budget, disk_peak_gib, off_baseline, call_pattern, lane, opus_clause, wall_cap_h, parallelism, run_type) -> `crit_check`; all rc 7 before any ssh. `SMOKE_SKIP=1` waives only the smoke, only for `Tags: blocker|probe`. Criteria with `Ruleset: 29` or older (or no Ruleset line) keep the Power check alone.


## Judge preflight + identity (LOOP v2 T5)
- `shard_judge.sh --preflight <traces> <out> <bench> <ids> <system> [N] [haiku|opus]` (same args as a run) runs `preflight.py` before any pass, then a live both-orders probe (`PREFLIGHT_PROBE_IDS`, default 1 id, on the arm traces and on `PREFLIGHT_CONTROL_TRACES`; rows in `<out>.preflight/{arm,control}.jsonl`). rc 0 prints `PREFLIGHT OK set= status= model= ids= planned_calls= spent= cap= control= probe=`; rc 8 prints `PREFLIGHT REFUSED <code>: ...` on stderr and writes nothing to `<out>` (no lock).
- Codes: `provenance` (rows in `<out>` or `<out>.shards` with another tracesSha256 / judge model; `ALLOW_SPLICE=1` declares a splice), `control_missing` (`PREFLIGHT_CONTROL` lacks an ok row in both orders for some id; `PREFLIGHT_CONTROL_REQUIRED=1` also refuses when no file is given), `calls_cap` (criterion `calls_cap: Haiku A / Opus B` in `## Budget`, unfilled or planned + spent > cap; spent = ok rows of `<out>` + files listed in `<out dir>/.calls.ledger`), `calls_declared` (`PREFLIGHT_DECLARED_CALLS` != 2 x ids not yet judged), `opus_on_dev` (Opus on a `dev` or unknown set in `sets.tsv` without a filled `opus_clause` in the criterion's `## Precheck`), `probe_failed`, plus `locked` / `stop_file`. Env: `PREFLIGHT_CRITERION PREFLIGHT_CONTROL PREFLIGHT_CONTROL_TRACES PREFLIGHT_SET PREFLIGHT_SETS_TSV`.
- `sets.tsv` (`set<TAB>status<TAB>note`: dev | held-out | clean; trailing `*` = prefix glob) mirrors EXPOSURES.md; an unknown set is `dev` (fail closed).
- `arm.sh l1` / `judge` call it when `$CRITERION` has `Ruleset: >= 30` (control = first CONTROLS entry; `CONTROL_CHECK=warn` makes the control optional); rc 8 + `ABORT l1|judge: preflight refused`. `PREFLIGHT=0` skips with one printed line. Older criteria skip silently.
- `identity.py --gen <traces> [--replay <traces>] [--patch-sha H] [--adapter S] [--tree C] [--mode on|off] [--not-applied-re RE] [--ids F]`: one commit / patch / adapter per file, replay = generation tree (TK2), pins match, and in `--mode on` no reason code `:(nosidecar|noopts|not-applied|notapplied)$` (X2b); missing metadata = unknown, never a failure. `arm.sh <conf> smoke <traces>` runs it first (conf vars `ADAPTER_PIN`, `PATCH_SHA256` when set) and on FAIL writes `smoke.verdict.json` FAIL (reason `identity: ...`, so `crit_check` rc 7) and returns 1; units.jsonl skip it. `IDENTITY_SKIP=1` waives it only for `Tags: blocker|probe`.
- Tests: `bash _lib/tests/judge-tests.sh` (stub judge, synthetic ids, 0 LLM calls).


## Locks, session start, deny hook (LOOP v2 T6; tests: `bash _lib/tests/guard-tests.sh`)
- `tools/lock.sh take|release|holder|audit|own|disown`: lane locks (`mini-long mac-gen mac-cpu judge`, sessions `main|burn`) in `coordinator/locks/<lane>.lock` (session/until/pid/taken/note; default `--until` now + 4 h; expired = free; rc 9 + `LOCKED <lane> by <s> until <ts>` when another session holds it) and `arms/<arm>/.owner`. Env: `LOCK_ROOT`, `BOAR_SESSION_PID` (the session pid; empty = unknown, never STALE), `NOW`. STATE's `locks=` includes the lane locks.
- `arm.sh judge` and `l1` (`judge_lane_`, right before `preflight_`): rc 9 + `ABORT judge: judge lane locked by <s> until <ts> (lock.sh)` when `lock.sh holder judge` is another session than `${BOAR_SESSION}` (default `main`). No lock = unchanged path.
- `tools/session-start.sh`: cron registry audit (`locks/cron-registry.txt`, one `id= session= created= purpose=` row per CronCreate), lock + `.owner` audit, auth canary (`claude -p ok --max-budget-usd 0.05`, 60 s; rc 3 on failure), last LOOP-LOG line + age.
- `tools/deny-hook.sh` (PreToolUse, registered in `<workspace>/.claude/settings.json`): git push, hf upload, docker restart/stop/rm/down, kill :8094, blind/ + rnd/veil/ reads; escapes and rules in `tools/HOOKS.md`.



## Lane report, day brief, watchdog (LOOP v2 T7; tests: `bash _lib/tests/lanes-tests.sh`)
- `tools/lanes-report.py [--log LOOP-LOG.md] [--backfill tsv] [--from/--to "YYYY-MM-DD HH:MM"] [--window 09:00-24:00] [--overlap-scope all|window] [--json]`: per-day busy hours of mini/mac (D6 `mini=`/`mac=` fields: tick -> next tick, last tick 90 min; plus backfill TSV `machine start end arm source`), both-idle hours in the window, overlap hours and episodes (gap < 5 min = one episode; overlap counted over all 24 h by default because the baseline's 9 episodes include night runs).
- `tools/lanes-backfill-2026-10-11.tsv`: 36 traceable intervals (QUEUE line / status file / retro `arms[i]`; 4 MacBook rows `est`) for 10-11 09:00 -> 10-14 19:30. It reproduces both-idle 25.1 h (retro 25.6), overlap 12.4 h (11.8), 10 episodes (9); the day split 6.5 / 12.7 / 2.2 / 3.7 h. Not independent proof of the baseline, a regression anchor for the report.
- `tools/daybrief.sh [--send <target>]` (D11): 3 lines + link from the last 24 h of LOOP-LOG; decisions = `- [ ]` lines of `DECISIONS-NEEDED.md` if present, else BACKLOG section 0. Env LOOP_LOG, NOW, BACKLOG, DAYBRIEF_LINK, DISCORD_BIN.
