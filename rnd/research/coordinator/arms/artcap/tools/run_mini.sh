#!/bin/bash
# ARTCAP replay on the Mac mini (0 LLM; criterion 4069ae83): same recipe as run.sh, mini paths, embedder threads 4 (BOAR_EMBED_THREADS, mini shim copy only).
# usage (on the mini): run_mini.sh <main|st> <label> [RS_ARTCAP=...]
set -u
export PATH=/opt/homebrew/bin:$PATH
MK=<runner>/kiln/artcap; IN=$MK/in; K=<runner>/kiln/compose/packs-k13; V=<runner>/shared-data/packs/v3proto
export BOAR_REPLAY_CACHE=$MK/cache BOAR_SHARED_MODELS=<runner>/shared-models BOAR_REPLAY_NODE_MODULES=<runner>/eval-runner/eval/node_modules BOAR_EMBED_THREADS=4
TSX=<runner>/eval-runner/eval/node_modules/.bin/tsx; TOOL=$MK/tools/replay-artcap-mini.ts; TREE=$MK/rs-ARTCAP
SET=$1; LAB=$2; shift 2; t0=$(date +%s); cd $MK
ENV="RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1"
PK=$(for p in boar-crypto boar-wikivoyage-en boar-simplewiki-en qa-cooking-se qa-money-se boar-factbook boar-medlineplus-en boar-firstaid-en boar-visa-en qa-health-se qa-travel-se qa-outdoors-se wiki-vital5; do printf "%s," $K/$p.sqlite; done | sed 's/,$//')
if [ $SET = main ]; then
  OUT=$MK/replays/main.$LAB.jsonl
  env $ENV "$@" $TSX $TOOL --questions $IN/dg-S-K1-main-s42.requests.jsonl --tree $TREE --packs $PK \
    --tasks-from $IN/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
    --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $OUT 2> $OUT.err
  echo "mini main $LAB rc=$? $(( $(date +%s) - t0 ))s [$*] $(tail -1 $OUT.err | cut -c1-120)"
else
  OUT=$MK/replays/st.$LAB.jsonl; : > $OUT
  for g in on-k13 on-k13+qa-bitcoin-se on-k13+qa-ethereum-se; do
    P=$PK; case $g in *bitcoin*) P=$PK,$V/qa-bitcoin-se.sqlite;; *ethereum*) P=$PK,$V/qa-ethereum-se.sqlite;; esac
    O=$MK/replays/st.$LAB.$g.jsonl
    env $ENV "$@" $TSX $TOOL --questions $IN/$g.requests.jsonl --tree $TREE --packs $P \
      --tasks-from $IN/$g.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
      --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $O 2> $O.err
    echo "mini st $LAB $g rc=$? $(tail -1 $O.err | cut -c1-120)"; cat $O >> $OUT
  done
  echo "mini st $LAB rows=$(wc -l < $OUT) $(( $(date +%s) - t0 ))s [$*]"
fi
