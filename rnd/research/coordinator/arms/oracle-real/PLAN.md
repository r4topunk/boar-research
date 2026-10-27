# ORACLE-REAL plan / resume
Status 2026-10-21 04:4x: DONE (generation 04:26-04:30 on mini slot gen2; judged 98 Haiku calls; report ORACLE-REAL.md).
Re-run from scratch (idempotent pieces):
```
OR=<workspace>/rnd/research/coordinator/arms/oracle-real
python3 -I $OR/tools/build_inputs.py $OR            # inputs (must reproduce the shas in ORACLE-criterion.md)
bash $OR/tools/run_oracle.sh start; bash $OR/tools/run_oracle.sh status; bash $OR/tools/run_oracle.sh fetch   # mini, slot-locked
python3 -I $OR/tools/oracle_agg.py /dev/null --need $OR/judgments/oracle-K3-v01.jids   # ids to judge, then shard_judge.sh (see ORACLE-REAL.md)
python3 -I $OR/tools/oracle_agg.py $OR/aggregates/oracle-real.json
```
