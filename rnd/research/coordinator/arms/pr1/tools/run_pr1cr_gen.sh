#!/bin/bash
# PR1 CodeRabbit-fixes identity run (de3d97ac); copy of run_pr1_gen.sh. PR1 generation identity run (MacBook): tree kiln-local/be-de3d97ac-pr1cr (git archive of pr/cut7-engine 8882b175 + the
# cut7-stack adapter 8dd1faff), same env as arms/stack/tools/run_stack.sh (ship profile, mmbert detector :8094, server
# backend, llama-b11010-cpu, -t 4). Requests = v01-cut7-stack-off-s42 with runId/commit/arm rewritten (mkreq inline in PR1-REBASE.md).
# Waits (poll 60 s, max 60 min) until no llama-server other than the detector (:8094) and no adapter.ts job is running.
set -u
E=<workspace>/rnd/research/coordinator/arms/pr1; T=<workspace>/kiln-local/be-de3d97ac-pr1cr
REQ=$E/runs/v01-pr1cr-s42.requests.jsonl; OUT=$E/runs/v01-pr1cr-s42.traces.jsonl; S=${OUT%.jsonl}.status
MD=<workspace>/shared-models/emergency-detector; SRV=<workspace>/spikes/llama-b11010-cpu/bin/llama-server
busy() { pgrep -fl llama-server | grep -v -- "--port 8094" | grep -q . || pgrep -f "be/adapter.ts" >/dev/null; }
echo "wait-start $(date '+%F %T')" > "$S"; w=0
while busy; do w=$((w+1)); [ $w -gt 60 ] && { echo "FAIL busy after 60 min" >> "$S"; exit 2; }; sleep 60; done
echo "start $(date +%s) $(date '+%F %T') waited ${w} min" >> "$S"
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
[ "$(shasum -a 256 be/adapter.ts | cut -c1-16)" = 8dd1faff2b157d00 ] || { echo "FAIL adapter sha" >> "$S"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
EXTRA=(--backend server --server-bin "$SRV" --threads 4 --timeout-ms 600000)
echo "cmd adapter.ts --requests $REQ --out $OUT ${EXTRA[*]}" >> "$S"
be/node_modules/tsx/dist/cli.mjs be/adapter.ts --requests "$REQ" --out "$OUT" "${EXTRA[@]}" > "${OUT%.jsonl}.log" 2>&1; rc=$?
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
