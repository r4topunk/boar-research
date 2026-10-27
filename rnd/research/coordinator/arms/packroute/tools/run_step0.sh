#!/usr/bin/env bash
# PACKROUTE step 0 replays (0 LLM / 0 judge / 0 paid; MacBook; criterion sha 801e9ac9…). Resumable: an existing output is skipped.
#   run_step0.sh [diff] [st180] [v01] [v02]   (default: all, in that order)
# Tree wt/packs = dt512 + T-K2 + packDense2 (never set here) + PACKROUTE patch. Packs = the PUBLISHED files.
#  diff : default-off differential: kit only, v0.1 public 60, modes off,router,quota (router/quota have nothing to route with
#         the kit alone -> must equal off) vs densechunk-st runs/v01-kit.jsonl OFF; each self-test pack alone (kit + pack),
#         mode off vs densechunk-st runs/st-<pack>.jsonl OFF (= reference S).
#  st180: kit + all 9 packs, the 180 self-test items, modes off,router,quota,off  (P, R, Q, P warm)
#  v01  : kit + all 9 packs, v0.1 public 60, same modes
#  v02  : kit + all 9 packs, v0.2 110 -> blind/bench-v02/runs-packs/packroute-all9-v02.jsonl (script-only; stderr = summary line)
set -uo pipefail
B=<workspace>; cd $B
A=$B/rnd/research/coordinator/arms/packroute; R=$A/tools/replay-pr.sh; O=$A/runs; O2=$B/blind/bench-v02/runs-packs
mkdir -p $O $O2
KIT=shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite
PACKS="qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en"
pub() { case "$1" in boar-factbook|boar-simplewiki-en) echo shared-data/packs/wave2/$1.sqlite;; *) echo shared-data/packs/wave1/$1.sqlite;; esac; }
ALL=$KIT; for p in $PACKS; do ALL="$ALL,$(pub $p)"; done
C=(--gate search --k 6 --tree wt/packs)
V01=(--questions boar-eval/bench/v0.1/questions.public.jsonl --gold boar-eval/bench/v0.1/gold/sources.json)
ST=$O/st180.questions.jsonl
[ -s $ST ] || for p in $PACKS; do cat rnd/research/packs/selftest/$p.jsonl; done > $ST
diffrun() {
  [ -s $O/diff-v01-kit.jsonl ] || $R "${C[@]}" --packs $KIT "${V01[@]}" --modes off,router,quota --out $O/diff-v01-kit.jsonl 2>&1 | grep -E '^\{|app dir' | sed 's/^/[diff v01-kit] /'
  for p in $PACKS; do
    [ -s $O/diff-st-$p.jsonl ] || $R "${C[@]}" --packs $KIT,$(pub $p) --questions rnd/research/packs/selftest/$p.jsonl --gold none --modes off \
      --out $O/diff-st-$p.jsonl 2>&1 | grep -E '^\{|app dir' | sed "s/^/[diff st $p] /"
  done
}
st180() { [ -s $O/all9-st180.jsonl ] || $R "${C[@]}" --packs $ALL --questions $ST --gold none --modes off,router,quota,off --out $O/all9-st180.jsonl 2>&1 | grep -E '^\{|app dir' | sed 's/^/[st180] /'; }
v01() { [ -s $O/all9-v01.jsonl ] || $R "${C[@]}" --packs $ALL "${V01[@]}" --modes off,router,quota,off --out $O/all9-v01.jsonl 2>&1 | grep -E '^\{|app dir' | sed 's/^/[v01] /'; }
v02() { [ -s $O2/packroute-all9-v02.jsonl ] || $R "${C[@]}" --packs $ALL --questions blind/bench-v02/live/v0.2/questions.v02-new.jsonl \
  --gold boar-eval/bench/v0.2/gold/sources.json --modes off,router,quota,off --out $O2/packroute-all9-v02.jsonl 2>&1 | grep -E '^\{' | sed 's/^/[v02] /'; }
for x in ${*:-diff st180 v01 v02}; do case $x in diff) diffrun;; st180) st180;; v01) v01;; v02) v02;; esac; done
echo RUN-STEP0-DONE
