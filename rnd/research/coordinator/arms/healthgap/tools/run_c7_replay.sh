#!/bin/bash
# Off-switch check: the same 0-LLM stub replay on a scratch copy of the plain cut 7 tree (ARM cut7, no HEALTHGAP).
# Usage: run_c7_replay.sh <requests(arm cut7).jsonl> <out traces.jsonl>
set -u
T=<scratch>; REQ=$1; OUT=$2; MD=<workspace>/shared-models/emergency-detector
<workspace>/rnd/research/coordinator/arms/headpass-st/tools/busy.sh >/dev/null && { echo busy; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "detector down"; exit 1; }
diff -rq $T/src <workspace>/kiln-local/be-0cfd4a77-cut7/src || { echo "not cut 7"; exit 1; }
cd $T && python3 -I <workspace>/rnd/research/coordinator/arms/healthgap/tools/mk_replay_stub.py $T >/dev/null || exit 1
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
env -u HEALTHGAP be/node_modules/tsx/dist/cli.mjs be/replay-stub.ts --requests "$REQ" --out "$OUT" > "${OUT%.jsonl}.log" 2>&1
