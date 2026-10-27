#!/bin/bash
# G2-FULLKIT read 1 (0 LLM, MacBook): MAIN 97, K1 tree, settings {"packHeadPass":"a2","packDense2":"extra"}.
# usage: run_main.sh <v2|v3> ; v3 = crypto, wikivoyage, simplewiki from v3proto; v2 = crypto, wikivoyage (shared-data), simplewiki wave2 (v2 files, no chunk_vecs).
# Adapted from g-chunkvecs/step0/run.sh; tool = tools/replay-sweep.ts (= replay-qform + wallMs).
B=<workspace>; R=$B/rnd/research/coordinator/arms/retrieve-sweep
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
if [ "$1" = v3 ]; then P=$B/shared-data/packs/v3proto; PK=$P/boar-crypto.sqlite,$P/boar-wikivoyage-en.sqlite,$P/boar-simplewiki-en.sqlite
else PK=$B/shared-data/crypto/boar-crypto.sqlite,$B/shared-data/packs/boar-wikivoyage-en.sqlite,$B/shared-data/packs/wave2/boar-simplewiki-en.sqlite; fi
cd $B
$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx $R/tools/replay-sweep.ts \
  --questions $R/../decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl --tree $B/kiln-local/be-0cfd4a77-cut7-litepacks \
  --packs $PK --tasks-from $R/replay/funnel-K1.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
  --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"extra"}' --out $R/g2-fullkit/runs/main.$1.jsonl 2> $R/g2-fullkit/runs/main.$1.err
tail -1 $R/g2-fullkit/runs/main.$1.err
