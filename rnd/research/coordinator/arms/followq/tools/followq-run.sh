#!/usr/bin/env bash
# FOLLOWQ retrieval-only run: 192 dev chat messages x Q0/Q1/Q2 (576 requests), cut 5 tree be-0cfd4a77-cut5lite on the Mac mini,
# committed adapter (be-repo) patched by patch_adapter.py into a side runner dir be-fq (be-repo untouched), same kit and embedder as CHATGATE,
# learned detector v3b on :8094 as in CHATGATE (affects the health branch), heavy lock, no generation, no judge.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; OUT=$E/runs/kiln/followq; T=$B/rnd/research/coordinator/arms/followq/tools
MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
mkdir -p $OUT; export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-fq
python3 $T/mkreq.py $OUT || exit 1
python3 $T/patch_adapter.py $E/adapters/desktop-node/runner/adapter.ts $OUT/adapter.fq.ts || exit 1
TREE='<runner>/kiln/be-0cfd4a77-cut5lite'
<on the mini> "rm -rf $TREE/be-fq && mkdir -p $TREE/be-fq && cd $TREE/be-repo && cp -R app-shims gate.ts merge-shards.mjs parallel.sh protocol.ts server.ts trace.ts vendor ../be-fq/ && ln -s <runner>/eval-runner/eval/node_modules ../be-fq/node_modules"
scp -q $OUT/adapter.fq.ts MINI_HOST:boar/kiln/be-0cfd4a77-cut5lite/be-fq/adapter.ts
<on the mini> "cd $TREE && cmp be-repo/trace.ts be-fq/trace.ts && diff <(sed 's/x/x/' be-repo/adapter.ts) be-fq/adapter.ts | head -8"
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
<on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && echo "detector up" || { echo "DETECTOR DOWN"; exit 1; }
echo "free before: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
l=followq-s44
BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json \
  $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm cut5lite --requests $OUT/$l.requests.jsonl --out $OUT/$l.traces.jsonl --places $PLACES > $OUT/$l.runsh.out 2>&1
echo "$l rc=$? $(date +%H:%M) $(tail -1 $OUT/$l.runsh.out | cut -c1-120)"
<on the mini> "rm -rf $TREE/be-fq/runs/$l"
echo 'p=$(lsof -tiTCP:8094 -sTCP:LISTEN); [ -n "$p" ] && kill $p; echo detector stopped' | <on the mini> bash -s
echo "free after: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
echo FOLLOWQ-RUN-DONE
