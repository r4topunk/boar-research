#!/bin/bash
# VALIDATION 2026-10-24: put everything the mini queue needs on the mini (MacBook side, 0 LLM). Run at GO time, after rc-env.sh / rs-RC are final and V0 passed.
# usage: sync_mini.sh check | sync | start | fetch
#   check = dry plan: sizes to copy, mini disk now and after, which RC packs the mini already has (by sha), nothing written
#   sync  = mk_jobs.py (RC kit shas from rc-env.sh), rsync trees (no node_modules: the mini base tree's be/node_modules is cloned in), packs, w78 sidecars,
#           env files (rc.env from rc-env.sh with mini paths; rb.env = SEFIX-124 + RS_RB_K=4 RS_RB_COMPRESS=0.4 on compose/packs-k13), night/ (jobs + tools); then verify
#   start = sync verified -> mini_queue.sh start (detached on the mini; the MacBook may sleep afterwards)
#   fetch = copy run/<job>/out (+ STATUS) back to night/fetched/<job>/ (gitignored) for the aggregators
# Mini layout: <runner>/kiln/val1024/{trees/rs-RC,trees/rs-RETBENCH,packs-rc/,w78/sidecars,w78/sidecars-c,env/,night/,run/<job>/,QUEUE.log}
set -u
B=<workspace>; VD=$B/rnd/research/coordinator/arms/validation-1024; N=$VD/night; M=MINI_HOST
MR=<runner>/kiln/val1024; MK=<runner>/kiln; BASE=$MK/be-0cfd4a77-cut7-litepacks; K13=$MK/compose/packs-k13; V3M=<runner>/shared-data/packs/v3proto
. $VD/tools/rc-env.sh
W78=$RC_ARMS/coverage-map/w78
ACT=${1:-check}
mb() { du -sk "$@" 2>/dev/null | awk '{s+=$1} END {printf "%d", s/1024}'; }
# packs the mini lacks = RC pack files whose sha is not one of compose/packs-k13's
MSHA=$(ssh -T -n $M "bash -c 'cd $K13 && shasum -a 256 *.sqlite'")
NEED=""; for p in ${RC_PACKS//,/ }; do s=$(python3 -I -c 'import json,sys;print(json.load(open(sys.argv[1]))[sys.argv[2]]["sha256"])' $N/rc-kit.json $(basename $p .sqlite) 2>/dev/null || shasum -a 256 $p | cut -d' ' -f1)
  echo "$MSHA" | grep -q "^$s " || NEED="$NEED $p"; done
if [ "$ACT" = check ]; then
  echo "RC packs missing on the mini:$NEED"; echo "copy MB: packs $(mb $NEED) + sidecars $(mb $W78/sidecars $W78/sidecars-c) + trees (src only) $(( $(mb $RC_TREE) + $(mb $B/kiln-local/rs-RETBENCH) ))"
  ssh -T -n $M "bash -c 'df -g ~ | tail -1; du -sk $MR 2>/dev/null'"; exit 0; fi
if [ "$ACT" = fetch ]; then
  for j in $(ssh -T -n $M "ls $MR/run"); do mkdir -p $N/fetched/$j; rsync -a --exclude tree $M:$MR/run/$j/ $N/fetched/$j/; echo "$j: $(tail -1 $N/fetched/$j/STATUS)"; done; exit 0; fi
if [ "$ACT" = prestage ]; then  # static inputs only (packs-rc + w78 sidecars), safe before GO; sync repeats it idempotently
  ssh -T -n $M "bash -c 'mkdir -p $MR/packs-rc $MR/w78'"
  for p in $NEED; do rsync -a $p $M:$MR/packs-rc/$(basename $p) || exit 1; done
  ssh -T -n $M "bash -c 'cd $MR/packs-rc && for f in $K13/*.sqlite $V3M/qa-bitcoin-se.sqlite $V3M/qa-ethereum-se.sqlite; do [ -e \$(basename \$f) ] || cp -c \$f .; done; shasum -a 256 *.sqlite; df -g ~ | tail -1'" || exit 1
  rsync -a --delete $W78/sidecars $W78/sidecars-c $M:$MR/w78/ || exit 1; exit 0; fi
if [ "$ACT" = sync ] || [ "$ACT" = start ]; then
  python3 -I $N/tools/mk_jobs.py || exit 1
  ssh -T -n $M "bash -c 'mkdir -p $MR/trees $MR/packs-rc $MR/w78 $MR/env $MR/run'"
  for T in rs-RC rs-RETBENCH rs-RC-STICKY; do
    rsync -a --delete --exclude /node_modules --exclude /be/node_modules --exclude /be/.cache $B/kiln-local/$T/ $M:$MR/trees/$T/ || exit 1
    ssh -T -n $M "bash -c 'cd $MR/trees/$T && rm -rf be/node_modules node_modules && cp -cR $BASE/be/node_modules be/node_modules && ln -sfn $BASE/be/vendor-protocol be/node_modules/@boar-eval/protocol && ln -s be/node_modules node_modules && test -f be/node_modules/@boar-eval/protocol/src/index.ts'" || exit 1
  done
  # packs-rc: K13 files the mini has (APFS clone, no space), the RC-only files copied, plus qa-bitcoin-se / qa-ethereum-se (PACKPROOF ON groups)
  # idempotent: RC-only files are rsynced first (skipped when already identical), K13 / v3proto clones only for names not present
  for p in $NEED; do rsync -a $p $M:$MR/packs-rc/$(basename $p) || exit 1; done
  ssh -T -n $M "bash -c 'cd $MR/packs-rc && for f in $K13/*.sqlite $V3M/qa-bitcoin-se.sqlite $V3M/qa-ethereum-se.sqlite; do [ -e \$(basename \$f) ] || cp -c \$f .; done; ls | wc -l'" || exit 1
  rsync -a --delete $W78/sidecars $W78/sidecars-c $M:$MR/w78/ || exit 1
  # rc.env: the RS_* exports of rc-env.sh, MacBook w78 dirs -> mini; pack dir -> packs-rc
  env | grep '^RS_' | sort | sed "s#$W78#$MR/w78#g" > $N/rc.env.mini; echo "BOAR_EVAL_PACK_DIRS=$MR/packs-rc" >> $N/rc.env.mini
  grep -q /Script/ $N/rc.env.mini && { echo "rc.env still has a MacBook path"; exit 1; }
  printf 'BOAR_EVAL_PACK_DIRS=%s\nRS_MERGE=gidf\nRS_SE_LEAD=0.78\nRS_SE_MAXDF=0.25\nRS_KEEP_NOPROPER=1\nRS_RB_K=4\nRS_RB_COMPRESS=0.4\n' $K13 > $N/rb.env.mini
  scp -q $N/rc.env.mini $M:$MR/env/rc.env && scp -q $N/rb.env.mini $M:$MR/env/rb.env || exit 1
  rsync -a --delete --exclude fetched --exclude '*.mini' $N/ $M:$MR/night/ || exit 1
  # verify: tree src identical (sha manifest), kit shas resolvable, binaries, detector, disk
  for T in rs-RC rs-RETBENCH rs-RC-STICKY; do
    a=$(cd $B/kiln-local/$T && find src be -path be/node_modules -prune -o -path be/.cache -prune -o -type f -print | LC_ALL=C sort | xargs shasum -a 256 | shasum -a 256 | cut -c1-16)
    b=$(ssh -T -n $M "bash -c 'cd $MR/trees/$T && find src be -path be/node_modules -prune -o -path be/.cache -prune -o -type f -print | LC_ALL=C sort | xargs shasum -a 256 | shasum -a 256 | cut -c1-16'")
    [ "$a" = "$b" ] && echo "tree $T identical ($a)" || { echo "TREE MISMATCH $T $a vs $b"; exit 1; }
  done
  python3 -I - $N/jobs.json > $N/kitcheck.mini <<'E'
import json, sys
J = json.load(open(sys.argv[1])); need = {}
for j in J["jobs"]:
    import glob, os
    for f in glob.glob(os.path.dirname(sys.argv[1]) + f"/jobs/{j['name']}/req/*.jsonl") + glob.glob(os.path.dirname(sys.argv[1]) + f"/jobs/{j['name']}/turn2.template.jsonl"):
        for l in open(f):
            for k in json.loads(l)["config"]["kit"]: need[(j["packdir"], k["id"], k["sha256"])] = 1
for d, i, s in sorted(need): print(d, i, s)
E
  scp -q $N/kitcheck.mini $M:$MR/kitcheck.txt
  ssh -T -n $M "bash -c 'bad=0; while read d i s; do [ \$d = packs-k13 ] && f=$K13/\$i.sqlite || f=$MR/\$d/\$i.sqlite; [ \"\$(shasum -a 256 \$f | cut -d\" \" -f1)\" = \$s ] || { echo KIT MISMATCH \$d \$i; bad=1; }; done < $MR/kitcheck.txt; echo kit-check bad=\$bad; ls <runner>/spikes/llama-b11010/build-cpu/bin/llama-server <runner>/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf > /dev/null && echo bins-ok; curl -sf http://127.0.0.1:8094/health > /dev/null && echo detector-ok; df -g ~ | tail -1'"
  [ "$ACT" = start ] && ssh -T -n $M "bash $MR/night/tools/mini_queue.sh start"
fi
