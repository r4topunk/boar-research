#!/usr/bin/env bash
# DEV-4B-PRESSURE background set (frozen 2026-10-21 for the 10-22 device day). Run with `bash`, not fish.
#   bash bg_set.sh <label>        # opens the set, waits 60 s, appends one JSON line to bg_set.jsonl
# The set: a browser with 5 Wikipedia tabs, Maps, YouTube (opened, nothing playing), the camera app, each brought to the
# front once and left in the background. Packages that are not installed are skipped and recorded as missing
# (GrapheneOS may lack Google apps). Pages need the network: run this with Wi-Fi ON, then switch airplane mode ON
# before opening the maintainer's app. Nothing is typed or signed in; no personal data.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; LABEL=${1:?label}
BROWSERS="com.android.chrome app.vanadium.browser org.mozilla.firefox"
OTHERS="com.google.android.apps.maps com.google.android.youtube app.grapheneos.camera com.google.android.GoogleCamera"
URLS="https://en.wikipedia.org/wiki/Lisbon https://en.wikipedia.org/wiki/Ethereum https://en.wikipedia.org/wiki/Sahara https://en.wikipedia.org/wiki/Hypothermia https://en.wikipedia.org/wiki/Mount_Kilimanjaro"
installed() { adb shell pm list packages "$1" | tr -d '\r' | grep -qx "package:$1"; }
launched=(); missing=()
browser=""; for b in $BROWSERS; do installed "$b" && { browser=$b; break; }; done
if [[ -n "$browser" ]]; then
  for u in $URLS; do adb shell am start -a android.intent.action.VIEW -d "$u" -p "$browser" >/dev/null 2>&1; sleep 4; done
  launched+=("$browser:5tabs")
else missing+=("browser"); fi
cam_done=0
for p in $OTHERS; do
  case $p in *camera*|*Camera*) [[ $cam_done == 1 ]] && continue ;; esac
  if installed "$p"; then
    adb shell monkey -p "$p" -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1; sleep 6; launched+=("$p")
    case $p in *camera*|*Camera*) cam_done=1 ;; esac
  else missing+=("$p"); fi
done
adb shell input keyevent KEYCODE_HOME; sleep 60
MA=$(adb shell grep MemAvailable /proc/meminfo | tr -dc '0-9')
RUN=$(for p in ${browser:-} $OTHERS; do [[ -n "$(adb shell pidof "$p" | tr -d '\r')" ]] && printf '%s ' "$p"; done)
printf '{"label":"%s","at":"%s","memAvailableKb":%s,"launched":"%s","missing":"%s","stillRunning":"%s"}\n' \
  "$LABEL" "$(date +%Y-%m-%dT%H:%M:%S)" "${MA:-null}" "${launched[*]:-}" "${missing[*]:-}" "$RUN" | tee -a "$HERE/bg_set.jsonl"
