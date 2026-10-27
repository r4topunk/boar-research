#!/bin/bash
# RETRIEVE-SWEEP replay driver (0 LLM). Usage: replay.sh <tree> <questions.jsonl> <out.jsonl> <set: qform|main> [extra replay args...]
# Env switches (RS_*) are inherited from the caller. qform = merged A-union pack, stock settings unless --settings-json given;
# main = K1 kit (crypto, wikivoyage, simplewiki v3proto), K1 settings, 1.7B catalog entry, gate/detector from the funnel's K1 traces.
set -u
T=$1; Q=$2; O=$3; SET=$4; shift 4
B=<workspace>
export BOAR_REPLAY_CACHE=$B/kiln-local/rs-H2-cache  # private APFS clone of boar-eval/runs/replay-cache: concurrent arms share the sqlite and hit "database is locked"
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx
TOOL=$B/rnd/research/coordinator/arms/retrieve-sweep/tools/replay-sweep-text.ts
if [ "$SET" = qform ]; then
  $TSX $TOOL --questions $Q --tree $T --packs $B/shared-data/packs/persona-a-union-merged/boar-aunion-merged.sqlite \
    --gate search --cpu-embed --wide 12 --out $O "$@"
else
  $TSX $TOOL --questions $Q --tree $T \
    --packs $B/shared-data/crypto/boar-crypto.sqlite,$B/shared-data/packs/boar-wikivoyage-en.sqlite,$B/shared-data/packs/v3proto/boar-simplewiki-en.sqlite \
    --tasks-from $B/rnd/research/coordinator/arms/retrieve-sweep/replay/funnel-K1.traces.jsonl \
    --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 --forward-opts \
    --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $O "$@"
fi
