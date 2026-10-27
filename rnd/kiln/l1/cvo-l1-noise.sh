#!/usr/bin/env bash
# CVO L1 side check, same time window for both arms: re-run lan-exp-007 (the one non-routed item whose text differs from cut3-confirm, no cvo code)
# and the 4 routed lan-cmp items, seed-44 requests, twice on the cut 3 tree and twice on the CVO tree (interleaved). Answers whether the exp-007 diff is
# generation noise and gives an added-time estimate free of the cut3-confirm vs cvo-l1 load drift. Detector: reuse a running one, start one only if absent, never stop it.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; OUT=$E/runs/kiln/cvo-l1/noise; mkdir -p $OUT; export HEAVY_CLASS=short BOAR_EVAL_RUNNER_DIR=be-ship
MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
DET=(BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json)
IDS=lan-exp-007,lan-cmp-001,lan-cmp-002,lan-cmp-004,lan-cmp-005
for n in 1 2; do for arm in cut3 cvo; do
  python3 - $E/runs/kiln/cvo-l1/cvo-v01-s44.requests.jsonl $OUT/$arm-$n.requests.jsonl $arm-noise-$n $arm <<'PY'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
for r in rows: r["runId"] = sys.argv[3]; r["config"]["arm"] = sys.argv[4]
open(sys.argv[2], "w").write("".join(json.dumps(r) + "\n" for r in rows))
PY
  env "${DET[@]}" $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm $arm --requests $OUT/$arm-$n.requests.jsonl --ids $IDS --out $OUT/$arm-$n.traces.jsonl --places $PLACES > $OUT/$arm-$n.out 2>&1
  echo "$arm-$n rc=$? $(tail -1 $OUT/$arm-$n.out | cut -c1-60)"
done; done
echo NOISE-DONE
