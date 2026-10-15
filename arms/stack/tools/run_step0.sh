#!/usr/bin/env bash
# STACK step 0 replays (0 LLM / 0 judge / 0 paid; MacBook only; criterion sha 56ed7ccf…). Resumable: an existing output is skipped.
#   run_step0.sh [st180] [v01] [v02]   (default: all)
# Tree wt/groundst (dt512 + T-K2 + PACKROUTE quota + packGround incl. "perpack"). Packs = the published files.
#  st180: kit + all 9 packs, the 180 self-test items, modes off,stack,off,stack,quota,perpack (P, X, P warm, X warm, components)
#  v01  : v0.1 public 60, kit only and kit + all 9, modes off,stack,off
#  v02  : v0.2 110, kit only and kit + all 9 -> $HELDOUT_DIR/bench-v02/runs-packs/stack-v02-{kit,all9}.jsonl (script-only; stderr = summary line only)
set -uo pipefail
B=$BOAR_WS; cd $B
A=$B/rnd/research/coordinator/arms/stack; R=$A/tools/replay-stack.sh; O=$A/runs; O2=$HELDOUT_DIR/bench-v02/runs-packs
mkdir -p $O $O2
KIT=shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite
PACKS="qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en"
pub() { case "$1" in boar-factbook|boar-simplewiki-en) echo shared-data/packs/wave2/$1.sqlite;; *) echo shared-data/packs/wave1/$1.sqlite;; esac; }
ALL=$KIT; for p in $PACKS; do ALL="$ALL,$(pub $p)"; done
C=(--gate search --k 6 --tree wt/groundst)
V01=(--questions boar-eval/bench/v0.1/questions.public.jsonl --gold boar-eval/bench/v0.1/gold/sources.json)
V02=(--questions $HELDOUT_DIR/bench-v02/live/v0.2/questions.v02-new.jsonl --gold boar-eval/bench/v0.2/gold/sources.json)
ST=$B/rnd/research/coordinator/arms/packroute/runs/st180.questions.jsonl
st180() { [ -s $O/st180-all9.jsonl ] || $R "${C[@]}" --packs $ALL --questions $ST --gold none --modes off,stack,off,stack,quota,perpack --out $O/st180-all9.jsonl 2>&1 | grep -E '^\{' | sed 's/^/[st180] /'; }
v01() {
  [ -s $O/v01-kit.jsonl ] || $R "${C[@]}" --packs $KIT "${V01[@]}" --modes off,stack,off --out $O/v01-kit.jsonl 2>&1 | grep -E '^\{' | sed 's/^/[v01-kit] /'
  [ -s $O/v01-all9.jsonl ] || $R "${C[@]}" --packs $ALL "${V01[@]}" --modes off,stack,off --out $O/v01-all9.jsonl 2>&1 | grep -E '^\{' | sed 's/^/[v01-all9] /'
}
v02() {
  [ -s $O2/stack-v02-kit.jsonl ] || $R "${C[@]}" --packs $KIT "${V02[@]}" --modes off,stack,off --out $O2/stack-v02-kit.jsonl 2>&1 | grep -E '^\{' | sed 's/^/[v02-kit] /'
  [ -s $O2/stack-v02-all9.jsonl ] || $R "${C[@]}" --packs $ALL "${V02[@]}" --modes off,stack,off --out $O2/stack-v02-all9.jsonl 2>&1 | grep -E '^\{' | sed 's/^/[v02-all9] /'
}
for x in ${*:-st180 v01 v02}; do case $x in st180) st180;; v01) v01;; v02) v02;; esac; done
echo RUN-STEP0-DONE
