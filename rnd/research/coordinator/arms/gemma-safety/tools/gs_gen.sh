#!/bin/bash
# GEMMA-SAFETY mini-side driver (nohup on the mini). Usage: gs_gen.sh <job dir>
# <job dir>: tree/ (APFS clone of <runner>/kiln/be-cut7-warn = MacBook kiln-local/be-cut7-warn src + the mini's litepacks be/node_modules + be/vendor-protocol),
# gs-probes65-{1p7b,gemma}.requests.jsonl. Runs 1p7b (adapter-litesafety.ts) then gemma (adapter-gemmasafety.ts), one slot (gen1|gen2 lock as lp-screens mini_gen.sh).
# Env as LITESAFETY run_ls.sh: NUMGUARD=1 HEALTHGAP=1 WARN=1, BOAR_SERVER_EXTRA_ARGS="--reasoning off" (both: same model id), pack dirs wave2:wave1:packs:crypto.
# Guards: ARM/COMMIT/answer.ts/warn.ts/adapter pins, engine never reads the env switches, detector :8094 up (never started/stopped here),
# <= 2 non-detector llama-servers (bin/llama-server -m), disk >= 25 GiB. Resumable (<name>.done). STATUS last line DONE | FAIL ...
set -u
J=$1; K=<runner>/kiln; T=$J/tree; S=$J/STATUS; SL=$K/slots
export PATH=/opt/homebrew/bin:$PATH
MD=$HOME/boar/shared-models/emergency-detector; SRV=$HOME/boar/spikes/llama-b11010/build-cpu/bin/llama-server; DATA=$HOME/boar/shared-data
echo "queued $(date +%s) $(date '+%F %T') host=$(hostname -s)" >> $S
mkdir -p $SL; SLOT=""
while [ -z "$SLOT" ]; do
  for s in gen1 gen2; do
    if [ -d $SL/$s ] && [ -f $SL/$s.owner ]; then op=$(awk '{print $1}' $SL/$s.owner); kill -0 "$op" 2>/dev/null || { rm -f $SL/$s.owner; rmdir $SL/$s 2>/dev/null && echo "reclaimed stale $s (pid $op)" >> $S; }; fi
    if mkdir $SL/$s 2>/dev/null; then SLOT=$s; echo "$$ $(date '+%F %T') $J" > $SL/$s.owner; break; fi
  done
  [ -z "$SLOT" ] && sleep 20
done
trap 'rm -f $SL/$SLOT.owner; rmdir $SL/$SLOT 2>/dev/null' EXIT
echo "slot $SLOT $(date '+%F %T')" >> $S
fail() { echo "FAIL $*" >> $S; exit 1; }
cd $T || fail "no tree"
[ "$(cat ARM)" = pr1+warn ] && [ "$(cat COMMIT)" = 8ac9eb7a0f79d9983a5712079379f595f3e4ad73 ] || fail ARM/COMMIT
[ "$(shasum -a 256 src/routing/answer.ts | cut -c1-16)" = a88374f906f6a7de ] && [ "$(shasum -a 256 src/routing/warn.ts | cut -c1-16)" = d79357cbab07cbd8 ] || fail "answer/warn pins"
grep -q 'process.env.WARN\|process.env.HEALTHGAP\|process.env.NUMGUARD' src/routing/*.ts && fail "engine reads env"
[ "$(shasum -a 256 be/adapter-litesafety.ts | cut -c1-16)" = e0ea51a998d04f11 ] && [ "$(shasum -a 256 be/adapter-gemmasafety.ts | cut -c1-16)" = bd9fe7a8e2eb4774 ] || fail "adapter pins"
export NUMGUARD=1 HEALTHGAP=1 WARN=1 BOAR_SERVER_EXTRA_ARGS="--reasoning off"
export BOAR_EVAL_PACK_DIRS=$DATA/packs/wave2:$DATA/packs/wave1:$DATA/packs:$DATA/crypto
export BOAR_SHARED_MODELS=$HOME/boar/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 \
  BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
run() { # run <sys> <adapter>
  local n=gs-probes65-$1-s42 rq=$J/gs-probes65-$1.requests.jsonl tr=$J/gs-probes65-$1-s42.traces.jsonl
  [ -f $J/$n.done ] && { echo "skip $n" >> $S; return 0; }
  while [ "$(pgrep -f 'bin/llama-server -m' | while read p; do ps -o command= -p $p; done | grep -vc -- '--port 8094')" -ge 2 ]; do sleep 20; done
  curl -sf http://127.0.0.1:8094/health > /dev/null || fail "detector :8094 down (not started here)"
  FREE=$(df -g ~ | awk 'NR==2{print $4}'); [ "$FREE" -ge 25 ] || fail "disk ${FREE} GiB < 25"
  rm -f $tr; echo "start $n $(date +%s) $(date '+%T') free=${FREE}GiB adapter=$2" >> $S
  be/node_modules/tsx/dist/cli.mjs be/$2 --requests $rq --out $tr --backend server --server-bin $SRV --threads 4 --timeout-ms 600000 > $J/$n.log 2>&1; rc=$?
  local nr=$(wc -l < $tr 2>/dev/null | tr -d ' '); local ne=$(grep -c '"error":{' $tr 2>/dev/null)
  echo "end $n $(date +%s) rc=$rc rows=$nr errors=$ne" >> $S
  [ $rc = 0 ] && [ "$nr" = "$(wc -l < $rq | tr -d ' ')" ] && [ "$ne" = 0 ] || fail "$n rc=$rc rows=$nr errors=$ne"
  touch $J/$n.done
}
run 1p7b adapter-litesafety.ts
run gemma adapter-gemmasafety.ts
echo DONE >> $S
