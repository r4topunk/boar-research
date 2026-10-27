#!/bin/bash
# Poll every 10 min (≤ 6 h) until DEEPTHINK2.md has a verdict AND no 35B llama-server AND every dt2-* STATUS has an end line.
F=<workspace>/rnd/research/coordinator/arms/deepthink2/DEEPTHINK2.md
for i in $(seq 1 37); do
  v=$( [ -f $F ] && grep -oE "PROMOTED|FAIL-INCOMPLETE|\bNO\b" $F | head -1 )
  m=$(<on the mini> 'bash -c "pgrep -f \"llama-server.*Qwen3.6-35B\" | wc -l | tr -d \" \"; n=0; for s in <runner>/kiln/be-0cfd4a77-deepthink2/be-repo/runs/dt2-*/STATUS; do grep -q \"^end \" \$s || n=\$((n+1)); done; echo \$n"' | tr '\n' ' ')
  echo "$(date +%H:%M) verdict=[$v] mini(35B,openSTATUS)=[$m]"
  set -- $m
  [ -n "$v" ] && [ "$1" = 0 ] && [ "$2" = 0 ] && { echo READY; exit 0; }
  sleep 600
done; echo TIMEOUT; exit 2
