#!/bin/bash
# DECODE-GROUND generation on the Mac mini (LP-SCREENS job layout): APFS clone of the K1 litepacks tree + tools/dg.patch, env DG_ARM,
# lp-screens/tools/mini_gen.sh under nohup (2-slot guard, disk >= 25 GiB, detector :8094 used, never started/stopped). No judging here.
# Usage: run_dg.sh ARM REQUESTS RUN        ARM = B | S | C1 | SC | SB   (B = the patched tree with DG_ARM unset: the parity control)
#   REQUESTS: a LITEPACKS K1 requests jsonl (make one with: python3 -I ../lp-screens/tools/mkreq.py K1 <ids> <runId> cut7-headpass-x2+litepacks+dg-<arm> <out>);
#   the tree's ARM file is set to the requests' config.arm. Env: NOWAIT=1 = start the mini job and exit (STATUS on the mini: <runner>/kiln/lp-screens/jobs/RUN/STATUS);
#   DG_ALPHA / DG_BIAS / DG_PLAUS / DG_MISSING override the arm defaults (alpha 1.0, bias 2.0, plausibility off, missing logprob -30), written to the job env.
# C1/SC run llama-server with -np 2 (two slots, -c 8192 = 4096 per slot, as the single-slot baseline). Outputs: runs/traces/RUN.traces.jsonl, runs/logs/RUN.status.
set -u
ARM=$1; REQ=$2; RUN=$3
case $ARM in B|S|SA|C1|SC|SB) ;; *) echo "ARM must be B, S, SA, C1, SC or SB"; exit 2;; esac
H=<workspace>/rnd/research/coordinator/arms/decode-ground; LS=$H/../lp-screens/tools
M=MINI_HOST; MK=<runner>/kiln; BASE=$MK/be-0cfd4a77-cut7-litepacks; J=$MK/lp-screens/jobs/$RUN; PF=${DG_PATCH:-$H/tools/dg.patch}   # SA uses DG_PATCH=$H/tools/dg-sa.patch (dg.patch + the SA arm; S/SB/SC/C1 unchanged)
mkdir -p $H/runs/traces $H/runs/logs; TR=$H/runs/traces/$RUN.traces.jsonl; ST=$H/runs/logs/$RUN.status
n=$(wc -l < $REQ | tr -d ' '); CA=$(head -1 $REQ | python3 -I -c "import json,sys;print(json.loads(sys.stdin.readline())['config']['arm'])")
ENVF=$(mktemp); { [ $ARM != B ] && echo "DG_ARM=$ARM"
  case $ARM in C1|SC) echo 'BOAR_SERVER_EXTRA_ARGS="--reasoning off -np 2"'; echo "BOAR_SERVER_CTX=8192";; esac
  for v in DG_ALPHA DG_BIAS DG_PLAUS DG_MISSING; do [ -n "${!v:-}" ] && echo "$v=${!v}"; done; } > $ENVF
scp -q $LS/mini_gen.sh $M:$MK/lp-screens-mini_gen.sh || exit 1
ssh $M bash -s -- "$J" "$BASE" "$CA" <<'X' || { echo "FAIL setup"; exit 1; }
set -e; J=$1; B=$2; CA=$3
[ "$(shasum -a 256 $B/src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] && [ "$(shasum -a 256 $B/be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] && [ "$(cat $B/ARM)" = cut7-headpass-x2+litepacks ] || { echo "base tree mismatch"; exit 1; }
if [ -f $J/STATUS ] && ! grep -q -E '^(DONE|FAIL)' $J/STATUS; then echo "job running"; exit 1; fi
rm -rf $J; mkdir -p $J; cp -cR $B $J/tree; rm -rf $J/tree/be/.cache; echo "$CA" > $J/tree/ARM
X
scp -q $REQ $M:$J/requests.jsonl && scp -q $PF $M:$J/candidate.patch && scp -q $ENVF $M:$J/env || exit 1; rm -f $ENVF
ssh -T -n $M "cd $J/tree && patch -p1 -s < ../candidate.patch && find . -name '*.orig' -delete && grep -c 'DECODE-GROUND' src/routing/answer.ts be/adapter-litedecline.ts" || { echo "FAIL patch"; exit 1; }
ssh -T -n $M "nohup bash $MK/lp-screens-mini_gen.sh $J > $J/nohup.log 2>&1 < /dev/null &" || exit 1
echo "$(date +%T) started $RUN arm $ARM on mini ($n items, job $J)"
[ "${NOWAIT:-0}" = 1 ] && exit 0
f=0; while :; do sleep 30; s=$(ssh -T -n -o ConnectTimeout=20 $M "tail -1 $J/STATUS" 2>/dev/null) || { f=$((f+1)); [ $f -ge 20 ] && { echo "FAIL unreachable"; exit 1; }; continue; }
  f=0; case $s in DONE) break;; FAIL*) echo "mini $s"; ssh -T -n $M "cat $J/STATUS; tail -20 $J/run.log"; scp -q $M:$J/STATUS $ST; exit 1;; esac; done
scp -q $M:$J/traces.jsonl $TR && scp -q $M:$J/STATUS $ST && scp -q $M:$J/run.log $H/runs/logs/$RUN.run.log || exit 1
ssh -T -n $M "rm -rf $J/tree" || true
[ "$(wc -l < $TR | tr -d ' ')" = "$n" ] || { echo "FAIL rows"; exit 1; }
echo "$(date +%T) DONE $RUN rows=$n"
