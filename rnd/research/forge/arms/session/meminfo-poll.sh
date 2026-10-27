#!/usr/bin/env bash
# Polls BOAR's memory once per second: TOTAL PSS / TOTAL RSS (kB) and Native Heap, for Probe B and the gate probe (P5).
#   arms/session/meminfo-poll.sh OUT.csv SECONDS [--serial S] [--package team.sopa.aoair]
# Start it BEFORE launching the app for a load measurement. Prints the peak TOTAL RSS at the end.
set -uo pipefail
OUT=${1:?out csv}; SECS=${2:?seconds}; shift 2; SERIAL=; PKG=team.sopa.aoair
while [ $# -gt 0 ]; do case "$1" in --serial) SERIAL=$2; shift 2 ;; --package) PKG=$2; shift 2 ;; *) echo "unknown $1" >&2; exit 2 ;; esac; done
ADB=(adb); [ -n "$SERIAL" ] && ADB=(adb -s "$SERIAL")
echo "t,total_pss_kb,total_rss_kb,native_heap_pss_kb" > "$OUT"
for ((i = 0; i < SECS; i++)); do
  m=$("${ADB[@]}" shell dumpsys meminfo "$PKG" 2>/dev/null)
  pss=$(printf '%s\n' "$m" | awk '/TOTAL PSS:/ {print $3; exit}')
  rss=$(printf '%s\n' "$m" | awk '/TOTAL RSS:/ {print $6; exit} /TOTAL PSS:/ && /TOTAL RSS:/ {for (k=1;k<=NF;k++) if ($k=="RSS:") {print $(k+1); exit}}')
  nh=$(printf '%s\n' "$m" | awk '/Native Heap/ {print $3; exit}')
  echo "$(date +%s),${pss:-},${rss:-},${nh:-}" >> "$OUT"
  sleep 1
done
awk -F, 'NR > 1 && $3 > m {m = $3} END {printf "peak TOTAL RSS %.2f GiB (%d kB) over %d samples\n", m / 1048576, m, NR - 1}' "$OUT"
