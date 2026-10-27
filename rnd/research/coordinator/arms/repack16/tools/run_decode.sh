#!/bin/bash
# REPACK16: MacBook fzstd decode time per search for the logged miss sequences. usage: run_decode.sh <replay out> <packs root>
OUT=$1; PR=$2; P=<workspace>/shared-data/packs/persona-a-union; T=$(dirname "$0")
O="boar-crypto boar-factbook boar-firstaid-en boar-medlineplus-en boar-visa-en"
m64=(); mA16=(); m6=()
for p in $O; do m64+=("$p=$P/$p.sqlite"); mA16+=("$p=$P/$p.sqlite"); m6+=("$p=$PR/all16/$p.sqlite"); done
m64+=("boar-wikivoyage-en=$P/boar-wikivoyage-en.sqlite"); mA16+=("boar-wikivoyage-en=$PR/wv16/boar-wikivoyage-en.sqlite"); m6+=("boar-wikivoyage-en=$PR/wv16/boar-wikivoyage-en.sqlite")
for o in S M; do
  node $T/decode_bench.mjs $OUT/A-$o-64-16.blocklog.jsonl "${m64[@]}"
  node $T/decode_bench.mjs $OUT/A-$o-64-64.blocklog.jsonl "${m64[@]}"
  node $T/decode_bench.mjs $OUT/A-$o-16-64.blocklog.jsonl "${mA16[@]}"
  for c in 16 64 256; do node $T/decode_bench.mjs $OUT/A6-$o-16-$c.blocklog.jsonl "${m6[@]}"; done
done 2>&1 | grep -v Warn
