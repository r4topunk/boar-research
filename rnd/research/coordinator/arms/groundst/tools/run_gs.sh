#!/usr/bin/env bash
# GROUND-ST step 0 replays (0 LLM / 0 judge / 0 paid; MacBook only). Resumable: an output that exists is skipped.
#   run_gs.sh [kit|<pack> ...]   (default: kit v0.1 + v0.2, then the 9 self-test packs)
#   GS_VARIANT=perpack run_gs.sh  (addendum 1, X3): passes off,perpack,off -> outputs with a ".perpack" suffix
#   (runs/gs-<pack>.perpack.jsonl, runs/v01-kit.gs.perpack.jsonl, blind/.../groundst-v02-kit.perpack.jsonl); stderr = summary line only.
# Tree wt/groundst (wt/packs + packGround true | "top1"); published files only (no sidecars), packDense2/packRoute absent.
# Passes off,ground,top1,off (off2 = warm p50 and repeat identity). Self-test: kit + that pack -> runs/gs-<pack>.jsonl.
# Kit only: v0.1 public -> runs/v01-kit.gs.jsonl; v0.2 -> blind/bench-v02/runs-packs/groundst-v02-kit.jsonl (script-only;
# stderr filtered to the JSON summary line and the cache line; no item text is printed).
set -uo pipefail
B=<workspace>; cd $B
A=$B/rnd/research/coordinator/arms/groundst; R=$A/tools/replay-gs.sh; O=$A/runs; O2=$B/blind/bench-v02/runs-packs
KIT=shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite
pub() { case "$1" in boar-factbook|boar-simplewiki-en) echo shared-data/packs/wave2/$1.sqlite;; *) echo shared-data/packs/wave1/$1.sqlite;; esac; }
V=${GS_VARIANT:-}
if [ -n "$V" ]; then SFX=".$V"; MODES=off,$V,off; F='^\{'; else SFX=""; MODES=off,ground,top1,off; F='^\{|app dir'; fi
C=(--gate search --k 6 --tree wt/groundst --modes $MODES)
kit() {
  [ -s $O/v01-kit.gs$SFX.jsonl ] || $R "${C[@]}" --packs $KIT --questions boar-eval/bench/v0.1/questions.public.jsonl \
     --gold boar-eval/bench/v0.1/gold/sources.json --out $O/v01-kit.gs$SFX.jsonl 2>&1 | grep -E "$F" | sed 's/^/[v01-kit.gs] /'
  [ -s $O2/groundst-v02-kit$SFX.jsonl ] || $R "${C[@]}" --packs $KIT --questions blind/bench-v02/live/v0.2/questions.v02-new.jsonl \
     --gold boar-eval/bench/v0.2/gold/sources.json --out $O2/groundst-v02-kit$SFX.jsonl 2>&1 | grep -E "$F" | sed 's/^/[v02-kit.gs] /'
}
st() {
  local p=$1 q=rnd/research/packs/selftest/$1.jsonl
  [ -s $O/gs-$p$SFX.jsonl ] || $R "${C[@]}" --packs $KIT,$(pub $p) --questions $q --gold none \
     --out $O/gs-$p$SFX.jsonl 2>&1 | grep -E "$F" | sed "s/^/[gs $p] /"
}
LIST="${*:-kit boar-medlineplus-en boar-factbook qa-health-se boar-firstaid-en qa-outdoors-se qa-bitcoin-se qa-ethereum-se qa-travel-se boar-simplewiki-en}"
for x in $LIST; do if [ "$x" = kit ]; then kit; else st "$x"; fi; done
echo RUN-GS-DONE
