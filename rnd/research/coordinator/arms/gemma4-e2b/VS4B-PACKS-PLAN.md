# GEMMA-VS-4B + GEMMA-PACKS: resume commands (runners are resumable: finished generation / judgments are skipped)

Criteria frozen at rnd 3d76b5c5 (VS4B-criterion.md 4212369b..., PACKS-criterion.md 624aac30...). Launched 2026-10-21 02:21 (A and G0), G3 after G0 aggregates.
```
A=<workspace>/rnd/research/coordinator/arms; G=$A/gemma4-e2b; cd $A
# A (4B on MAIN 97 K0)
CRITERION=$G/VS4B-criterion.md nohup bash $A/lp-screens/tools/run_arm.sh gemma4-e2b-vs4b K0 main $G/vs4b-engsamp.patch > $G/logs/vs4b.log 2>&1 < /dev/null &
# B G0 (Gemma K0 on cand80)
OUT_BASE=$G/packs CRITERION=$G/PACKS-criterion.md CTLAGG_OVERRIDE=$G/packs/aggregates/cache-K0-cand80.json nohup bash $G/tools/run_pool_k.sh gemma4-e2b-eng K0 $G/packs/cand80.ids $G/gemma4-e2b-engsamp.patch > $G/logs/packs-K0.log 2>&1 < /dev/null &
# B G3 (only after packs/aggregates/gemma4-e2b-eng-K0-cand80-s42.json exists)
OUT_BASE=$G/packs CRITERION=$G/PACKS-criterion.md CTLAGG_OVERRIDE=$G/packs/aggregates/gemma4-e2b-eng-K0-cand80-s42.json nohup bash $G/tools/run_pool_k.sh gemma4-e2b-eng K3 $G/packs/cand80.ids $G/gemma4-e2b-engsamp.patch > $G/logs/packs-K3.log 2>&1 < /dev/null &
# reports (0 LLM)
python3 -I $G/tools/vs4b_report.py $G/vs4b/vs4b-report.json
python3 -I $G/tools/packs_report.py $G/packs/packs-report.json
```
If a judge log says "STOP file present": delete the STOP file in that judgments .shards dir and rerun the same command. Mini job status: <on the mini> 'tail -3 <runner>/kiln/lp-screens/jobs/<run>/STATUS'.
