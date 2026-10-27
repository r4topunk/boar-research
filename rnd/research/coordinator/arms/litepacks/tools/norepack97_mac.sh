#!/bin/bash
# NOREPACK97 MacBook arm. Usage: norepack_mac.sh <arm name> <extra args beyond --reasoning off, may be empty>
# Same as tools/run_lp.sh (tree be-0cfd4a77-cut7-litepacks, LITEDECLINE_OFF=5, -t 4, seed 42 in requests) but BOAR_SERVER_EXTRA_ARGS is the pass-through:
# "--reasoning off [--no-repack]". 10 requests from norepack97/req/nr97.requests.jsonl. Output norepack97/traces/<arm>.jsonl (+ .server.log).
set -u
N=$1; X=${2:-}
H=<workspace>/rnd/research/coordinator/arms/litepacks; T=<workspace>/kiln-local/be-0cfd4a77-cut7-litepacks
SRV=<workspace>/spikes/llama-b11010-cpu/bin/llama-server; MD=<workspace>/shared-models/emergency-detector
cd $T || exit 1
# NOTE: the MacBook binary carries a stale absolute rpath (old scratchpad .../scratchpad/home/boar/llama-b11010/build-cpu/bin); a symlink at that path -> spikes/llama-b11010-cpu/bin was recreated (outside the repo). DYLD_* is stripped by SIP shells, so it does not work.
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/v3proto:<workspace>/shared-data/packs/wave3:<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto
export BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
export BOAR_SERVER_EXTRA_ARGS="--reasoning off $X" LITEDECLINE_OFF=5
curl -sf http://127.0.0.1:8094/health > /dev/null || { echo "FAIL detector down"; exit 1; }
while $H/../headpass-st/tools/busy.sh >/dev/null 2>&1; do sleep 20; done
OUT=$H/norepack97/traces/$N.jsonl; rm -f $OUT
be/node_modules/tsx/dist/cli.mjs be/adapter-litedecline.ts --requests $H/norepack97/req/nr97.requests.jsonl --out $OUT --backend server --server-bin $SRV --threads 4 --timeout-ms 600000 > $H/norepack97/traces/$N.log 2>&1
echo "$N rc=$? rows=$(wc -l < $OUT)"
