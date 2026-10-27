#!/usr/bin/env bash
# exp-02 disk watchdog (coordinator rule 2): while the Maple GGUF exists, check free space every 60 s.
# Below 12 GiB free: kill the download/run, delete the GGUF, write an ALERT line. Exits when the GGUF is gone.
# Usage (mini, nohup): bash <runner>/kiln/harness/watchdog-disk.sh <runner>/kiln/models/maple-preview-TQ2_0-head-Q4_K.gguf
F="$1"; LOG=<runner>/kiln/watchdog.log; MIN_KB=$((12 * 1048576))
echo "$(date '+%F %T') start watching $F" >> "$LOG"
sleep 5
while [ -e "$F" ] || pgrep -f "curl -sSL --fail -o maple" >/dev/null; do
  free=$(df -k ~ | tail -1 | awk '{print $4}')
  echo "$(date '+%F %T') free_GiB=$(awk -v k=$free 'BEGIN{printf "%.2f", k/1048576}')" >> "$LOG"
  if [ "$free" -lt "$MIN_KB" ]; then
    echo "$(date '+%F %T') ALERT free below 12 GiB: killing Kiln job and deleting $F" >> "$LOG"
    pkill -f "curl -sSL --fail -o maple"; pkill -f "serve-bench.py --model-id maple-preview"; pkill -f "llama-b11010/build-cpu/bin/llama-server"
    sleep 2; rm -f "$F"; echo "$(date '+%F %T') ALERT deleted" >> "$LOG"; exit 9
  fi
  sleep 60
done
echo "$(date '+%F %T') file gone, watchdog exits" >> "$LOG"
