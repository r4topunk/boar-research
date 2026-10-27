#!/bin/bash
# DRIFT17 mini-side generation driver (nohup on the mini). Usage: d17_gen.sh <job dir>
# <job dir> holds tree/ (APFS clone of <runner>/kiln/be-0cfd4a77-cut7-litepacks), cfg.json, questions.jsonl, mkreq_d17.py.
# System = LITEPACKS K0 lite (mini_gen.sh env: LITEDECLINE_OFF=5, --reasoning off, Qwen3-1.7B via adapter-litedecline.ts, b11010 CPU -t 4).
# Order: B standalone (80) -> A waves 1..15 (history = earlier turns + this run's answers); smoke gate after wave 2. Slot lock gen1|gen2 as mini_gen.sh.
# Resumable: a step whose <name>.done exists is skipped. Writes STATUS (last line DONE | FAIL ...).
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
[ "$(cat ARM)" = cut7-headpass-x2+litepacks ] || fail ARM
[ "$(shasum -a 256 src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] || fail "answer.ts sha"
[ "$(shasum -a 256 be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] || fail "adapter sha"
export BOAR_EVAL_PACK_DIRS=$DATA/packs/v3proto:$DATA/packs/wave3:$DATA/packs/wave2:$DATA/packs/wave1:$DATA/packs:$DATA/crypto
export BOAR_SHARED_MODELS=$HOME/boar/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 \
  BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
export BOAR_SERVER_EXTRA_ARGS="--reasoning off" LITEDECLINE_OFF=5
run() { # run <name>: requests $J/<name>.requests.jsonl -> traces
  local n=$1 rq=$J/$1.requests.jsonl tr=$J/$1.traces.jsonl
  [ -f $J/$n.done ] && { echo "skip $n" >> $S; return 0; }
  while [ "$(pgrep -f 'bin/llama-server -m' | while read p; do ps -o command= -p $p; done | grep -vc -- '--port 8094')" -ge 2 ]; do sleep 20; done
  curl -sf http://127.0.0.1:8094/health > /dev/null || fail "detector :8094 down (not started here)"
  FREE=$(df -g ~ | awk 'NR==2{print $4}'); [ "$FREE" -ge 25 ] || fail "disk ${FREE} GiB < 25"
  rm -f $tr; echo "start $n $(date +%s) $(date '+%T') free=${FREE}GiB rows=$(wc -l < $rq | tr -d ' ')" >> $S
  be/node_modules/tsx/dist/cli.mjs be/adapter-litedecline.ts --requests $rq --out $tr --backend server --server-bin $SRV \
    --threads 4 --timeout-ms 600000 > $J/$n.log 2>&1; rc=$?
  local nr=$(wc -l < $tr 2>/dev/null | tr -d ' '); local ne=$(grep -c '"error":{' $tr 2>/dev/null)
  echo "end $n $(date +%s) rc=$rc rows=$nr errors=$ne" >> $S
  [ $rc = 0 ] && [ "$nr" = "$(wc -l < $rq | tr -d ' ')" ] && [ "$ne" = 0 ] || fail "$n rc=$rc rows=$nr errors=$ne"
  touch $J/$n.done
}
python3 -I $J/mkreq_d17.py $J/cfg.json standalone $J/questions.jsonl d17-standalone-s42 $J/d17-standalone-s42.requests.jsonl >> $S || fail mkreq
run d17-standalone-s42
SE=d17-session-s42; [ -f $J/$SE.traces.jsonl ] || : > $J/$SE.traces.jsonl
for k in $(seq 1 15); do W=$SE-t$k
  if [ ! -f $J/$W.done ]; then
    python3 -I $J/mkreq_d17.py $J/cfg.json session $J/questions.jsonl $SE $J/$W.requests.jsonl $k $J/$SE.traces.jsonl >> $S || fail "mkreq $W"
    run $W; cat $J/$W.traces.jsonl >> $J/$SE.traces.jsonl
  fi
  if [ $k = 2 ] && [ ! -f $J/smoke.ok ]; then
    python3 -I - $J/$SE-t2.traces.jsonl $J/d17-standalone-s42.traces.jsonl >> $S <<'PY' || fail "smoke (history did not reach the prompt)"
import json,sys
rd=lambda p:{t["itemId"]:t for t in map(json.loads,open(p))}
A,B=rd(sys.argv[1]),rd(sys.argv[2]); c=g=0
for i,a in A.items():
    pa=(a.get("timing") or {}).get("promptTokens"); pb=(B[i].get("timing") or {}).get("promptTokens")
    if pa and pb: c+=1; g+=pa>pb
print(f"smoke t2: A>B promptTokens {g}/{c}"); sys.exit(0 if c and g*2>=c else 1)
PY
    touch $J/smoke.ok
  fi
done
echo DONE >> $S
