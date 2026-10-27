#!/bin/bash
# H4-MERGE replay driver (0 LLM, MacBook). usage: run.sh <set> <label>   (RS_MERGE comes from the caller's env; unset = control)
#   set: qm   QFORM 432, merged A-union pack, stock settings          -> replays/qm.<label>.jsonl
#        q6   QFORM 432, six separate A-union v2 packs, stock settings -> replays/q6.<label>.jsonl
#        <kit> K3 | K3CM | K3W : MAIN 97, coverage-map install kit, K3 settings -> replays/main.<kit>.<label>.jsonl
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; H=$R/retrieve-sweep/h4-merge
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$R/retrieve-sweep/tools/replay-sweep.ts
TREE=${TREE:-$B/kiln-local/rs-H4}; S=$B/shared-data; QQ=$R/qform/items/qform.questions.jsonl
SET=$1; LAB=$2; t0=$(date +%s); cd $B
case $SET in
  qm) OUT=$H/replays/qm.$LAB.jsonl
      $TSX $TOOL --questions $QQ --tree $TREE --packs $S/packs/persona-a-union-merged/boar-aunion-merged.sqlite --gate search --cpu-embed --wide 12 --out $OUT 2> $OUT.err ;;
  q6) OUT=$H/replays/q6.$LAB.jsonl
      PK=$S/packs/wave2/boar-factbook.sqlite,$S/packs/wave1/boar-firstaid-en.sqlite,$S/packs/wave1/boar-medlineplus-en.sqlite,$S/crypto/boar-crypto.sqlite,$S/packs/boar-wikivoyage-en.sqlite,$S/packs/wave4/boar-visa-en.sqlite
      $TSX $TOOL --questions $QQ --tree $TREE --packs $PK --gate search --cpu-embed --wide 12 --out $OUT 2> $OUT.err ;;
  K3|K3CM|K3W) OUT=$H/replays/main.$SET.$LAB.jsonl
      $TSX $TOOL --questions $R/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl --tree $TREE --packs $(cat $R/coverage-map/replay/kit.$SET.txt) \
        --tasks-from $R/coverage-map/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
        --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $OUT 2> $OUT.err ;;
  proof) OUT=$H/replays/proof20.$LAB.jsonl
      $TSX $TOOL --questions $R/retrieve-sweep/replay/proof20.questions.jsonl --tree $TREE --packs $S/packs/persona-a-union-merged/boar-aunion-merged.sqlite --gate search --cpu-embed --wide 12 --out $OUT 2> $OUT.err ;;
  proof6) OUT=$H/replays/proof6.$LAB.jsonl
      PK=$S/packs/wave2/boar-factbook.sqlite,$S/packs/wave1/boar-firstaid-en.sqlite,$S/packs/wave1/boar-medlineplus-en.sqlite,$S/crypto/boar-crypto.sqlite,$S/packs/boar-wikivoyage-en.sqlite,$S/packs/wave4/boar-visa-en.sqlite
      $TSX $TOOL --questions $R/retrieve-sweep/replay/proof20.questions.jsonl --tree $TREE --packs $PK --gate search --cpu-embed --wide 12 --out $OUT 2> $OUT.err ;;
esac
echo "$SET $LAB rc=$? $(( $(date +%s) - t0 ))s RS_MERGE=${RS_MERGE:-unset} $(tail -1 $OUT.err | cut -c1-200)"
