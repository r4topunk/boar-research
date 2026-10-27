#!/usr/bin/env bash
# DETMAX G2/G3/G4 runs: control = be-0cfd4a77-cut5lite (cut 5), arm = be-0cfd4a77-detmax (patch 544b1b8f...), same committed adapter be-repo (7a0282ae...),
# BOAR_RUNNER_PROFILE=ship, detector v3b on :8094 (as CHATGATE), node backend, seed 44, heavy lock, same day, ctl then arm.
# Sets: v0.1 EN s44 (60 single-turn items, requests from cut4-l1) and the 192 dev chat messages (CHATGATE requests, multi-turn via item.history). No judge here.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; OUT=$E/runs/kiln/detmax; C=$E/runs/kiln/chatgate
MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
mkdir -p $OUT; export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-repo
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
chk() { echo "cd <runner>/kiln/be-0cfd4a77-$1 && echo \"\$(cut -c1-12 PATCH_SHA256) \$(shasum -a 256 be-repo/adapter.ts | cut -c1-16)\"" | <on the mini> bash -s; }
[ "$(chk cut5lite)" = "3b7a0dfa42bd 7a0282ae1f4229e6" ] || { echo "CTL TREE MISMATCH"; exit 1; }
[ "$(chk detmax)" = "824e0b35fcdf 7a0282ae1f4229e6" ] || { echo "ARM TREE MISMATCH"; exit 1; }
echo "free before: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
<on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && echo "detector up" || { echo "DETECTOR DOWN"; exit 1; }
runone() { # tag set tree srcrequests
  local tag=$1 set=$2 tree=$3 src=$4 l=$1-$2
  python3 - $src $OUT/$l.requests.jsonl $l $tree <<'PY'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
for r in rows: r["runId"] = sys.argv[3]; r["config"]["arm"] = sys.argv[4]
open(sys.argv[2], "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
PY
  BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json \
    $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm $tree --requests $OUT/$l.requests.jsonl --out $OUT/$l.traces.jsonl --places $PLACES > $OUT/$l.runsh.out 2>&1
  echo "$l rc=$? $(date +%H:%M) $(tail -1 $OUT/$l.runsh.out | cut -c1-100)"
  <on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-$tree/be-repo/runs/$l"
}
V=$E/runs/kiln/cut4-l1/cut4-v01-s44.requests.jsonl; H=$C/chatgate-s44.requests.jsonl
runone ctl v01-s44 cut5lite $V; runone arm v01-s44 detmax $V
runone ctl chat cut5lite $H;    runone arm chat detmax $H
echo 'p=$(lsof -tiTCP:8094 -sTCP:LISTEN); [ -n "$p" ] && kill $p; echo detector stopped' | <on the mini> bash -s
echo "free after: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
echo DETMAX-RUN-DONE
