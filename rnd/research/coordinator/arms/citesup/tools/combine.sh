#!/bin/bash
# CITESUP: combine patches (applied in order, -p1, to the lp-screens base tree) into one candidate patch. Usage: combine.sh <out.patch> <p1> [p2 ...]
set -eu
OUT=$1; shift; B=<workspace>/kiln-local/be-0cfd4a77-cut7-litepacks; T=$(mktemp -d)
mkdir -p $T/a $T/b
FILES=$(cat "$@" | grep -E '^\+\+\+ b/' | awk '{print $2}' | sed 's#^b/##' | sort -u)
for f in $FILES; do mkdir -p $T/a/$(dirname $f) $T/b/$(dirname $f); [ -f $B/$f ] && cp $B/$f $T/a/$f && cp $B/$f $T/b/$f || true; done
for p in "$@"; do (cd $T/b && patch -p1 -s --no-backup-if-mismatch < $p); done
(cd $T && diff -ruN a b > $OUT) || true
patch -p1 --dry-run -s -d $B < $OUT && echo "combined $(basename $OUT) $(shasum -a 256 $OUT | cut -c1-16) files: $FILES"
rm -rf $T
