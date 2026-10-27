#!/usr/bin/env bash
# CUT5-SPEED G2/G3: control = cut 4 final tree (be-0cfd4a77-instsubj4, PATCH_SHA256 d51e844c...), arm = be-0cfd4a77-cut5lite (cfbaf707...);
# node backend (default, as cut4-l1.sh), same be-ship runner (f5c50806...). v0.1 EN s44+s45, order s44 ctl, s44 arm, s45 ctl, s45 arm; detector on; heavy lock.
# usage: cut5lite-l1.sh [extra]   extra = "rerun": control-vs-control reruns (ctl2) of s44+s45 afterwards.
set -uo pipefail
B=<workspace>; E=$B/boar-eval
PSHA=d51e844c6522cb18; RUNNER_SHA=f5c5080635558897; ASHA=3b7a0dfa42bddee2
OUT=$E/runs/kiln/cut5lite-l1; D4=$E/runs/kiln/cut4-l1
MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
mkdir -p $OUT; export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-ship
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
chk() { echo "cd <runner>/kiln/be-0cfd4a77-$1 && echo \"\$(cut -c1-16 PATCH_SHA256) \$(shasum -a 256 be-ship/adapter.ts | cut -c1-16)\"" | <on the mini> bash -s; }
[ "$(chk instsubj4)" = "$PSHA $RUNNER_SHA" ] || { echo "CTL TREE MISMATCH"; exit 1; }
[ "$(chk cut5lite)" = "$ASHA $RUNNER_SHA" ] || { echo "ARM TREE MISMATCH"; exit 1; }
echo "free before: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
<on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && echo "detector up" || { echo "DETECTOR DOWN"; exit 1; }
DET=(BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json)
runone() { # tag seed tree
  local tag=$1 s=$2 tree=$3 l=$1-v01-s$2
  python3 - $D4/cut4-v01-s$s.requests.jsonl $OUT/$l.requests.jsonl $l $tree <<'PY'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
for r in rows: r["runId"] = sys.argv[3]; r["config"]["arm"] = sys.argv[4]
open(sys.argv[2], "w").write("".join(json.dumps(r) + "\n" for r in rows))
PY
  env "${DET[@]}" $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm $tree --requests $OUT/$l.requests.jsonl --out $OUT/$l.traces.jsonl --places $PLACES > $OUT/$l.runsh.out 2>&1
  echo "$l rc=$? $(date +%H:%M) $(tail -1 $OUT/$l.runsh.out | cut -c1-100)"
  <on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-$tree/be-ship/runs/$l"
}
if [ "${1:-}" = rerun ]; then
  for s in 44 45; do runone ctl2 $s instsubj4; done
else
  for s in 44 45; do runone ctl $s instsubj4; runone arm $s cut5lite; done
fi
echo 'p=$(lsof -tiTCP:8094 -sTCP:LISTEN); [ -n "$p" ] && kill $p; echo detector stopped' | <on the mini> bash -s
echo "free after: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
echo CUT5SPEED-L1-GEN-DONE
