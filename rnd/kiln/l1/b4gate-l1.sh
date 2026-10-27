#!/usr/bin/env bash
# Anvil's b4gate arm, L1 (README: rnd/research/anvil/exp/chat-routing/arm/README.md). ios8 4B profile, node backend, seed 42.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; CS=$B/rnd/research/compass/chat-slice; OUT=$E/runs/kiln/b4gate
export BOAR_EVAL_RUNNER_DIR=be-b4gate HEAVY_CLASS=normal
INST=(--installed qwen2.5-1.5b-instruct-q4km,qwen3-4b-instruct-2507-q4km)
until grep -q REPLYLANG-DONE <scratch> 2>/dev/null; do sleep 20; done
mkdir -p $OUT
CFG=$OUT/ios8-b4gate.config.json
python3 -c "import json; c=json.load(open('$E/runs/ios8/ios8-s42.config.json')); c['arm']='b4gate'; c['seed']=42; json.dump(c, open('$CFG','w'))"
FIRST=$(python3 -c "import json; print(json.load(open('$B/rnd/research/compass/fast-loop/l1-slices.json'))['slices']['routing-chat']['ids'][0])")
# 1. item-1 sanity
$B/rnd/kiln/l1/run_l1.sh routing-chat b4gate-sanity $CFG --no-judge -- --ids $FIRST "${INST[@]}" > $OUT/sanity.out 2>&1
python3 - "$E/runs/kiln/l1/b4gate-sanity-routing-chat-s42/traces.jsonl" <<'PY' || { echo SANITY-FAIL; echo B4GATE-L1-DONE; exit 1; }
import json, sys
t = json.loads(open(sys.argv[1]).readline())
ev = [e for e in t["events"] if e.get("kind") == "route-gate"]; codes = [c for c in t["route"]["reasonCodes"] if c.startswith("route-gate:")]
print("sanity", t["itemId"], "route-gate events", len(ev), "codes", codes, "versions.adapter", t["runtime"]["versions"]["adapter"])
sys.exit(0 if ev and codes and not any(c == "route-gate:unavailable" for c in codes) else 1)
PY
echo "sanity ok $(date +%H:%M)"
# 2. routing-chat slice, judged
$B/rnd/kiln/l1/run_l1.sh routing-chat b4gate $CFG -- "${INST[@]}" > $OUT/routing-chat.out 2>&1; echo "routing-chat rc=$? $(date +%H:%M)"
# 3. chat-slice v0 (64, multi-turn), full engine
d=$OUT/chat-v0; mkdir -p $d; cp $CFG $d/config.json
pnpm -s -C $E/packages/protocol exec tsx src/makeRequests.ts --questions $CS/slice.v0.jsonl --config $d/config.json --run-id kiln-b4gate-chat-v0 > $d/requests.jsonl
$E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm b4gate --requests $d/requests.jsonl --out $d/traces.jsonl "${INST[@]}" > $d/runsh.out 2>&1; echo "chat-v0 rc=$? $(date +%H:%M)"
python3 $CS/score_l0.py --slice $CS/slice.v0.jsonl --traces $d/traces.jsonl --json $d/score_l0.json > $d/score_l0.txt 2>&1
echo B4GATE-L1-DONE
