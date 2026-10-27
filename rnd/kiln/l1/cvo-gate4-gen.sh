#!/usr/bin/env bash
# CVO gate #4 generation only (no scoring): 120 items, seed 44, Android 12 GB 4B, kit A, detector v3b, heavy lock. Both arms, 4 chunks of 30 interleaved
# (cut3, cvo, cut3, cvo, ...). Never opens the gate4 key. Detector: reuse running one, start only if absent, never stop.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; S=$B/rnd/research/coordinator/arms/cvo/gate4-set/items.jsonl
export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-ship
MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
[ "$(shasum -a 256 $S | cut -c1-8)" = 0e1781e9 ] || { echo SET-HASH-MISMATCH; exit 1; }
for x in "cut3 a67c70dbd194da82" "cvo 25415359e2916e22"; do set -- $x
  got=$(echo "cd <runner>/kiln/be-0cfd4a77-$1 && echo \"\$(cut -c1-16 PATCH_SHA256) \$(shasum -a 256 be-ship/adapter.ts | cut -c1-16)\"" | <on the mini> bash -s)
  [ "$got" = "$2 949eee0355032eb1" ] || { echo "TREE MISMATCH $1 $got"; exit 1; }; done; echo trees ok
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
DET=(BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json)
T=$E/runs/kiln/cvo-gate4-chunks; mkdir -p $T
python3 - $S $E/runs/kiln/cvo-l1/cvo-v01-s44.requests.jsonl $T <<'PY'
import json, sys
items = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
tmpl = json.loads(open(sys.argv[2]).readline())
for arm in ("cut3", "cvo"):
    for c in range(4):
        rows = []
        for it in items[c*30:(c+1)*30]:
            r = json.loads(json.dumps(tmpl)); r["runId"] = f"gate4-{arm}-s44-c{c}"; r["item"] = {"id": it["id"], "question": it["question"], "lang": "en"}; r["config"]["arm"] = arm
            rows.append(r)
        open(f"{sys.argv[3]}/{arm}-c{c}.requests.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in rows))
PY
for c in 0 1 2 3; do for arm in cut3 cvo; do
  env "${DET[@]}" $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm $arm --requests $T/$arm-c$c.requests.jsonl --out $T/$arm-c$c.traces.jsonl --places $PLACES > $T/$arm-c$c.out 2>&1
  echo "$arm c$c rc=$? $(date +%H:%M)"
  <on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-$arm/be-ship/runs/gate4-$arm-s44-c$c"
done; done
for arm in cut3 cvo; do mkdir -p $E/runs/kiln/cvo-gate4-$arm-s44; cat $T/$arm-c{0,1,2,3}.traces.jsonl > $E/runs/kiln/cvo-gate4-$arm-s44/traces.jsonl; done
python3 - $E/runs/kiln/cvo-gate4 <<'PY'
import json, statistics, sys
p = sys.argv[1]; L = {}
for a in ("cut3", "cvo"):
    rows = [json.loads(l) for l in open(f"{p}-{a}-s44/traces.jsonl") if l.strip()]
    L[a] = {r["itemId"]: r for r in rows}
    print(f"{a}: {len(rows)} trace lines, {len({r['itemId'] for r in rows})} unique, errors {sum(1 for r in rows if r.get('error'))}")
v = L["cvo"]
routed = [i for i in v if "cvo:routed" in v[i]["route"]["reasonCodes"]]
over = [i for i in v if any(c.startswith("cvo:override") for c in v[i]["route"]["reasonCodes"])]
chg = [i for i in v if v[i]["answer"]["text"] != L["cut3"][i]["answer"]["text"]]
print(f"routed {len(routed)}, overrides {len(over)}, answers differing from cut3 {len(chg)}")
d = [v[i]["timing"]["totalMs"] - L["cut3"][i]["timing"]["totalMs"] for i in routed]
if d: print(f"paired median added time on routed: {statistics.median(d)/1000:+.2f} s (n={len(d)})")
PY
echo GATE4-GEN-DONE
