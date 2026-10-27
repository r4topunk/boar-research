#!/usr/bin/env bash
# usage: run-local.sh <label> <ids> [locations.json]   (MacBook, cut 7 tree copy, config (b), ship profile, no detector)
set -uo pipefail
L=$1; IDS=$2; LOC=${3:-}
cd <scratch>
export BOAR_RUNNER_PROFILE=ship BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs:<workspace>/shared-data/crypto
[ -n "$LOC" ] && export BOAR_ITEM_LOCATIONS=$LOC
REQ=<private held-out dir> $L | sed 's/-s42.*//; s/-s43.*//')
t0=$(date +%s)
${BE:-be-repo}/node_modules/.bin/tsx ${BE:-be-repo}/adapter.ts --requests <private held-out dir> --out <private held-out dir> --ids $IDS --threads 4   --places $PLACES > <private held-out dir> 2>&1
rc=$?; echo "$L rc=$rc wall=$(( $(date +%s) - t0 ))s n=$(wc -l < <private held-out dir>)"
