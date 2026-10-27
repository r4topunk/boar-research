#!/usr/bin/env bash
# CUT 2 rerun (coordinator GO; places (b) only; anchors reused from runs/kiln/vexact/anchors): tree be-0cfd4a77-cut2 (shipcut2-norv2 7931b9a8),
# detector env as for b6-on-health13 (Forge's device-detector question pending). (Template below.)
# Compass's V-exact the post author slice (rnd/research/compass/exp/bounty-eval/bench-vslice/RUN.md). Ship stack = tree be-0cfd4a77-cut2
# (b6-on-health13 6f841ab6…), runner be-ship 949eee03, detector ON (v3b, THR unset). Profiles: and4b (E3 Android 12 GB 4B config,
# headline) + ios15 (p2-iphone13). Seeds 42/43. PRIMARY (b): all 11 items with --places kit-vexact (gazetteer + Berlin/Lisbon/Tokyo
# tiles). SIDE ROW (a): the 6 venue items on the bare config (no places). Then anchors (vx-001/002 new; 3 old from v0.1 anchors),
# judge (bench-vslice; venue items not judged), venue scorer (venues.mjs) and claim_report.py -> VSLICE-REPORT.md.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; X=$B/rnd/research/compass/exp/bounty-eval; VS=$X/bench-vslice; OUT=$E/runs/kiln/vexact-cut2
MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
mkdir -p $OUT/anchors; export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-ship
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
got=$(echo 'cd <runner>/kiln/be-0cfd4a77-cut2 && echo "$(cut -c1-16 PATCH_SHA256) $(shasum -a 256 be-ship/adapter.ts | cut -c1-16)"' | <on the mini> bash -s)
[ "$got" = "7931b9a8905f230a 949eee0355032eb1" ] || { echo "TREE/RUNNER MISMATCH $got"; exit 1; }; echo "tree ok $got"
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
<on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && echo "detector up" || { echo "DETECTOR DOWN"; exit 1; }
DET=(BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json)
python3 -c "import json; [print(l.strip()) for l in open('$VS/questions.jsonl') if json.loads(l)['grading']['type'] == 'venue-list']" > $OUT/venue6.questions.jsonl
run() { # profile seed mode(b|a)
  local prof=$1 seed=$2 mode=$3 cfg q label=vslice-$1-s$2${3/b/}
  [ $mode = a ] && label=vslice-$prof-s$seed-bare
  [ $prof = and4b ] && cfg=$B/blind/bench-v02/runs-e3/e3-main-s42.config.json || cfg=$E/adapters/desktop-node/configs/p2-iphone13-0cfd4a77.json
  [ $mode = b ] && q=$VS/questions.jsonl || q=$OUT/venue6.questions.jsonl
  python3 -c "import json; c=json.load(open('$cfg')); c['arm']='cut2'; c['seed']=$seed; json.dump(c, open('$OUT/$label.config.json','w'))"
  pnpm -s -C $E/packages/protocol exec tsx src/makeRequests.ts --questions $q --config $OUT/$label.config.json --run-id $label > $OUT/$label.requests.jsonl 2>/dev/null
  local extra=(); [ $mode = b ] && extra=(--places $PLACES)
  env "${DET[@]}" $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm cut2 --requests $OUT/$label.requests.jsonl --out $OUT/$label.traces.jsonl ${extra[@]+"${extra[@]}"} > $OUT/$label.runsh.out 2>&1
  echo "$label rc=$? $(date +%H:%M) $(tail -1 $OUT/$label.runsh.out | cut -c1-90)"
  <on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-cut2/be-ship/runs/$label"
}
for seed in 42 43; do for prof in and4b ios15; do run $prof $seed b; done; done
echo 'p=$(lsof -tiTCP:8094 -sTCP:LISTEN); [ -n "$p" ] && kill $p; echo detector stopped' | <on the mini> bash -s
# judge the primary runs (judge.mjs skips venue-list items)
for seed in 42 43; do for prof in and4b ios15; do l=vslice-$prof-s$seed
  (cd $E && node harness/judge.mjs --traces $OUT/$l.traces.jsonl --out $OUT/$l.judgments.jsonl --bench $VS --system $l > $OUT/$l.judge.log 2>&1; echo "judge $l rc=$?") &
done; done
wait; echo VEXACT-CUT2-JUDGED
