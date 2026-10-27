#!/usr/bin/env bash
# CVO L1 control: cut 3 re-run TODAY (tree be-0cfd4a77-cut3, same requests, seeds 44/45, same config) to separate CVO's effect from drift since cut3-confirm (Oct 4).
# Detector: reuse a running one, start only if absent, never stop it. Generation only.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; OUT=$E/runs/kiln/cvo-l1/ctl; D3=$E/runs/kiln/cut3-confirm; mkdir -p $OUT; export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-ship
MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
got=$(echo 'cd <runner>/kiln/be-0cfd4a77-cut3 && echo "$(cut -c1-16 PATCH_SHA256) $(shasum -a 256 be-ship/adapter.ts | cut -c1-16)"' | <on the mini> bash -s)
[ "$got" = "a67c70dbd194da82 949eee0355032eb1" ] || { echo "TREE/RUNNER MISMATCH $got"; exit 1; }; echo "tree ok $got"
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
DET=(BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json)
for s in 44 45; do
  python3 - $D3/cut3-v01-s$s.requests.jsonl $OUT/ctl-v01-s$s.requests.jsonl ctl-v01-s$s <<'PY'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
for r in rows: r["runId"] = sys.argv[3]
open(sys.argv[2], "w").write("".join(json.dumps(r) + "\n" for r in rows))
PY
  env "${DET[@]}" $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm cut3 --requests $OUT/ctl-v01-s$s.requests.jsonl --out $OUT/ctl-v01-s$s.traces.jsonl --places $PLACES > $OUT/ctl-v01-s$s.runsh.out 2>&1
  echo "ctl s$s rc=$? $(date +%H:%M)"
  <on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-cut3/be-ship/runs/ctl-v01-s$s"
done
echo CTL-DONE
