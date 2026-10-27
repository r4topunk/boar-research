#!/bin/bash
# FA-CARDS step A/B replay (MacBook, 0 generation): be/replay-stub-litesafety.ts on a be-cut7-warn tree, env as LITESAFETY run_ls.sh REPLAY=1.
# Usage: replay.sh <tree> <tag>   (tree = kiln-local/be-cut7-warn for A, the local copy with the trigger edit for B)
set -u
T=$1; TAG=$2; A=<workspace>/rnd/research/coordinator/arms/fa-cards; B=<workspace>; MD=$B/shared-models/emergency-detector
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down"; exit 1; }
cd $T || exit 1
[ "$(cat ARM)" = pr1+warn ] && [ "$(cat COMMIT)" = 8ac9eb7a0f79d9983a5712079379f595f3e4ad73 ] || { echo FAIL ARM; exit 1; }
[ "$(shasum -a 256 be/replay-stub-litesafety.ts | cut -c1-16)" = 496fc3402e18f446 ] || { echo FAIL adapter; exit 1; }
echo "tree $T answer.ts=$(shasum -a 256 src/routing/answer.ts | cut -c1-16) conditionCards.ts=$(shasum -a 256 src/routing/conditionCards.ts | cut -c1-16)"
export NUMGUARD=1 HEALTHGAP=1 WARN=1 BOAR_SERVER_EXTRA_ARGS="--reasoning off"
export BOAR_EVAL_PACK_DIRS=$B/shared-data/packs/v3proto:$B/shared-data/packs/wave3:$B/shared-data/packs/wave2:$B/shared-data/packs/wave1:$B/shared-data/packs:$B/shared-data/crypto
export BOAR_SHARED_MODELS=$B/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 \
  BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
mkdir -p $A/runs/$TAG
for S in v01 cm probes65 ls80; do
  O=$A/runs/$TAG/fa-$S.traces.jsonl; t0=$(date +%s)
  be/node_modules/tsx/dist/cli.mjs be/replay-stub-litesafety.ts --requests $A/runs/req/fa-$S.requests.jsonl --out $O > $A/runs/$TAG/fa-$S.log 2>&1
  echo "$TAG $S rc=$? rows=$(wc -l < $O | tr -d ' ') errors=$(grep -c '"error":{' $O) $(( $(date +%s) - t0 ))s"
done
