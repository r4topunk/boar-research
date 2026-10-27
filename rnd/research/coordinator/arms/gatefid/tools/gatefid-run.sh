#!/usr/bin/env bash
# GATEFID step 2 (deviation, see GATEFID.md): the be-ship runner on the mini already has the route gate ON by default
# (BOAR_ROUTE_GATE=0 = off), so every CUT5 run was gate-ON. The missing arm is the true gate-less control:
# cut 4 final tree (be-0cfd4a77-instsubj4), BOAR_ROUTE_GATE=0, v0.1 EN s44, same config as cut5lite-l1.
# Gate-ON arms = cut5lite-l1/ctl-v01-s44 (cut 4) and cut5lite-l1/arm-v01-s44 (cut 5, CUT5-LITE patch 3b7a0dfa).
set -uo pipefail
B=<workspace>; E=$B/boar-eval; OUT=$E/runs/kiln/gatefid; L=$E/runs/kiln/cut5lite-l1
MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
mkdir -p $OUT; export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-ship
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
got=$(echo 'cd <runner>/kiln/be-0cfd4a77-instsubj4 && echo "$(cut -c1-16 PATCH_SHA256) $(shasum -a 256 be-ship/adapter.ts | cut -c1-16)"' | <on the mini> bash -s)
[ "$got" = "d51e844c6522cb18 f5c5080635558897" ] || { echo "TREE MISMATCH $got"; exit 1; }
echo "free before: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
<on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && echo "detector up" || { echo "DETECTOR DOWN"; exit 1; }
l=nogate-v01-s44
python3 - $L/ctl-v01-s44.requests.jsonl $OUT/$l.requests.jsonl $l <<'PY'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
for r in rows: r["runId"] = sys.argv[3]; r["config"]["arm"] = "instsubj4"
open(sys.argv[2], "w").write("".join(json.dumps(r) + "\n" for r in rows))
PY
BOAR_ROUTE_GATE=0 BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json \
  $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm instsubj4 --requests $OUT/$l.requests.jsonl --out $OUT/$l.traces.jsonl --places $PLACES > $OUT/$l.runsh.out 2>&1
echo "$l rc=$? $(date +%H:%M) $(tail -1 $OUT/$l.runsh.out | cut -c1-100)"
<on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-instsubj4/be-ship/runs/$l"
echo 'p=$(lsof -tiTCP:8094 -sTCP:LISTEN); [ -n "$p" ] && kill $p; echo detector stopped' | <on the mini> bash -s
echo GATEFID-GEN-DONE
