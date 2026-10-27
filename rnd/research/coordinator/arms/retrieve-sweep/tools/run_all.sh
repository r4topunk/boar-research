#!/bin/bash
# RETRIEVE-SWEEP stage 1: every replay, sequential (wall times comparable). 0 LLM.
set -u
cd <workspace>/rnd/research/coordinator/arms/retrieve-sweep
K=<workspace>/kiln-local; QQ=../qform/items/qform.questions.jsonl; MQ=../decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl
K1='{"packHeadPass":"a2","packDense2":"append-budget"}'
R() { local name=$1; shift; local t0=$(date +%s); echo "== $name"; "$@" 2>&1 | grep -E '^\{"n"|FATAL|NEW' ; echo "   $(( $(date +%s) - t0 ))s"; }
for S in "$@"; do case $S in
  base)  R B0w.qform env -u RS_X tools/replay.sh $K/be-0cfd4a77-cut7-litepacks $QQ replay/B0w.qform.jsonl qform
         R B1w.qform tools/replay.sh $K/be-0cfd4a77-cut7-litepacks $QQ replay/B1w.qform.jsonl qform --forward-opts --settings-json "$K1"
         R B0.main tools/replay.sh $K/be-0cfd4a77-cut7-litepacks $MQ replay/B0.main.jsonl main ;;
  A)     for t in 0.78 0.74; do R A$t.qform env RS_GROUND_DENSE=$t tools/replay.sh $K/rs-A $QQ replay/A$t.qform.jsonl qform
                                R A$t.main env RS_GROUND_DENSE=$t tools/replay.sh $K/rs-A $MQ replay/A$t.main.jsonl main; done ;;
  B)     R B.qform env RS_KEYQ=1 tools/replay.sh $K/rs-B $QQ replay/B.qform.jsonl qform
         R B.main env RS_KEYQ=1 tools/replay.sh $K/rs-B $MQ replay/B.main.jsonl main ;;
  D)     R D.off20 tools/replay.sh $K/rs-D replay/proof20.questions.jsonl replay/D.off20.jsonl qform
         python3 -I tools/proofdiff.py ../qform/replay/qform.replay.jsonl replay/D.off20.jsonl
         R D.qform env RS_DIVERSITY=1 tools/replay.sh $K/rs-D $QQ replay/D.qform.jsonl qform
         R D.main env RS_DIVERSITY=1 tools/replay.sh $K/rs-D $MQ replay/D.main.jsonl main ;;
  E)     R E.off20 tools/replay.sh $K/rs-E replay/proof20.questions.jsonl replay/E.off20.jsonl qform
         python3 -I tools/proofdiff.py ../qform/replay/qform.replay.jsonl replay/E.off20.jsonl
         R E.qform env RS_MINSIM=0.62 tools/replay.sh $K/rs-E $QQ replay/E.qform.jsonl qform
         R E.main env RS_MINSIM=0.62 tools/replay.sh $K/rs-E $MQ replay/E.main.jsonl main ;;
  C)     R C.qform env RS_SIBLING=1 tools/replay.sh $K/rs-C $QQ replay/C.qform.jsonl qform --forward-opts --settings-json "$K1"
         R C.main env RS_SIBLING=1 tools/replay.sh $K/rs-C $MQ replay/C.main.jsonl main ;;
  F)     R F.off20 tools/replay.sh $K/rs-F replay/proof20.questions.jsonl replay/F.off20.jsonl qform
         python3 -I tools/proofdiff.py ../qform/replay/qform.replay.jsonl replay/F.off20.jsonl
         R F.qform env $FENV tools/replay.sh $K/rs-F $QQ replay/F.qform.jsonl qform $FARGS
         R F.main env $FENV tools/replay.sh $K/rs-F $MQ replay/F.main.jsonl main ;;
esac; done
echo ALLDONE
