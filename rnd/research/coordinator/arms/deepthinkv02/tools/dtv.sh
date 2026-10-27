#!/bin/bash
# DEEPTHINK-V02 MacBook driver (criterion 265ea559…) = deepthink(2)/tools/dt(2).sh parametrised by tree, v0.2 = noplaces (DEEPVPARA Stage 2 / Run A).
# Reuses the mini copies <runner>/kiln/deepthink-remote-run.sh (B=1024, ctx 4096) and deepthink2-remote-run.sh (B=3072, BOAR_SERVER_CTX=8192) unchanged.
# TREE env = deepthink | deepthink2 (required for launch/status/fetch/place). Prints counts/ids/timings only.
#   TREE=<t> dtv.sh mkreq <src> <out> <runId>   config.arm = TREE label (the adapter refuses a mismatch); arm D settings {quickFirst, alwaysComplete, deepModelId}; items untouched
#   dtv.sh place <requests> <runId>                         scp requests into BOTH trees' be-repo/runs/<runId>/ (no launch)
#   dtv.sh launch <runId>                                   start <TREE>-remote-run.sh <runId> D noplaces under nohup
#   dtv.sh status <runId> | fetch <runId> <outTraces> <requests> | think <traces> [ids] [out]   (as dt2.sh; HIT env = budget)
set -u
H=MINI_HOST; E=<workspace>/boar-eval; DT2=<workspace>/rnd/research/coordinator/arms/deepthink2/tools/dt2.sh
TREE=${TREE:-}; T=boar/kiln/be-0cfd4a77-$TREE
cmd=$1; shift
case $cmd in
mkreq) src=$1 out=$2 run=$3
  st='{"quickFirst":true,"alwaysComplete":true,"deepModelId":"qwen3.6-35b-a3b-ud-q2kxl"}'
  jq -c --arg r "$run" --arg a "${TREE:?TREE unset}" --argjson s "$st" '.runId=$r | .config.settings=$s | .config.arm=$a' "$src" > "$out"
  echo "requests $(wc -l < "$out") runId $run settings $(head -1 "$out" | jq -c .config.settings) seed $(head -1 "$out" | jq .seed) sha $(shasum -a 256 "$out" | cut -c1-12) itemsSha $(jq -c .item "$out" | shasum -a 256 | cut -c1-12) srcItemsSha $(jq -c .item "$src" | shasum -a 256 | cut -c1-12)";;
place) req=$1 run=$2
  for t in deepthink deepthink2; do ssh -T -n $H "mkdir -p <runner>/kiln/be-0cfd4a77-$t/be-repo/runs/$run" && scp -q "$req" "$H:boar/kiln/be-0cfd4a77-$t/be-repo/runs/$run/requests.jsonl" || exit 1
    echo "$t: $(ssh -T -n $H "shasum -a 256 <runner>/kiln/be-0cfd4a77-$t/be-repo/runs/$run/requests.jsonl" | cut -c1-12)"; done;;
launch) run=$1; [ -n "$TREE" ] || { echo "TREE unset"; exit 1; }
  ssh -T -n $H "test -e ~/$T/be-repo/runs/$run/STATUS" && { echo "REFUSE: $run already has a STATUS on $TREE (a run started or finished); pick a new run id"; exit 2; }
  ssh -T -n -f $H "nohup bash -l <runner>/kiln/$TREE-remote-run.sh $run D noplaces > <runner>/kiln/deepthinkv02-$run.nohup.log 2>&1 < /dev/null &"
  echo "launched $run on $TREE (D, noplaces) at $(date +%H:%M)";;
status|fetch) [ -n "$TREE" ] || { echo "TREE unset"; exit 1; }
  sed "s#^H=MINI_HOST; T=boar/kiln/be-0cfd4a77-deepthink2;#H=MINI_HOST; T=$T;#" $DT2 > /tmp/dtv-inner.sh; bash /tmp/dtv-inner.sh $cmd "$@";;
think) bash $DT2 think "$@";;
esac
