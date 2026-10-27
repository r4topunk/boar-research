#!/usr/bin/env bash
# RUNNERS verification: 9 rows (France warm-up + first 8 v0.1 EN items), cut 5 tree (be-0cfd4a77-cut5lite), runner be-ship (mini-only, f5c50806)
# vs committed adapter deployed as be-repo with BOAR_RUNNER_PROFILE=ship. Node backend, detector on, heavy lock. Text must be identical 9/9.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; L=$E/runs/kiln/cut5lite-l1; OUT=$E/runs/kiln/runner-verify
MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
mkdir -p $OUT; export HEAVY_CLASS=normal
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
python3 - $L/arm-v01-s44.requests.jsonl $OUT <<'PY'
import json, sys, copy
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
w = copy.deepcopy(rows[0]); w["item"] = {"id": "warm-france", "question": "What is the capital of France?", "lang": "en"}
sel = [w] + rows[:8]
for tag in ("beship", "repo"):
    out = []
    for r in sel:
        r = copy.deepcopy(r); r["runId"] = "rv-" + tag; out.append(r)
    open(f"{sys.argv[2]}/rv-{tag}.requests.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in out))
PY
DET=(BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json)
for v in "beship be-ship" "repo be-repo"; do set -- $v
  extra=(); [ $1 = repo ] && extra=(BOAR_RUNNER_PROFILE=ship)
  env "${DET[@]}" ${extra[@]+"${extra[@]}"} BOAR_EVAL_RUNNER_DIR=$2 $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm cut5lite --requests $OUT/rv-$1.requests.jsonl --out $OUT/rv-$1.traces.jsonl --places $PLACES > $OUT/rv-$1.runsh.out 2>&1
  echo "rv-$1 rc=$? $(tail -1 $OUT/rv-$1.runsh.out | cut -c1-90)"
  <on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-cut5lite/$2/runs/rv-$1"
done
echo 'p=$(lsof -tiTCP:8094 -sTCP:LISTEN); [ -n "$p" ] && kill $p; echo detector stopped' | <on the mini> bash -s
python3 - $OUT <<'PY'
import json, sys
ld = lambda p: [json.loads(l) for l in open(p)]
a, b = ld(sys.argv[1] + "/rv-beship.traces.jsonl"), ld(sys.argv[1] + "/rv-repo.traces.jsonl")
g = lambda t: sum(1 for e in t["events"] if e.get("kind") == "route-gate")
same = sum(x["itemId"] == y["itemId"] and x["answer"]["text"] == y["answer"]["text"] and x["route"] == y["route"] for x, y in zip(a, b))
print(f"text+route identical {same}/{len(a)}; gate events beship {sum(map(g, a))} repo {sum(map(g, b))}; tiers {[t['route']['tier'] for t in a]}")
PY
echo RV-DONE
