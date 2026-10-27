#!/bin/bash
# CHATFAIL S1 scratch trees (never touches wt/pr1). Cumulative arms:
#   s1-c0 = scratch/base (wt/pr1 src + followUp.ts from upstream/fullnative-dev; run tools/setup-scratch.sh first)
#   s1-a1 = c0 + chatfail-l1.patch ; s1-a2 = a1 + chatfail-l2l3.patch ; s1-a3 = a2 + chatfail-l4.patch
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"; S="$HERE/scratch"
[ -d "$S/base/src" ] || "$HERE/tools/setup-scratch.sh"
prev=base
for step in "c0:" "a1:chatfail-l1.patch" "a2:chatfail-l2l3.patch" "a3:chatfail-l4.patch"; do
  arm="${step%%:*}"; patch="${step#*:}"; dst="$S/s1-$arm"; rm -rf "$dst"
  if [ -z "$patch" ]; then cp -R "$S/base" "$dst"; else cp -R "$S/s1-$prev" "$dst"; (cd "$dst" && patch -p1 -s < "$HERE/tools/$patch"); fi
  for d in assets locales modules; do [ -e "<workspace>/wt/pr1/$d" ] && ln -sfn "<workspace>/wt/pr1/$d" "$dst/$d"; done
  prev=$arm
done
echo ok
