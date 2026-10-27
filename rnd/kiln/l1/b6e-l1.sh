#!/usr/bin/env bash
# Anvil's b6e arm L1 (rnd/research/anvil/exp/emergency-gate/arm/README.md; L2-criterion.md fc5df39a… re-frozen, supersedes 31c0dde8). Tree
# be-0cfd4a77-b6e (b6e-engine.patch 3753e524…, retargeted before data; L2-criterion fc5df39a…), runner be-b6e = bb05e07b + runner-b4gate 8ca619bd + health11-runner e4882a95
# (949eee03…). BOAR_DETECTOR unset everywhere; control = same tree/runner with BOAR_ROUTE_GATE=0. 1 rep, s42.
set -uo pipefail
[ -f <workspace>/rnd/kiln/l1/b6e.PAUSED ] && { echo "B6E KILLED (coordinator 2026-10-03): not run"; echo B6E-L1-DONE; exit 0; }
B=<workspace>; E=$B/boar-eval; CS=$B/rnd/research/compass/chat-slice; OUT=$E/runs/kiln/b6e; A=$B/rnd/research/anvil/exp/emergency-gate/arm
export BOAR_EVAL_RUNNER_DIR=be-b6e HEAVY_CLASS=normal
unset BOAR_DETECTOR BOAR_DETECTOR_URL BOAR_DETECTOR_HEAD BOAR_DETECTOR_THR
got=$(echo 'cd <runner>/kiln/be-0cfd4a77-b6e && echo "$(cut -c1-16 PATCH_SHA256) $(shasum -a 256 be-b6e/adapter.ts | cut -c1-16)"' | <on the mini> bash -s)
[ "$got" = "3753e524d544b5b1 949eee0355032eb1" ] || { echo "TREE/RUNNER SHA MISMATCH: $got"; echo B6E-L1-DONE; exit 1; }
echo "tree+runner ok ($got)"
INST=(--installed qwen2.5-1.5b-instruct-q4km,qwen3-4b-instruct-2507-q4km)
mkdir -p $OUT; CFG=$OUT/ios8-b6e.config.json
python3 -c "import json; c=json.load(open('$E/runs/ios8/ios8-s42.config.json')); c['arm']='b6e'; c['seed']=42; json.dump(c, open('$CFG','w'))"
FIRST=$(python3 -c "import json; print(json.load(open('$B/rnd/research/compass/fast-loop/l1-slices.json'))['slices']['routing-chat']['ids'][0])")
emcheck() { python3 - "$1" <<'PY'
import json, sys
T = [json.loads(l) for l in open(sys.argv[1])]
em = sum(any(c.startswith("route-gate:em-") for c in t["route"]["reasonCodes"]) for t in T)
print(f"traces {len(T)}, with route-gate:em-* {em}"); sys.exit(0 if em else 1)
PY
}
# 0. sanity item 1
$B/rnd/kiln/l1/run_l1.sh routing-chat b6e-sanity $CFG --no-judge -- --ids $FIRST "${INST[@]}" > $OUT/sanity.out 2>&1
emcheck $E/runs/kiln/l1/b6e-sanity-routing-chat-s42/traces.jsonl || { echo "SANITY-FAIL: no route-gate:em-*"; echo B6E-L1-DONE; exit 1; }
echo "sanity ok $(date +%H:%M)"
# 1. routing-chat 24, judged
$B/rnd/kiln/l1/run_l1.sh routing-chat b6e $CFG -- "${INST[@]}" > $OUT/routing-chat.out 2>&1; echo "routing-chat rc=$? $(date +%H:%M)"
# 2. chat-slice v0 64 through the engine vs L0 decisions (l0-b6e.jsonl)
d=$OUT/chat-v0; mkdir -p $d; cp $CFG $d/config.json
pnpm -s -C $E/packages/protocol exec tsx src/makeRequests.ts --questions $CS/slice.v0.jsonl --config $d/config.json --run-id kiln-b6e-chat-v0 > $d/requests.jsonl
$E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm b6e --requests $d/requests.jsonl --out $d/traces.jsonl "${INST[@]}" > $d/runsh.out 2>&1; echo "chat-v0 rc=$? $(date +%H:%M)"
python3 $CS/score_l0.py --slice $CS/slice.v0.jsonl --traces $d/traces.jsonl --json $d/score_l0.json > $d/score_l0.txt 2>&1
# 3. Sonar core-142, re-keyed (runId + arm only; Sonar's Android 12 GB 4B config), arm vs control back to back
for side in arm ctl; do
  python3 - "$B/rnd/research/sonar/exp/30-learned-detector/l1/core-and-health11.requests.jsonl" "$OUT/core-$side.requests.jsonl" "kiln-b6e-core-$side" <<'PY'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
for r in rows: r["runId"] = sys.argv[3]; r["config"]["arm"] = "b6e"
open(sys.argv[2], "w").write("".join(json.dumps(r) + "\n" for r in rows))
PY
  [ $side = ctl ] && G=0 || G=
  BOAR_ROUTE_GATE=$G $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm b6e --requests $OUT/core-$side.requests.jsonl --out $OUT/core-$side.traces.jsonl > $OUT/core-$side.runsh.out 2>&1
  echo "core-$side rc=$? $(date +%H:%M)"
done
emcheck $OUT/core-arm.traces.jsonl || echo "WARN: core arm traces have no route-gate:em-* (profile has no gate?)"
python3 - $OUT/core-ctl.traces.jsonl <<'PY'
import json, sys
n = sum(any(c.startswith("route-gate:") for c in json.loads(l)["route"]["reasonCodes"]) for l in open(sys.argv[1]))
print(f"control route-gate codes: {n} (must be 0)")
PY
# 4. (README 1d1c00f2…, L1 item 4) Compass emergency-dev 31 items re-keyed from Sonar's cdev requests, arm vs control, 4B s42
CDEV_IDS="ed-en-008 ed-en-011 ed-en-065 ed-en-083 ed-en-094 ed-en-098 ed-en-100 ed-pt-008 ed-pt-011 ed-pt-065 ed-pt-083 ed-pt-094 ed-pt-098 ed-pt-100 ed-es-001 ed-es-002 ed-es-012 ed-es-028 ed-es-030 ed-es-057 ed-en-024 ed-en-048 ed-pt-009 ed-pt-036 ed-pt-049 ed-pt-060 ed-es-003 ed-es-026 ed-es-043 ed-es-053 ed-es-058"
for side in arm ctl; do
  python3 - "$B/rnd/research/sonar/exp/30-learned-detector/l1/cdev-and-health11.requests.jsonl" "$OUT/cdev-$side.requests.jsonl" "kiln-b6e-cdev-$side" "$CDEV_IDS" <<'PY2'
import json, sys
keep = sys.argv[4].split(); rows = [json.loads(l) for l in open(sys.argv[1])]; rows = [r for r in rows if r["item"]["id"] in keep]
assert len(rows) == 31, len(rows)
for r in rows: r["runId"] = sys.argv[3]; r["config"]["arm"] = "b6e"
open(sys.argv[2], "w").write("".join(json.dumps(r) + "\n" for r in rows))
PY2
  [ $side = ctl ] && G=0 || G=
  BOAR_ROUTE_GATE=$G $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm b6e --requests $OUT/cdev-$side.requests.jsonl --out $OUT/cdev-$side.traces.jsonl > $OUT/cdev-$side.runsh.out 2>&1
  echo "cdev-$side rc=$? $(date +%H:%M)"
done
python3 $B/rnd/kiln/l1/b6e-cdev-score.py > $OUT/cdev-score.out 2>&1; rc=$?
[ $rc = 2 ] && echo "B6E-L1-STOP (item 4 pre-registered stop; no L2)" || echo "cdev score rc=$rc"
<on the mini> "ls <runner>/kiln/be-0cfd4a77-b6e/be-b6e/runs"
echo B6E-L1-DONE
