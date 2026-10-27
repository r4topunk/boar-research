#!/usr/bin/env bash
# CUT 4 desktop v0.1 EN s44 + s45 generation (KVFIX gate 2 + INSTANT-FRAG L1 input), same config as cvh-l1.sh / cut3-confirm.
# Run by the coordinator on the MacBook, generation on the Mac mini (heavy lock). NOT run by the engine engineer.
# usage: cut4-l1.sh setup   # one-off: builds <runner>/kiln/be-0cfd4a77-cut4 from the cut4-stack patch and copies be-ship from the cut3 tree
#        cut4-l1.sh run     # generates s44, s45; then compares with the stored cut 3 traces
# KVFIX NOTE: the desktop adapter drives llama-server through makeServerEngine, NOT src/inference/LlamaEngine.ts (the shim no-ops
# saveSession), so gate (2) cannot exercise KVFIX; what it shows is that the stack changes nothing but the INSTANT-FRAG items.
# Gate (2) pass = answers byte-identical to cut 3 except <= 1 item per seed run-to-run noise (lan-exp-007 precedent) + the L0-predicted
# INSTANT-FRAG items; the comparison below prints both.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; A=$B/rnd/research/coordinator/arms
PATCH=$A/cut4/cut4-stack.vs-0cfd4a77.patch
PSHA=1fd5d9a57d2d590b   # first 16 hex of sha256(cut4-stack patch)
RUNNER_SHA=949eee0355032eb1             # be-ship/adapter.ts, as in cvh-l1.sh
OUT=$E/runs/kiln/cut4-l1; D3=$E/runs/kiln/cut3-confirm
MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
if [ "${1:-}" = setup ]; then
  [ "$(shasum -a 256 $PATCH | cut -c1-16)" = "$PSHA" ] || { echo "PATCH MISMATCH"; exit 1; }
  BOAR_EVAL_RUNNER_DIR=be-ship $E/adapters/desktop-node/setup.sh 0cfd4a77 --patch $PATCH --arm cut4 || exit 1
  <on the mini> "rsync -a --exclude runs <runner>/kiln/be-0cfd4a77-cut3/be-ship/ <runner>/kiln/be-0cfd4a77-cut4/be-ship/ && mkdir -p <runner>/kiln/be-0cfd4a77-cut4/be-ship/runs"
  exit 0
fi
mkdir -p $OUT; export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-ship
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
got=$(echo 'cd <runner>/kiln/be-0cfd4a77-cut4 && echo "$(cut -c1-16 PATCH_SHA256) $(shasum -a 256 be-ship/adapter.ts | cut -c1-16)"' | <on the mini> bash -s)
[ "$got" = "$PSHA $RUNNER_SHA" ] || { echo "TREE/RUNNER MISMATCH $got"; exit 1; }; echo "tree ok $got"
echo "free before: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
<on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && echo "detector up" || { echo "DETECTOR DOWN"; exit 1; }
DET=(BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json)
for s in 44 45; do python3 - $D3/cut3-v01-s$s.requests.jsonl $OUT/cut4-v01-s$s.requests.jsonl cut4-v01-s$s <<'PY'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
for r in rows: r["runId"] = sys.argv[3]; r["config"]["arm"] = "cut4"
open(sys.argv[2], "w").write("".join(json.dumps(r) + "\n" for r in rows))
PY
done
for l in cut4-v01-s44 cut4-v01-s45; do
  env "${DET[@]}" $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm cut4 --requests $OUT/$l.requests.jsonl --out $OUT/$l.traces.jsonl --places $PLACES > $OUT/$l.runsh.out 2>&1
  echo "$l rc=$? $(date +%H:%M) $(tail -1 $OUT/$l.runsh.out | cut -c1-90)"
  <on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-cut4/be-ship/runs/$l"
done
echo 'p=$(lsof -tiTCP:8094 -sTCP:LISTEN); [ -n "$p" ] && kill $p; echo detector stopped' | <on the mini> bash -s
echo "free after: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
# gate (2): answers vs cut 3 (same seed): byte-identical text, tier and reason codes
for s in 44 45; do python3 $A/cut4/tools/cmp.py $D3/cut3-v01-s$s.traces.jsonl $OUT/cut4-v01-s$s.traces.jsonl $OUT/cut4-v01-s$s.requests.jsonl | tail -12; done
echo CUT4-L1-GEN-DONE
