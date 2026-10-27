#!/bin/bash
# RETFLOOR mini job (0 LLM generation, 0 judge): stub llama-server + the real LITEPACKS adapter (be/adapter-litedecline.ts) on a
# COPY of <runner>/kiln/be-0cfd4a77-cut7-litepacks patched by apply_retfloor.py (env RETFLOOR_VARIANT). Same env as lp-screens mini_gen.sh.
# Usage: bash mini_rf.sh <job dir> <variants...>   (job dir holds apply_retfloor.py, stub_server.py, req/MAIN|PM.requests.jsonl)
# Slot lock: atomic mkdir <runner>/kiln/slots/gen1|gen2, owner in genN.owner, removed on exit (stale owner reclaimed).
set -u
J=$1; shift; K=<runner>/kiln; SL=$K/slots; S=$J/STATUS; export PATH=/opt/homebrew/bin:$PATH
DATA=$HOME/boar/shared-data; MD=$HOME/boar/shared-models/emergency-detector; SRV=$HOME/boar/spikes/llama-b11010/build-cpu/bin/llama-server
echo "queued $(date '+%F %T')" > $S; SLOT=""
while [ -z "$SLOT" ]; do
  for s in gen1 gen2; do
    if [ -d $SL/$s ] && [ -f $SL/$s.owner ]; then op=$(awk '{print $1}' $SL/$s.owner); kill -0 "$op" 2>/dev/null || { rm -f $SL/$s.owner; rmdir $SL/$s 2>/dev/null && echo "reclaimed stale $s" >> $S; }; fi
    if mkdir $SL/$s 2>/dev/null; then SLOT=$s; echo "$$ $(date '+%F %T') $J" > $SL/$s.owner; break; fi
  done
  [ -z "$SLOT" ] && sleep 20
done
STUB=""
trap 'rm -f $SL/$SLOT.owner; rmdir $SL/$SLOT 2>/dev/null; [ -n "$STUB" ] && kill $STUB 2>/dev/null' EXIT
echo "slot $SLOT $(date '+%F %T')" >> $S
fail() { echo "FAIL $*" >> $S; exit 1; }
FREE=$(df -g ~ | awk 'NR==2{print $4}'); [ "$FREE" -ge 25 ] || fail "disk ${FREE} GiB < 25"
curl -sf http://127.0.0.1:8094/health > /dev/null || fail "detector :8094 down (not started here)"
T=$J/be-0cfd4a77-cut7-litepacks-retfloor
if [ ! -d $T ]; then cp -c -R $K/be-0cfd4a77-cut7-litepacks $T && rm -rf $T/be/.cache && python3 -I $J/apply_retfloor.py $T >> $S || fail "tree"; fi
cd $T || fail "no tree"
echo "tree answer.ts=$(shasum -a 256 src/routing/answer.ts | cut -c1-16) orig=$(shasum -a 256 $K/be-0cfd4a77-cut7-litepacks/src/routing/answer.ts | cut -c1-16)" >> $S
PORT=18777; python3 -I $J/stub_server.py $PORT $HOME/boar/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf & STUB=$!; sleep 1
export BOAR_EVAL_PACK_DIRS=$DATA/packs/v3proto:$DATA/packs/wave3:$DATA/packs/wave2:$DATA/packs/wave1:$DATA/packs:$DATA/crypto
export BOAR_SHARED_MODELS=$HOME/boar/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 \
  BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal BOAR_SERVER_EXTRA_ARGS="--reasoning off" LITEDECLINE_OFF=5
mkdir -p $J/out
SETS="MAIN $(cd $J/req && ls PM-*.requests.jsonl | sed "s/.requests.jsonl//" | tr "\n" " ")"
for V in "$@"; do for SET in $SETS; do
  O=$J/out/$V-$SET; [ -s $O.traces.jsonl ] && [ "$(wc -l < $O.traces.jsonl)" = "$(wc -l < $J/req/$SET.requests.jsonl)" ] && continue
  rm -f $O.traces.jsonl $O.prompts.jsonl; t0=$(date +%s)
  RETFLOOR_VARIANT=$V be/node_modules/tsx/dist/cli.mjs be/adapter-litedecline.ts --requests $J/req/$SET.requests.jsonl --out $O.traces.jsonl \
    --backend server --server-bin $SRV --server-url http://127.0.0.1:$PORT --dump-prompts $O.prompts.jsonl --threads 4 --timeout-ms 600000 > $O.log 2>&1
  echo "$V $SET rc=$? rows=$(wc -l < $O.traces.jsonl | tr -d ' ') $(( $(date +%s) - t0 ))s" >> $S
done; done
echo DONE >> $S
