#!/usr/bin/env bash
# exp-04 LAYA disk watchdog (same rule as exp-02): every 60 s while the flag file exists; below 12 GiB free, kill the
# laya run and delete the HF cache + ONNX exports under <runner>/kiln/exp-04-jev/laya, then log ALERT and exit.
D=<runner>/kiln/exp-04-jev/laya; LOG=$D/watchdog.log; MIN_KB=$((12 * 1048576))
echo "$(date '+%F %T') start" >> "$LOG"
while [ -e "$D/.running" ]; do
  free=$(df -k ~ | tail -1 | awk '{print $4}')
  echo "$(date '+%F %T') free_GiB=$(awk -v k=$free 'BEGIN{printf "%.2f", k/1048576}')" >> "$LOG"
  if [ "$free" -lt "$MIN_KB" ]; then
    echo "$(date '+%F %T') ALERT below 12 GiB: killing laya and deleting hf cache + onnx" >> "$LOG"
    pkill -f "run_laya.py"; pkill -f "export_onnx.py"; pkill -f "snapshot_download"
    rm -rf "$D/hf" "$D/onnx" "$D/.running"; exit 9
  fi
  sleep 60
done
echo "$(date '+%F %T') flag removed, exit" >> "$LOG"
