#!/usr/bin/env bash
# G4ENG L1 (criterion arms/g4eng/G4ENG-criterion.md 5aecdd03…). Same session: control = cut 3 (tree be-0cfd4a77-cut3, Qwen3-4B) and arm = same engine bytes
# copied to tree be-0cfd4a77-g4eng (ARM=g4eng, patch a67c70db…) with requests config modelId = gemma-4-e4b-it-q4_0 (the Oct-1 QUEUE #2 config-only path). Generation only.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; OUT=$E/runs/kiln/g4eng-l1; D3=$E/runs/kiln/cut3-confirm; mkdir -p $OUT; export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-ship
MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
for t in cut3 g4eng; do
  got=$(echo "cd <runner>/kiln/be-0cfd4a77-$t && echo \"\$(cut -c1-16 PATCH_SHA256) \$(shasum -a 256 be-ship/adapter.ts | cut -c1-16)\"" | <on the mini> bash -s)
  [ "$got" = "a67c70dbd194da82 949eee0355032eb1" ] || { echo "TREE/RUNNER MISMATCH $t $got"; exit 1; }; echo "tree $t ok"
done
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
<on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && echo "detector up" || { echo "DETECTOR DOWN"; exit 1; }
DET=(BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json)
# interleave seeds so both arms see the same session conditions: ctl s44, g4 s44, ctl s45, g4 s45
for s in 44 45; do for arm in ctl g4eng; do
  l=$arm-v01-s$s
  python3 - $D3/cut3-v01-s$s.requests.jsonl $OUT/$l.requests.jsonl $l $arm <<'PY'
import json, sys
rows = [json.loads(x) for x in open(sys.argv[1]) if x.strip()]
for r in rows:
    r["runId"] = sys.argv[3]
    if sys.argv[4] == "g4eng": r["config"]["arm"] = "g4eng"; r["config"]["modelId"] = "gemma-4-e4b-it-q4_0"
open(sys.argv[2], "w").write("".join(json.dumps(r) + "\n" for r in rows))
PY
  a=cut3; [ $arm = g4eng ] && a=g4eng
  env "${DET[@]}" $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm $a --requests $OUT/$l.requests.jsonl --out $OUT/$l.traces.jsonl --places $PLACES > $OUT/$l.runsh.out 2>&1
  echo "$l rc=$? $(date +%H:%M) $(tail -1 $OUT/$l.runsh.out | cut -c1-90)"
  <on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-$a/be-ship/runs/$l"
done; done
echo 'p=$(lsof -tiTCP:8094 -sTCP:LISTEN); [ -n "$p" ] && kill $p; echo detector stopped' | <on the mini> bash -s
echo G4ENG-GEN-DONE
