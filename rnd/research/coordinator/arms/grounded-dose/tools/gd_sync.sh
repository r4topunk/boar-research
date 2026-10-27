#!/bin/bash
# MacBook side: put trees + requests + env on the mini under <runner>/kiln/gd, start gd_mini.sh detached.
set -u
B=<workspace>; G=$B/rnd/research/coordinator/arms/grounded-dose; M=MINI_HOST; MK=<runner>/kiln; GD=$MK/gd; BASE=$MK/be-0cfd4a77-cut7-litepacks
ssh -T -n $M "bash -c 'mkdir -p $GD/jobs/B900 $GD/jobs/Bk4c40 $GD/trees'"
for T in rs-X2B rs-RETBENCH; do
  rsync -a --delete --exclude /node_modules --exclude /be/node_modules --exclude /be/.cache $B/kiln-local/$T/ $M:$GD/trees/$T/ || exit 1
  ssh -T -n $M "bash -c 'cd $GD/trees/$T && rm -rf be/node_modules node_modules && cp -cR $BASE/be/node_modules be/node_modules && ln -sfn $BASE/be/vendor-protocol be/node_modules/@boar-eval/protocol && ln -s be/node_modules node_modules && test -f be/node_modules/@boar-eval/protocol/src/index.ts'" || exit 1
  a=$(cd $B/kiln-local/$T && find src be -path be/node_modules -prune -o -path be/.cache -prune -o -type f -print | LC_ALL=C sort | xargs shasum -a 256 | shasum -a 256 | cut -c1-16)
  b=$(ssh -T -n $M "bash -c 'cd $GD/trees/$T && find src be -path be/node_modules -prune -o -path be/.cache -prune -o -type f -print | LC_ALL=C sort | xargs shasum -a 256 | shasum -a 256 | cut -c1-16'")
  [ "$a" = "$b" ] && echo "tree $T identical ($a)" || { echo "TREE MISMATCH $T"; exit 1; }
done
ARMK=$(head -1 $G/req/B900.requests.jsonl | python3 -I -c "import json,sys;print(json.loads(sys.stdin.readline())['config']['arm'])")
KENV="BOAR_EVAL_PACK_DIRS=$MK/compose/packs-k13\nRS_MERGE=gidf\nRS_SE_LEAD=0.78\nRS_SE_MAXDF=0.25\nRS_KEEP_NOPROPER=1\n"
for A in B900:rs-X2B:RS_X2B_BUDGET=900 Bk4c40:rs-RETBENCH:RS_RB_K=4,RS_RB_COMPRESS=0.4; do
  N=${A%%:*}; R=${A#*:}; T=${R%%:*}; E=${R#*:}
  ssh -T -n $M "bash -c 'rm -rf $GD/jobs/$N/tree $GD/jobs/$N/traces.jsonl $GD/jobs/$N/STATUS; cp -cR $GD/trees/$T $GD/jobs/$N/tree; rm -rf $GD/jobs/$N/tree/be/.cache; echo $ARMK > $GD/jobs/$N/tree/ARM'"
  scp -q $G/req/$N.requests.jsonl $M:$GD/jobs/$N/requests.jsonl
  { printf "$KENV"; echo "$E" | tr ',' '\n'; } | ssh $M "cat > $GD/jobs/$N/env"
done
scp -q $G/tools/gd_mini.sh $M:$GD/gd_mini.sh
ssh -T -n $M "bash -c 'cat $GD/jobs/B900/env; echo --; cat $GD/jobs/Bk4c40/env; cat $GD/jobs/B900/tree/ARM; wc -l $GD/jobs/*/requests.jsonl; df -g ~ | tail -1'"
ssh -T -n $M "bash -c 'rm -f $GD/RUN.log; nohup bash $GD/gd_mini.sh $GD > $GD/nohup.log 2>&1 < /dev/null &'"
echo started
