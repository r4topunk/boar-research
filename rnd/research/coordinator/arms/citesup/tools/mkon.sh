#!/bin/bash
# CITESUP: min3v-citesup-log.patch with the adapter default switched to "on" at tau (same line count, so hunks stay valid). Usage: mkon.sh <tau>
set -eu
H=$(cd "$(dirname "$0")/.." && pwd); TAU=$1
sed "s|^+process.env.BOAR_CITESUP ??= \"log\";|+process.env.BOAR_CITESUP ??= \"on\"; process.env.BOAR_CITESUP_TAU ??= \"$TAU\";|" $H/min3v-citesup-log.patch > $H/min3v-citesup-on.patch
grep -c "BOAR_CITESUP_TAU ??= \"$TAU\"" $H/min3v-citesup-on.patch
patch -p1 --dry-run -s -d <workspace>/kiln-local/be-0cfd4a77-cut7-litepacks < $H/min3v-citesup-on.patch && echo "ok $(shasum -a 256 $H/min3v-citesup-on.patch | cut -c1-16)"
