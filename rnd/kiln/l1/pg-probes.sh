#!/usr/bin/env bash
# Compass premise-guard L1 probes (compass/exp/premise-guard/CRITERIA.md): cut 2 tree UNPATCHED (be-0cfd4a77-cut2, 7931b9a8), runner be-ship 949eee03,
# detector ON, --places kit-vexact (as the vexact-cut2 runs these requests were cloned from), s42+s43, 40 items each. NO judging.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; PG=$B/rnd/research/compass/exp/premise-guard; OUT=$E/runs/kiln/pg-probes; MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
mkdir -p $OUT; export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-ship
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
got=$(echo 'cd <runner>/kiln/be-0cfd4a77-cut2 && echo "$(cut -c1-16 PATCH_SHA256) $(shasum -a 256 be-ship/adapter.ts | cut -c1-16)"' | <on the mini> bash -s)
[ "$got" = "7931b9a8905f230a 949eee0355032eb1" ] || { echo "TREE/RUNNER MISMATCH $got"; exit 1; }
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
for s in 42 43; do l=pg-probes-and4b-s$s
  env BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json \
    $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm cut2 --requests $PG/$l.requests.jsonl --out $OUT/$l.traces.jsonl --places $PLACES > $OUT/$l.runsh.out 2>&1
  echo "$l rc=$? $(tail -1 $OUT/$l.runsh.out | cut -c1-60)"
  <on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-cut2/be-ship/runs/\$(python3 -c \"import json;print(json.loads(open('$PG/$l.requests.jsonl').readline())['runId'])\" 2>/dev/null)" 2>/dev/null
done
echo 'p=$(lsof -tiTCP:8094 -sTCP:LISTEN); [ -n "$p" ] && kill $p' | <on the mini> bash -s; echo PG-PROBES-DONE
