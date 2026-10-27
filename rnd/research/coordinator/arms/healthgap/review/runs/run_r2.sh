#!/bin/bash
# r2 reviewer replay (0 LLM; stub engine): scratch tree, detector :8094, busy guard. Usage: run_r2.sh <tree> <req> <out>
set -u; T=$1; REQ=$2; OUT=$3; MD=<workspace>/shared-models/emergency-detector
BUSY=<workspace>/rnd/research/coordinator/arms/headpass-st/tools/busy.sh
"$BUSY" >/dev/null 2>&1 && { echo BUSY; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo DET-DOWN; exit 1; }
cd "$T" || exit 1
grep -q 'process.env.HEALTHGAP' src/routing/*.ts && { echo ENV; exit 1; }
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
be/node_modules/tsx/dist/cli.mjs be/replay-stub.ts --requests "$REQ" --out "$OUT" > "${OUT%.jsonl}.log" 2>&1; echo rc=$?
