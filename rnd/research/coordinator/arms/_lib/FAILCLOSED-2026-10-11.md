# FAILCLOSED 2026-10-11 - judge pipeline fails closed (HANDOFF-2026-10-11 s3 step 4)
Commits: boar-eval 5c66d6c (harness/judge.mjs, bench/v0.2+v0.3/plan/floor_metrics.py + their SHA256SUMS); rnd 6a7b3db (arms/_lib/*, deepthink|deepvpara|deepthinkv02|deepthink2 tools, all 10 remote-run.sh).
Test: `bash rnd/research/coordinator/arms/_lib/tests/run.sh` -> 33 passed, 0 failed (offline, 0 judge calls, blind/ never read).

| # | Fix | Semantics |
|---|---|---|
| 1 | deepthink/tools/shard_judge.sh (the one arm.sh calls; copied to deepthink2, deepthinkv02 whose l1/l2 use their own copy) | rc 0 ok / 1 incomplete (ids on stderr, `<out>.missing`) / 3 a shard failed / 4 STOP (`<out>.shards/STOP` or `<out>.STOP`, checked at start and before every rerun) / 5 locked. Per-id check (both orders), not just a row count. |
| 2 | arm.sh + _lib/check_judgments.py | l1/judge/scales abort rc 5 unless judge rc 0, `.missing` empty, every id has both orders, rows = 2 x ids; arm AND control files; scales writes nothing on abort. judge() reads PIPESTATUS (the pipe used to hide the rc). |
| 3 | mkdir locks | `<out>.lock` in shard_judge (covers l1 + judge), `$AGG_DIR/.agg-$LABEL.lock` around l1/scales (rc 6). Manual `rm -r` for a stale lock after kill -9. |
| 4 | 10 remote-run.sh copies, arm.sh fetch | `FAIL rc=N` instead of DONE when the adapter rc != 0; wait rc 3 RUNNER-FAIL (already grepped FAIL); fetch aborts rc 3 on FAIL or no DONE (STATUS is fetched first). |
| 5 | paired.mjs (+2 identical copies), floor_metrics.py v0.2/v0.3 | stderr `n judged = X of n planned = Y` (+ids); `--strict` exit 1; `--floor-missing` floors unjudged items to 1/1/1 (the rubric minimum, same "-1" as above_min; judge-core RUBRIC 1-5), reference side from the other arm/run's scores for that item else the mean. Default stdout unchanged. |
| 6 | judge.mjs | no flag: `WARN dropped N errored traces`; `--strict` exit 5 before any call (also for ids without trace/ref); `--floor-errored`: 2 floor rows/item (ok, winner ref, boar 1/1/1, `error`, `floorScored`, `refImputed`), no LLM call, reference side = mean of the judged rows in that file. |

T1 PASS (default byte-identical vs legacy code kept in tests/fixtures/legacy, real R450 dev judgments 57 items, deep35 vs bmoe), sha256 old / new:
- paired.mjs 47e45324ea05ae934e06124cec4679169f8bf6bd6f986e9a5b45cbdb704c854e / same
- floor_metrics.py a3bdfc0d8ec7c9eb7ec2af4c645ed14195ab070021de6088c96c483c013ed353 / same
- arm.sh scales stage (legacy arm.sh vs new, L2 file) f4ebd5b7fd7214c80d62a2557adb63614c993e58b1b252d9486f55dd271b7013 / same (3 aggregate files identical)
T2 PASS (last 5 rows dropped: rc 5, names dng-001,dng-002,dng-005, nothing written; legacy exited 0). T3 PASS (rc 0 WARN count 1; --strict rc 5; --floor-errored 2 floor rows; paired.mjs "n judged = 57 of n planned = 57"; floor_metrics default n=56 vs --floor-missing n=57). T4 PASS (STOP: rc 4, stub never ran; plus rc 1/3/STOP-touch cases). T5 PASS (second judge stage rc 5 "LOCKED", agg lock rc 6).

Not done / caveats
- T1 on the frozen DT512 aggregates NOT run: its inputs are under blind/ (off-limits to me). Coordinator can run `DT512_BLIND_REPLAY=1 bash .../tests/run.sh` (replays scales "42 43" into a temp AGG_DIR and cmp's L2-H-2seed / paired_gap-HvsT/HvsD-2seed; the aggregates dir is never written). Expect the new control/arm completeness check to be the only possible difference (if a frozen control is incomplete it aborts; CONTROL_CHECK=warn).
- boar-eval plan SHA256SUMS pins floor_metrics.py: I updated both pins (old fe7c70b7...e7230a, additive change). haikujudge/judge2 inputs.sha256 pin the old judge.mjs (b3c3cd16...): historical records, now stale.
- deepvpara/tools/shard_judge.sh (older variant) is referenced by no script: left as is. Legacy per-arm wrappers (dt512/tools/*.sh, deepthink2/l1.sh ...) call the fixed shard_judge/paired but do not run the new completeness check; only arm.sh does.
- Mini copies of remote-run.sh (<runner>/kiln/*-remote-run.sh) must be re-pushed; I did not touch the mini. paired_gap.py still intersects silently (guarded by the arm.sh pre-check; no n-planned line).
