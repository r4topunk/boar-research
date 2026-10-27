# X2B-RETEST plan / resume (criterion X2B-RETEST-criterion.md, sha 3a3aaf0b, commit 11fed7a4)
Status 13:0x: DONE (see X2B-RETEST.md). Launched 2026-10-21 12:39 (both arms, GEN_ONLY, mini jobs <runner>/kiln/lp-screens/jobs/x2b{off,v1orc}-K1-stage1-pool-s42).
Resume (cwd rnd/research/coordinator/arms); each command is idempotent (skips generation when traces are present):
    OUT_BASE=$PWD/x2b-retest GEN_ONLY=1 bash x2b-retest/tools/run_pool_x2b.sh x2boff K1 ../ruler/ids/stage1-pool.ids x2b-retest/x2b-off.patch
    OUT_BASE=$PWD/x2b-retest GEN_ONLY=1 bash x2b-retest/tools/run_pool_x2b.sh x2bv1orc K1 ../ruler/ids/stage1-pool.ids x2b-retest/v1orc.patch
    python3 -I x2b-retest/tools/changed.py          # judge-call count vs cap 200
    # judge (drop GEN_ONLY, add CRITERION=$PWD/x2b-retest/X2B-RETEST-criterion.md), OFF first, then V1orC
    python3 -I x2b-retest/tools/report.py           # -> aggregates/x2b-retest.json + table

# X2B-OFF-MAIN (criterion sha 0415e6eb, commit 1c315378) — DONE 13:2x (s42: X2b stays on); addendum 1 DONE 13:3x (pooled: OFF safe at the edge; tools/opus9.sh, judge43_plan.py, report43.py)
Resume (cwd rnd/research/coordinator/arms; idempotent):
    OUT_BASE=$PWD/x2b-retest/main GEN_ONLY=1 bash x2b-retest/tools/run_pool_x2b.sh x2boffmain K1 x2b-retest/main-live77.ids x2b-retest/x2b-off.patch
    OUT_BASE=$PWD/x2b-retest/main CRITERION=$PWD/x2b-retest/X2B-OFF-MAIN-criterion.md bash x2b-retest/tools/run_pool_x2b.sh x2boffmain K1 x2b-retest/main-live77.ids x2b-retest/x2b-off.patch
    python3 -I x2b-retest/tools/report_main.py      # -> main/aggregates/x2b-off-main.json + table
