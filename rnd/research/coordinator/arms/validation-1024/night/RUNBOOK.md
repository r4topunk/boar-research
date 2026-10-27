# Mini queue runbook (VALIDATION 2026-10-24, ADDENDUM-1 section 4). Prepared 2026-10-23, 0 LLM / 0 judge calls so far.

GO (after V0 identity passes; rs-RC and tools/rc-env.sh final):
1. `tools/lock.sh take mini-long main --note "val1024 night queue"` (coordinator lane lock, MacBook side).
2. `bash night/tools/sync_mini.sh sync` (re-runs mk_jobs.py from rc-env.sh, rsyncs rs-RC + rs-RETBENCH (src; be/node_modules cloned from the mini base tree), packs-rc (already prestaged, sha-checked), w78 sidecars, rc.env / rb.env, night/; verifies tree sha manifests, every kit sha, bins, detector, disk).
3. `bash night/tools/sync_mini.sh start` (= sync again + `mini_queue.sh start`: nohup caffeinate -i, fully on the mini; the MacBook may sleep).
Watch: `<on the mini> 'bash <runner>/kiln/val1024/night/tools/mini_queue.sh status'` (QUEUE.log + one STATUS per job). Stop: `... mini_queue.sh stop`.
Morning: `sync_mini.sh fetch` -> `python3 -I night/tools/agg0.py` (NIGHT0.md) -> `python3 -I night/tools/judge_ready.py` (judge-ready/JUDGE-READY.md: exact A calls + commands).

| # | job | suite | requests | tree / kit / env | reference for divergence | ETA on the mini |
|---|---|---|---|---|---|---|
| 1 | v2-s | V2 S | 115 (12 groups) | rs-RC / RC kit / rc.env, personalityId succinct | uxmatrix/gen/succinct (SEFIX-124, MacBook) | ~20 min |
| 2 | v2-splus | V2 S+ | 115 (12 groups) | same, persona override v2/personas/splus.json | v2-s | ~24 min |
| 3 | s4-main-s42 | S4 | 97 | RC | coverage-map/sefix/ans-traces/sefix124-main-s42 | ~11 min |
| 4 | s4-main-s43 | S4 | 97 | RC | sefix124-main-s43 | ~11 min |
| 5 | v3-s | V3 L2 S | 48 + 48 (turn 2 built on the mini) | RC | none | ~12 min |
| 6 | v3-splus | V3 L2 S+ | 48 + 48 | RC, S+ | v3-s | ~13 min |
| 7 | s5-packproof | S5 | 360 (11 groups) | RC (+ qa-bitcoin-se / qa-ethereum-se ON groups) | packproof/gen (SEFIX-124, MacBook) | ~45 min |
| 8 | s7-uxm-on-s44 | S7 | 60, seed 44 | RC | v2-s ON (seed 42) | ~7 min |
| 9 | s10-topics | S10 | 27 | rs-RC + rc.env, kit wiki-vital5 only (topics27 recipe), Succinct | topics27/gen-succinct | ~3 min |
| 10 | b-k4comp40-19 | B-k4comp40 | 19 | rs-RETBENCH / SEFIX-124 K13 (compose/packs-k13) / SEFIX env + RS_RB_K=4 RS_RB_COMPRESS=0.4 | sefix124-main-s42 | ~3 min |
Total 1082 generations, ~2 h 30 min (Succinct ~6.5 s/answer on the M4 from sefix124-main traces (591 s / 97), S+ ~8.5 s assumed, ~35 s setup per group from the UXMATRIX mini STATUS). V2 = 230 answers, not 240: the 5 gen-nopack items have ON = OFF (one generation counted in both columns, as UXMATRIX).

Disk: mini 26.48 GiB free after the prestage (+1.07 GB packs, +95 MB sidecars); sync adds ~0.23 GB of tree src, outputs ~0.1 GB -> ~26.1 GiB; each group checks >= 25 GiB and the queue STOPS below it. Tree clones per job are APFS clones, removed at job end.

Judge-ready (no call tonight): V2 UXMATRIX protocol (night/tools/label.mjs = uxmatrix label.mjs byte-identical except LABEL_CAP), A calls = distinct units (~216 expected), cap 520; S4 judge.v1 N 4 both orders on items whose text differs, 2 calls per id (<= 194 per seed); V3 L2 v3/V3L2-criterion.md (frozen), S 48 A, <= 144, cap 220; S5 / S7 UXMATRIX units (A = units, ~ <= 360 / 60); S10 sentence audit (calls <= sentences); B-k4comp40 38.

## ADDENDUM-2 extension (jobs 11-16, 750 requests; total 1832)
Built by tools/mk_jobs_ext.py from the already-built jobs (only seed / persona / runId / arm change; mk_jobs.py untouched). Running as a second detached invocation on the mini, `mini_queue.sh start-ext` (pid in queue-ext.pid, caffeinate): it waits for queue.pid to exit, then runs jobs-ext.json's order with the same per-group checks (slot lock, detector, disk >= 25 GiB stops). v2-splus-s44 / v2-s-s44 carry not_after "2026-10-24 08:30" (skipped if they would start later). Order: v2-s-s43 (115), v2-splus-s43 (115), s5-packproof-splus (180 ON), s4-main-splus-s42 (97), v3-s-s43 (96), s10-topics-splus (27), v2-splus-s44 (60 ON), v2-s-s44 (60 ON). agg0.py and judge_ready.py cover them.
