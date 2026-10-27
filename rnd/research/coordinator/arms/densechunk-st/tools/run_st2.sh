#!/usr/bin/env bash
# DENSECHUNK-ST2 step 0 replays (0 LLM / 0 judge / 0 paid; MacBook). Resumable: an output that exists is skipped.
#   run_st2.sh [pack ...]   (default: kit v0.1 + v0.2, then the 9 self-test packs)
# Tree wt/packs with packDense2 "extra" (patch packdense2.vs-dt512.patch); sidecar copies in shared-data/packs/v3proto.
# Self-test: passes off,extra,off -> runs/st2-<pack>.jsonl (off = differential vs runs/st-<pack>.jsonl off; off2 = warm p50).
# Kit (sidecars on crypto + wikivoyage): passes off,on,extra,off (on = fusion differential vs the ST run) ->
#   runs/v01-kit.st2.jsonl; v0.2 -> blind/bench-v02/runs-packs/densechunk-st2-v02-kit.jsonl (script-only; stderr filtered
#   to the summary line, DIFF lines carry ids only).
set -uo pipefail
B=<workspace>; cd $B
A=$B/rnd/research/coordinator/arms/densechunk-st; R=$A/tools/replay-st.sh; O=$A/runs; O2=$B/blind/bench-v02/runs-packs
V=shared-data/packs/v3proto
KITV=$V/boar-crypto.sqlite,$V/boar-wikivoyage-en.sqlite
C=(--gate search --k 6 --tree wt/packs)
kit() {
  [ -s $O/v01-kit.st2.jsonl ] || $R "${C[@]}" --packs $KITV --questions boar-eval/bench/v0.1/questions.public.jsonl \
     --gold boar-eval/bench/v0.1/gold/sources.json --modes off,on,extra,off --out $O/v01-kit.st2.jsonl 2>&1 | grep -E '^\{|app dir|error' | sed 's/^/[v01-kit.st2] /'
  [ -s $O2/densechunk-st2-v02-kit.jsonl ] || $R "${C[@]}" --packs $KITV --questions blind/bench-v02/live/v0.2/questions.v02-new.jsonl \
     --gold boar-eval/bench/v0.2/gold/sources.json --modes off,on,extra,off --out $O2/densechunk-st2-v02-kit.jsonl 2>&1 | grep -E '^\{|app dir' | sed 's/^/[v02-kit.st2] /'
}
st() {
  local p=$1 q=rnd/research/packs/selftest/$1.jsonl
  [ -s $O/st2-$p.jsonl ] || $R "${C[@]}" --packs $KITV,$V/$p.sqlite --questions $q --gold none --modes off,extra,off \
     --out $O/st2-$p.jsonl 2>&1 | grep -E '^\{|app dir|error' | sed "s/^/[st2 $p] /"
}
LIST="${*:-kit boar-medlineplus-en boar-factbook qa-health-se boar-firstaid-en qa-outdoors-se qa-bitcoin-se qa-ethereum-se qa-travel-se boar-simplewiki-en}"
for x in $LIST; do if [ "$x" = kit ]; then kit; else st "$x"; fi; done
echo RUN-ST2-DONE
