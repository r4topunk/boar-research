#!/bin/bash
# HEALTHGAP 0-LLM route replay runner (rule v1.1 §5c): tree kiln-local/be-0cfd4a77-cut7-healthgap (ARM cut7+healthgap = cut 7 +
# tools/healthgap.patch), be/replay-stub.ts (mk_replay_stub.py; no model). HEALTHGAP=1 (ON) or unset (OFF) from the caller.
# Guards: busy.sh (no other llama-server / adapter job), detector :8094 up, patched files pinned, disk >= 3 GiB (no model loaded).
# Usage: run_hg_replay.sh <requests.jsonl> <out traces.jsonl>
set -u
T=<workspace>/kiln-local/be-0cfd4a77-cut7-healthgap; REQ=$1; OUT=$2; S=${OUT%.jsonl}.status; MD=<workspace>/shared-models/emergency-detector
BUSY=<workspace>/rnd/research/coordinator/arms/headpass-st/tools/busy.sh; H=<workspace>/rnd/research/coordinator/arms/healthgap
echo "start $(date +%s) $(date '+%F %T') env HEALTHGAP=${HEALTHGAP:-}" > "$S"
w=0; while "$BUSY" > /dev/null 2>&1; do [ $w -ge ${WAIT_MAX:-60} ] && { echo "FAIL busy" >> "$S"; exit 1; }; [ $w = 0 ] && echo "wait-busy $(date '+%T')" >> "$S"; w=$((w+1)); sleep 60; done
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
[ "$(cat ARM)" = cut7+healthgap ] || { echo "FAIL ARM" >> "$S"; exit 1; }
[ "$(shasum -a 256 src/routing/healthGap.ts | cut -c1-16)" = "$(cut -c1-16 $H/tools/pins.healthGap.ts)" ] && [ "$(shasum -a 256 src/routing/answer.ts | cut -c1-16)" = "$(cut -c1-16 $H/tools/pins.answer.ts)" ] || { echo "FAIL patched-file pins" >> "$S"; exit 1; }
grep -q 'process.env.HEALTHGAP' src/routing/*.ts && { echo "FAIL engine reads env" >> "$S"; exit 1; }
case "${HEALTHGAP:-}" in 1|"") ;; *) echo "FAIL HEALTHGAP=${HEALTHGAP}" >> "$S"; exit 1 ;; esac
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
FREE=$(df -k <home> | tail -1 | awk '{print int($4/1048576)}'); [ "$FREE" -ge 3 ] || { echo "FAIL disk ${FREE} GiB < 3" >> "$S"; exit 1; }
python3 -I $H/tools/mk_replay_stub.py "$T" >> "$S" || exit 1
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
be/node_modules/tsx/dist/cli.mjs be/replay-stub.ts --requests "$REQ" --out "$OUT" > "${OUT%.jsonl}.log" 2>&1; rc=$?
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
