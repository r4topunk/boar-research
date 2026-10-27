#!/usr/bin/env bash
# DENSECHUNK-ST step 0 replays (0 LLM / 0 judge / 0 paid; MacBook). Resumable: an output that exists is skipped.
#   run_st.sh [pack ...]   (default: kit no-harm v0.1 + v0.2, then the 9 self-test packs in sidecar order)
# Per self-test pack: wt/packs (packDense2 patch) with kit + pack from shared-data/packs/v3proto, passes off,on,off (+ qvec)
#   -> runs/st-<pack>.jsonl; differential: wt/packs-tk2base (T-K2 only) with the PUBLISHED files, pass off -> runs/st-<pack>.tk2.jsonl.
# Kit only (sidecars on crypto + wikivoyage): v0.1 public -> runs/v01-kit*.jsonl; v0.2 -> blind/bench-v02/runs-packs/densechunk-st-v02-kit*.jsonl
#   (script-only; stderr filtered to the summary line).
set -uo pipefail
B=<workspace>; cd $B
A=$B/rnd/research/coordinator/arms/densechunk-st; R=$A/tools/replay-st.sh; O=$A/runs; O2=$B/blind/bench-v02/runs-packs
V=shared-data/packs/v3proto; WK=shared-data/packs/work/densechunk; TK2=wt/packs-tk2base
KITV=$V/boar-crypto.sqlite,$V/boar-wikivoyage-en.sqlite
KITP=shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite
pub() { case "$1" in boar-factbook|boar-simplewiki-en) echo shared-data/packs/wave2/$1.sqlite;; *) echo shared-data/packs/wave1/$1.sqlite;; esac; }
waitfor() { while [ ! -f "$WK/$1.sidecar.json" ]; do sleep 60; done; }
C=(--gate search --k 6)
kit() {
  waitfor crypto; waitfor wikivoyage
  [ -s $O/v01-kit.jsonl ] || $R "${C[@]}" --tree wt/packs --packs $KITV --questions boar-eval/bench/v0.1/questions.public.jsonl \
     --gold boar-eval/bench/v0.1/gold/sources.json --modes off,on,off --out $O/v01-kit.jsonl 2>&1 | grep -E '^\{|app dir|DIFF|error' | sed 's/^/[v01-kit] /'
  [ -s $O/v01-kit.tk2.jsonl ] || $R "${C[@]}" --tree $TK2 --packs $KITP --questions boar-eval/bench/v0.1/questions.public.jsonl \
     --gold boar-eval/bench/v0.1/gold/sources.json --modes off --out $O/v01-kit.tk2.jsonl 2>&1 | grep -E '^\{|app dir' | sed 's/^/[v01-kit.tk2] /'
  [ -s $O2/densechunk-st-v02-kit.jsonl ] || $R "${C[@]}" --tree wt/packs --packs $KITV --questions blind/bench-v02/live/v0.2/questions.v02-new.jsonl \
     --gold boar-eval/bench/v0.2/gold/sources.json --modes off,on,off --out $O2/densechunk-st-v02-kit.jsonl 2>&1 | grep -E '^\{|app dir' | sed 's/^/[v02-kit] /'
  [ -s $O2/densechunk-st-v02-kit.tk2.jsonl ] || $R "${C[@]}" --tree $TK2 --packs $KITP --questions blind/bench-v02/live/v0.2/questions.v02-new.jsonl \
     --gold boar-eval/bench/v0.2/gold/sources.json --modes off --out $O2/densechunk-st-v02-kit.tk2.jsonl 2>&1 | grep -E '^\{|app dir' | sed 's/^/[v02-kit.tk2] /'
}
st() {
  local p=$1 q=rnd/research/packs/selftest/$1.jsonl
  waitfor $p
  [ -s $O/st-$p.jsonl ] || $R "${C[@]}" --tree wt/packs --packs $KITV,$V/$p.sqlite --questions $q --gold none --modes off,on,off --qvec \
     --out $O/st-$p.jsonl 2>&1 | grep -vE 'node-llama-cpp' | sed "s/^/[st $p] /"
  [ -s $O/st-$p.tk2.jsonl ] || $R "${C[@]}" --tree $TK2 --packs $KITP,$(pub $p) --questions $q --gold none --modes off \
     --out $O/st-$p.tk2.jsonl 2>&1 | grep -E '^\{|app dir' | sed "s/^/[st.tk2 $p] /"
}
LIST="${*:-kit boar-medlineplus-en boar-factbook qa-health-se boar-firstaid-en qa-outdoors-se qa-bitcoin-se qa-ethereum-se qa-travel-se boar-simplewiki-en}"
for x in $LIST; do if [ "$x" = kit ]; then kit; else st "$x"; fi; done
echo RUN-ST-DONE
