#!/bin/bash
# SFT4B stage 1 (mini): run one mlx-lm LoRA job under /usr/bin/time -l with a disk watchdog (addendum-1: abort if free < 27 GiB).
# usage (nohup): bash lora_job.sh <outdir containing config.yaml>   -> <outdir>/{log, status, df.log}
set -u
O=$1; K=<runner>/kiln/sft4b; S=$O/status
echo "start $(date '+%F %T') $(date +%s) free_KiB=$(df -k ~ | tail -1 | awk '{print $4}')" > "$S"
/usr/bin/time -l "$K/.venv/bin/python" -m mlx_lm lora -c "$O/config.yaml" > "$O/log" 2>&1 &
JP=$!; echo "pid $JP" >> "$S"; min=999999999
while kill -0 $JP 2>/dev/null; do
  f=$(df -k ~ | tail -1 | awk '{print $4}'); [ "$f" -lt "$min" ] && min=$f
  echo "$(date +%s) $f" >> "$O/df.log"
  if [ "$f" -lt $((27*1048576)) ]; then echo "WATCHDOG ABORT free_KiB=$f" >> "$S"; pkill -TERM -P $JP; kill -TERM $JP; sleep 5; pkill -KILL -P $JP; break; fi
  sleep 20
done
wait $JP; rc=$?
echo "end $(date '+%F %T') $(date +%s) rc=$rc df_min_KiB=$min df_min_GiB=$(awk -v m=$min 'BEGIN{printf "%.2f", m/1048576}')" >> "$S"
[ $rc = 0 ] && echo DONE >> "$S" || echo "FAIL rc=$rc" >> "$S"
