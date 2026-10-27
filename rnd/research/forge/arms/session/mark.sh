#!/usr/bin/env bash
# One line per leg/block boundary in LOG (CSV): local time, label, battery level %, battery temperature (°C), plugged.
#   arms/session/mark.sh LOG LABEL        e.g. mark.sh $BE/$D/legs.csv L3-start
set -uo pipefail
LOG=${1:?log csv}; LABEL=${2:?label}
[ -f "$LOG" ] || echo "time,label,level_pct,temp_c,plugged" > "$LOG"
B=$(adb shell dumpsys battery 2>/dev/null)
lvl=$(printf '%s\n' "$B" | awk -F': ' '/^ *level:/ {print $2; exit}' | tr -d '\r')
tmp=$(printf '%s\n' "$B" | awk -F': ' '/^ *temperature:/ {printf "%.1f", $2 / 10; exit}')
plg=$(printf '%s\n' "$B" | awk -F': ' '/^ *(AC|USB) powered: true/ {sub(/ powered.*/, "", $1); gsub(/ /, "", $1); print $1; exit}')
line="$(date '+%Y-%m-%d %H:%M:%S'),$LABEL,${lvl:-?},${tmp:-?},${plg:-none}"
echo "$line" >> "$LOG"; echo "$line"
