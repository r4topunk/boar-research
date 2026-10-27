#!/bin/bash
# GATE17 step 1 (0 judge calls): regenerate a mini LP-SCREENS control with --dump-prompts so the exact context the 1.7B saw is on disk.
# Usage: gen_dump.sh <control run, e.g. lpctl-K0-main-s42>
# Requests = the control's own request file (lp-screens/control/runs/req/<run>.requests.jsonl) with runId replaced; unpatched base tree
# be-0cfd4a77-cut7-litepacks (sha-checked); mini job via tools/mini_gen_dump.sh (lp-screens mini_gen.sh + --dump-prompts; same slot lock gen1/gen2).
# Labels stay valid only for byte-identical answer.text (checked later by tools/build_items.py).
set -u
CTL=$1
A=<workspace>/rnd/research/coordinator/arms; H=$A/lp-screens; D=$A/gate17
M=MINI_HOST; MK=<runner>/kiln; BASE=$MK/be-0cfd4a77-cut7-litepacks; RUN=gate17dump-${CTL#lpctl-}; J=$MK/lp-screens/jobs/$RUN
REQ=$D/runs/req/$RUN.requests.jsonl
python3 -I -c "
import json,sys
src,run,out=sys.argv[1:4]
with open(out,'w') as f:
    for l in open(src):
        r=json.loads(l); r['runId']=run; f.write(json.dumps(r,ensure_ascii=False)+'\n')
" $H/control/runs/req/$CTL.requests.jsonl $RUN $REQ || exit 1
INSHA=$( { cat $REQ; echo kind=dump-prompts; } | shasum -a 256 | cut -c1-16)
scp -q $D/tools/mini_gen_dump.sh $M:$MK/gate17-mini_gen_dump.sh || exit 1
ssh $M bash -s -- "$J" "$BASE" "$INSHA" <<'EOF' || exit 1
set -e; J=$1; B=$2; IS=$3
[ "$(shasum -a 256 $B/src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] && [ "$(shasum -a 256 $B/be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] && [ "$(cat $B/ARM)" = cut7-headpass-x2+litepacks ] || { echo "base tree mismatch"; exit 1; }
if [ -f $J/STATUS ] && ! grep -q -E '^(DONE|FAIL)' $J/STATUS; then echo "job $J still running"; exit 1; fi
rm -rf $J; mkdir -p $J; cp -cR $B $J/tree; rm -rf $J/tree/be/.cache; echo $IS > $J/INPUTS
EOF
scp -q $REQ $M:$J/requests.jsonl || exit 1
ssh -T -n $M "nohup bash $MK/gate17-mini_gen_dump.sh $J > $J/nohup.log 2>&1 < /dev/null &" || exit 1
echo "$(date +%T) started $RUN inputs $INSHA"
while :; do sleep 30; s=$(ssh -T -n -o ConnectTimeout=20 $M "tail -1 $J/STATUS" 2>/dev/null) || continue
  case $s in DONE) break;; FAIL*) echo "mini $s"; ssh -T -n $M "cat $J/STATUS; tail -20 $J/run.log"; exit 1;; esac; done
scp -q $M:$J/traces.jsonl $D/traces/$RUN.traces.jsonl && scp -q $M:$J/prompts.jsonl $D/traces/$RUN.prompts.jsonl && scp -q $M:$J/STATUS $D/runs/logs/$RUN.status.mini || exit 1
ssh -T -n $M "rm -rf $J/tree"
{ echo "inputs $INSHA kind=dump-prompts host=mini job=$J"; cat $D/runs/logs/$RUN.status.mini; } > $D/runs/logs/$RUN.status
echo "$(date +%T) DONE rows $(wc -l < $D/traces/$RUN.traces.jsonl) prompt rows $(wc -l < $D/traces/$RUN.prompts.jsonl)"
