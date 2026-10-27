#!/usr/bin/env bash
# TK2-FIX v0.2 kit no-harm (criterion TK2FIX-V02-criterion.md): cells cut7 / tk2fix, replay-tk2.sh, 0 LLM / 0 judge.
# SCRIPT-ONLY on blind: outputs under blind/bench-v02/runs-packs/; only summary lines (counts) are printed.
set -uo pipefail
B=<workspace>; cd $B
R=$B/rnd/research/coordinator/arms/packs/tk2-replay/tools/replay-tk2.sh; O=$B/blind/bench-v02/runs-packs
KIT=shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite
tree() { case "$1" in cut7) echo kiln-local/be-0cfd4a77-cut7;; tk2fix) echo kiln-local/be-0cfd4a77-cut7-tk2fix;; esac; }
for c in ${@:-cut7 tk2fix}; do
  out=$O/tk2fix-v02-kit.$c.jsonl
  [ -s $out ] && { echo "[v02 $c] done (skip)"; continue; }
  $R --gate search --k 6 --tree $(tree $c) --modes off,off --packs $KIT --questions blind/bench-v02/live/v0.2/questions.v02-new.jsonl \
     --gold boar-eval/bench/v0.2/gold/sources.json --out $out.tmp 2>&1 | grep -E '^\{"n"|app dir|rror' | sed "s/^/[v02 $c] /"
  [ -s $out.tmp ] && mv $out.tmp $out
done
echo RUN-V02-DONE
