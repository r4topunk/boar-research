# DILUTION-K plan / resume (RD-4)
Status 2026-10-21 05:3x: DONE (k1-k3 generated on the mini 05:22-05:29, 150 Haiku calls, verdict KILL; report DILUTION.md).
Resume (idempotent pieces):
```
DK=<workspace>/rnd/research/coordinator/arms/dilution-k
for k in k1 k2 k3; do bash $DK/tools/run_dk.sh status $k; done          # mini STATUS tail
for k in k1 k2 k3; do bash $DK/tools/run_dk.sh fetch $k; done           # when DONE (checks inputs sha + rows)
for k in k1 k2 k3; do bash $DK/tools/judge_dk.sh $k; done               # MacBook, Haiku 5.5-low N 4, only texts with no judged twin, cap 200 (ledger runs/logs/calls.ledger)
python3 -I $DK/tools/dk_agg.py $DK/aggregates/dilution-k.json            # readings + verdict
```
If a job died: `bash $DK/tools/run_dk.sh start <k>` (refuses while a job is queued/running).
