#!/usr/bin/env bash
# SPECDEC step 1: re-run cut 5 (be-0cfd4a77-cut5lite, patch 3b7a0dfa...) on v0.1 EN s44 through the be-ship runner with
# --dump-prompts (rendered messages + nPredict + enableThinking per generate call, with itemId). --backend server (llama-server b11010,
# gate-less, as SPEEDPACK-L1/KVQ8 server runs); retrieval and prompts do not depend on the backend. Detector on :8094 (stopped by port after).
set -uo pipefail
B=<workspace>; E=$B/boar-eval
RUNNER_SHA=f5c5080635558897; ASHA=3b7a0dfa42bddee2
OUT=$B/rnd/research/coordinator/arms/specdec/data; mkdir -p $OUT
SRC=$E/runs/kiln/cut5lite-l1/arm-v01-s44.requests.jsonl
MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
SRV=<runner>/spikes/llama-b11010/build-cpu/bin/llama-server
export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-ship
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
got=$(echo 'cd <runner>/kiln/be-0cfd4a77-cut5lite && echo "$(cut -c1-16 PATCH_SHA256) $(shasum -a 256 be-ship/adapter.ts | cut -c1-16)"' | <on the mini> bash -s)
[ "$got" = "$ASHA $RUNNER_SHA" ] || { echo "TREE/RUNNER MISMATCH $got"; exit 1; }; echo "tree ok $got"
echo "free before: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
<on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && echo "detector up" || { echo "DETECTOR DOWN"; exit 1; }
DET=(BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json)
l=specdec-cut5-s44
python3 - $SRC $OUT/$l.requests.jsonl $l <<'PY'
import json, sys
rows = [json.loads(x) for x in open(sys.argv[1]) if x.strip()]
for r in rows: r["runId"] = sys.argv[3]
open(sys.argv[2], "w").write("".join(json.dumps(r) + "\n" for r in rows))
PY
T=boar/kiln/be-0cfd4a77-cut5lite
env "${DET[@]}" BOAR_KV_TYPE= $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm cut5lite --requests $OUT/$l.requests.jsonl --out $OUT/$l.traces.jsonl --places $PLACES --backend server --server-bin $SRV --dump-prompts be-ship/runs/$l/prompts.jsonl > $OUT/$l.runsh.out 2>&1
echo "rc=$? $(tail -1 $OUT/$l.runsh.out | cut -c1-100)"
scp -q MINI_HOST:$T/be-ship/runs/$l/prompts.jsonl $OUT/$l.prompts.jsonl && echo "prompts fetched $(wc -l < $OUT/$l.prompts.jsonl)"
<on the mini> "rm -rf ~/$T/be-ship/runs/$l"
echo 'p=$(lsof -tiTCP:8094 -sTCP:LISTEN); [ -n "$p" ] && kill $p; echo detector stopped' | <on the mini> bash -s
echo "free after: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
