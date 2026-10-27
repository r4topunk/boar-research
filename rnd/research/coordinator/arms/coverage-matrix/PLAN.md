# COVERAGE-MATRIX plan and resume commands

Criterion: MATRIX-criterion.md (+ .sha256), committed before generation. Driver: tools/run_matrix.sh (MacBook, nohup); resumable (finished generation and judgments are skipped).
```
CM=<workspace>/rnd/research/coordinator/arms/coverage-matrix
nohup bash $CM/tools/run_matrix.sh > $CM/logs/run_matrix.log 2>&1 < /dev/null &
tail -5 $CM/logs/run_matrix.log; ls $CM/logs
<on the mini> 'for f in <runner>/kiln/lp-screens/jobs/{q17,gemma,q4b}-*/STATUS; do echo $f; tail -2 $f; done'   # mini status (bash -c if fish complains)
python3 -I $CM/tools/matrix_report.py $CM/matrix-report.json   # report, 0 LLM
```
A judge log saying "STOP file present": delete the STOP file in that judgments .shards dir and rerun the driver. A cell logged CAP-PENDING stays pending (no subsetting).
