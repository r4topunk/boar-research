#!/bin/bash
# Wave 3 (2026-10-13): convert + empty-title drop + build for the two wave-3 Stack Exchange packs, then copy to shared-data/packs/wave3.
# Same steps as wave 1 (scripts/conv-se.sh, drop-empty-title.mjs, build.sh). Run on the build host after the deep chain ends.
# usage: se-wave3.sh [site ...]   (default: cooking money)
set -uo pipefail
export PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin
S=<runner>/kiln/packs/scripts; L=<runner>/kiln/packs/logs; W=<runner>/shared-data/packs/wave3; mkdir -p "$W"
name_of() { case "$1" in cooking) echo "Seasoned Advice (cooking) Stack Exchange Q&A";; money) echo "Personal Finance & Money Stack Exchange Q&A";; esac; }
for site in "${@:-cooking money}"; do
  [ -z "$site" ] && continue
  for s in $site; do
    id=qa-$s-se; name=$(name_of $s)
    echo "=== $id ($s) $(date +%T)"
    bash $S/conv-se.sh $s $id > $L/convert-$id.log 2>&1 || echo "convert/validate rc!=0 for $id (empty titles are expected; re-validated after the drop)"
    node $S/drop-empty-title.mjs <runner>/kiln/packs/work/$id | tee -a $L/convert-$id.log
    (cd <runner>/kiln/packs && node convert/validate.mjs work/$id >> $L/convert-$id.log 2>&1) || { echo "validate FAILED $id"; continue; }
    j=$(ls <runner>/kiln/packs/work/$id/*.jsonl)
    bash $S/build.sh $id "$name" <runner>/kiln/packs/work/$id/manifest.json $j > $L/build-$id.log 2>&1 || { echo "build FAILED $id"; continue; }
    tail -2 $L/build-$id.log
    cp <runner>/kiln/packs/out/$id.sqlite <runner>/kiln/packs/out/$id.sqlite.json "$W/" && echo "copied $id -> $W"
  done
done
df -g ~ | awk 'NR==2{print "free_gib " $4}'
echo ALLDONE $(date +%T)
