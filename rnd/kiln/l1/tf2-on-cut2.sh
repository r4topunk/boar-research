#!/usr/bin/env bash
# tf2-on-cut2 (criterion rnd/research/coordinator/tf2-criterion.md, sha256 2e0dec75…). Generation only; judging is a separate step.
# Tree be-0cfd4a77-tf2 (patch rnd/research/coordinator/tf2-on-cut2.vs-0cfd4a77.patch bd39546d…), runner be-ship 949eee03,
# detector v3b ON (THR unset), --places kit-vexact. Runs inside <runner>/bin/run-heavy via run.sh.
#  G2: v0.1 EN 60, s44 = overnight ov-cut2-v01-s44 requests re-keyed (runId, arm) -> diff vs ov-cut2-v01-s44 traces.
#  G3: V-exact 11 items, and4b (Android 12 GB 4B), s42 + s43 = cut 2 V-exact requests re-keyed (runId, arm).
set -uo pipefail
B=<workspace>; E=$B/boar-eval; OUT=$E/runs/kiln/tf2-on-cut2; C2=$E/runs/kiln/vexact-cut2
MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
mkdir -p $OUT; export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-ship
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
got=$(echo 'cd <runner>/kiln/be-0cfd4a77-tf2 && echo "$(cut -c1-16 PATCH_SHA256) $(shasum -a 256 be-ship/adapter.ts | cut -c1-16)"' | <on the mini> bash -s)
[ "$got" = "bd39546d3e1f8a2b 949eee0355032eb1" ] || { echo "TREE/RUNNER MISMATCH $got"; exit 1; }; echo "tree ok $got"
echo "free before: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
<on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && echo "detector up" || { echo "DETECTOR DOWN"; exit 1; }
DET=(BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json)
rekey() { # src dst runId
  python3 - "$1" "$2" "$3" <<'PY'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
for r in rows: r["runId"] = sys.argv[3]; r["config"]["arm"] = "tf2"
open(sys.argv[2], "w").write("".join(json.dumps(r) + "\n" for r in rows))
PY
}
run() { # label
  env "${DET[@]}" $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm tf2 --requests $OUT/$1.requests.jsonl --out $OUT/$1.traces.jsonl --places $PLACES > $OUT/$1.runsh.out 2>&1
  echo "$1 rc=$? $(date +%H:%M) $(tail -1 $OUT/$1.runsh.out | cut -c1-90)"
  <on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-tf2/be-ship/runs/$1"
}
# baselines (cut 2) for G2
scp -q MINI_HOST:boar/kiln/overnight/req/ov-cut2-v01-s44.requests.jsonl $OUT/cut2-v01-s44.requests.jsonl
scp -q MINI_HOST:boar/kiln/overnight/traces/ov-cut2-v01-s44.traces.jsonl $OUT/cut2-v01-s44.traces.jsonl
rekey $OUT/cut2-v01-s44.requests.jsonl $OUT/tf2-v01-s44.requests.jsonl tf2-v01-s44
for s in 42 43; do rekey $C2/vslice-and4b-s$s.requests.jsonl $OUT/tf2-vslice-and4b-s$s.requests.jsonl tf2-vslice-and4b-s$s; done
for s in 42 43; do run tf2-vslice-and4b-s$s; done
run tf2-v01-s44
echo 'p=$(lsof -tiTCP:8094 -sTCP:LISTEN); [ -n "$p" ] && kill $p; echo detector stopped' | <on the mini> bash -s
echo "free after: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
echo TF2-GEN-DONE
