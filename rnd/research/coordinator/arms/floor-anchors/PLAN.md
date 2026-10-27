# FLOOR-ANCHORS plan / resume (criterion FLOOR-criterion.md, sha ed88f377...)

State 2026-10-21 03:4x: decline variants judged (180 Haiku, aggregates/floor-decline.json: INVALID). 1B arm: mini job
<runner>/kiln/lp-screens/jobs/floor-anchors-K0-main-sub3e6183-s42 QUEUED on the slot lock (gen1/gen2 held by q17-KA-main-97 and q4b-K3-cand80);
Update 04:0x: still queued after 27 min (the slot lock is not FIFO: q4b-KA-cand80 took gen1 at 03:50; gen2 = q17-KA-main-97). MacBook runner (run_arm.sh, nohup, pid in ps) polls it and then judges (114 Haiku) + aggregates automatically. Log: runs/logs/run_arm.nohup.log.

## Resume (if the MacBook runner died)
    A=<workspace>/rnd/research/coordinator/arms
    <on the mini> 'cat <runner>/kiln/lp-screens/jobs/floor-anchors-K0-main-sub3e6183-s42/STATUS'   # queued / slot / start / end / DONE
    # rerun is idempotent: same inputs b781e2172c0a5b0f -> it reuses a DONE mini job or the local traces, resumes judging
    nohup env IDS_OVERRIDE=$A/litepacks/data/v01-57.ids CRITERION=$A/floor-anchors/FLOOR-criterion.md \
      bash $A/lp-screens/tools/run_arm.sh floor-anchors K0 main $A/floor-anchors/fa-1b-closedbook.patch >> $A/floor-anchors/runs/logs/run_arm.nohup.log 2>&1 < /dev/null &
    # (if the mini job is still queued/running, run_arm.sh refuses to recreate it: wait for DONE, then rerun the line above)
## After ALLDONE in the log
    python3 -I $A/floor-anchors/tools/floor_agg.py      # -> aggregates/floor.json (separability verdict)
    # then: FLOOR.md separability section, QUEUE row (tools/qrow.sh main ...), commit rnd (never push)

DONE 04:07: generation (04:02-04:06) + 102 Haiku judged + aggregates/floor.json; FLOOR.md §2 written. Nothing left to run.
