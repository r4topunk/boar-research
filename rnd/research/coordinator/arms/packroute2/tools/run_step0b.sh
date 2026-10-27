#!/usr/bin/env bash
# PACKROUTE-2 step 0b replays (0 LLM / 0 judge / 0 paid; MacBook; criterion sha d67fd81c…). Resumable: an existing output is skipped.
#   run_step0b.sh [diff] [st180] [v01] [v02]   (default: all, in that order)
# Tree wt/packs = dt512 + T-K2 + packDense2 (never set) + PACKROUTE patch + PACKROUTE-2 llm/llmq routes mode.
#  diff : default-off identity on the new tree vs PACKROUTE's runs/diff-*.jsonl (kit only v0.1 60: off,router,quota; each
#         single pack + kit, the pack's 20 self-test items: off).
#  st180: kit + all 9 packs, the 180 self-test items, modes off,llm,llmq,off  (P, R4, R4Q, P warm) with runs/routes-st180.jsonl
#  v01  : kit + all 9 packs, v0.1 public 60, same modes, runs/routes-v01.jsonl
#  v02  : kit + all 9 packs, v0.2 110 -> blind/bench-v02/runs-packs/packroute2-all9-v02.jsonl (script-only; stderr = summary line),
#         routes blind/bench-v02/runs-packs/packroute2-v02.routes.jsonl
# WORDING=v2 selects the retry wording's routes files (suffix .v2) and output names.
set -uo pipefail
B=<workspace>; cd $B
A=$B/rnd/research/coordinator/arms/packroute2; R=$A/tools/replay-pr2.sh; O=$A/runs; O2=$B/blind/bench-v02/runs-packs
PR=$B/rnd/research/coordinator/arms/packroute
SUF=""; [ "${WORDING:-v1}" = v1 ] || SUF=".${WORDING}"
mkdir -p $O $O2
KIT=shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite
PACKS="qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en"
pub() { case "$1" in boar-factbook|boar-simplewiki-en) echo shared-data/packs/wave2/$1.sqlite;; *) echo shared-data/packs/wave1/$1.sqlite;; esac; }
ALL=$KIT; for p in $PACKS; do ALL="$ALL,$(pub $p)"; done
C=(--gate search --k 6 --tree wt/packs)
V01=(--questions boar-eval/bench/v0.1/questions.public.jsonl --gold boar-eval/bench/v0.1/gold/sources.json)
ST=$PR/runs/st180.questions.jsonl
diffrun() {
  [ -s $O/diff-v01-kit.jsonl ] || $R "${C[@]}" --packs $KIT "${V01[@]}" --modes off,router,quota --out $O/diff-v01-kit.jsonl 2>&1 | grep -E '^\{' | sed 's/^/[diff v01-kit] /'
  for p in $PACKS; do
    [ -s $O/diff-st-$p.jsonl ] || $R "${C[@]}" --packs $KIT,$(pub $p) --questions rnd/research/packs/selftest/$p.jsonl --gold none --modes off \
      --out $O/diff-st-$p.jsonl 2>&1 | grep -E '^\{' | sed "s/^/[diff st $p] /"
  done
}
st180() { [ -s $O/all9-st180$SUF.jsonl ] || $R "${C[@]}" --packs $ALL --questions $ST --gold none --modes off,llm,llmq,off --routes $O/routes-st180$SUF.jsonl \
  --out $O/all9-st180$SUF.jsonl 2>&1 | grep -E '^\{' | sed 's/^/[st180] /'; }
v01() { [ -s $O/all9-v01$SUF.jsonl ] || $R "${C[@]}" --packs $ALL "${V01[@]}" --modes off,llm,llmq,off --routes $O/routes-v01$SUF.jsonl \
  --out $O/all9-v01$SUF.jsonl 2>&1 | grep -E '^\{' | sed 's/^/[v01] /'; }
v02() { [ -s $O2/packroute2-all9-v02$SUF.jsonl ] || $R "${C[@]}" --packs $ALL --questions blind/bench-v02/live/v0.2/questions.v02-new.jsonl \
  --gold boar-eval/bench/v0.2/gold/sources.json --modes off,llm,llmq,off --routes $O2/packroute2-v02$SUF.routes.jsonl \
  --out $O2/packroute2-all9-v02$SUF.jsonl 2>&1 | grep -E '^\{' | sed 's/^/[v02] /'; }
for x in ${*:-diff st180 v01 v02}; do case $x in diff) diffrun;; st180) st180;; v01) v01;; v02) v02;; esac; done
echo RUN-STEP0B-DONE
