#!/bin/bash
# Poll a TV run every 10 min until STATUS has DONE or the 7 h hard stop (criterion) is reached. Prints progress counts only.
RUN=$1; TREE=$2; T0=$(date +%s); LIM=$((7*3600))
while true; do
  st=$(<on the mini> "grep -c DONE <runner>/kiln/be-0cfd4a77-$TREE/be-repo/runs/$RUN/STATUS; grep -cE ' (success|error|declined|fail)' <runner>/kiln/be-0cfd4a77-$TREE/be-repo/runs/$RUN/run.log" | tr '\n' ' ')
  set -- $st; echo "$(date +%H:%M) done=$1 progress=$2 elapsed=$(( ($(date +%s)-T0)/60 ))m"
  [ "$1" = 1 ] && { echo FINISHED; exit 0; }
  [ $(( $(date +%s) - T0 )) -ge $LIM ] && { echo HARDSTOP; exit 3; }
  sleep 600
done
