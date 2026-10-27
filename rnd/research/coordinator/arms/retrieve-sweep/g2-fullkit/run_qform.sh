#!/bin/bash
# G2-FULLKIT read 2 (0 LLM, MacBook): QFORM 432 on six separate A-union packs. usage: run_qform.sh <v3-extra|v2-off|v2-k1>
B=<workspace>; R=$B/rnd/research/coordinator/arms/retrieve-sweep
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
S=$B/shared-data; V3=$S/packs/v3proto
case $1 in
  v3-extra) PK=$V3/boar-factbook.sqlite,$V3/boar-firstaid-en.sqlite,$V3/boar-medlineplus-en.sqlite,$V3/boar-crypto.sqlite,$V3/boar-wikivoyage-en.sqlite,$V3/boar-visa-en.sqlite
            SET='{"packHeadPass":"a2","packDense2":"extra"}' ;;
  v2-off)   PK=$S/packs/wave2/boar-factbook.sqlite,$S/packs/wave1/boar-firstaid-en.sqlite,$S/packs/wave1/boar-medlineplus-en.sqlite,$S/crypto/boar-crypto.sqlite,$S/packs/boar-wikivoyage-en.sqlite,$S/packs/wave4/boar-visa-en.sqlite; SET="" ;;
  v2-k1)    PK=$S/packs/wave2/boar-factbook.sqlite,$S/packs/wave1/boar-firstaid-en.sqlite,$S/packs/wave1/boar-medlineplus-en.sqlite,$S/crypto/boar-crypto.sqlite,$S/packs/boar-wikivoyage-en.sqlite,$S/packs/wave4/boar-visa-en.sqlite
            SET='{"packHeadPass":"a2","packDense2":"append-budget"}' ;;
esac
cd $B
ARGS=(--questions $R/../qform/items/qform.questions.jsonl --tree $B/kiln-local/be-0cfd4a77-cut7-litepacks --packs $PK --gate search --cpu-embed --wide 12 --out $R/g2-fullkit/runs/qform.$1.jsonl)
[ -n "$SET" ] && ARGS+=(--forward-opts --settings-json "$SET")
$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx $R/tools/replay-sweep.ts "${ARGS[@]}" 2> $R/g2-fullkit/runs/qform.$1.err
tail -1 $R/g2-fullkit/runs/qform.$1.err
